import sys
import os
import tempfile
import subprocess

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from integrations.audio.asr_api import transcribe_bytes_assemblyai, submit_transcription_bytes
from integrations.audio.vosk_spotter import detect_keywords_in_wav_bytes, load_vosk_model
from integrations.audio import transcription_manager as transcription_manager
import time
import threading
import io

# Full FFmpeg Path
FFMPEG = r"C:\Program Files\Softdeluxe\Free Download Manager\ffmpeg.exe"

_last_cloud_submit = 0.0
_min_interval = float(os.getenv("WAKE_WORD_MIN_INTERVAL", "1.0"))


def detect_wake_word(webm_path):
    """Detect wake words 'Studio' or 'Hey Studio' in audio.

    Returns a tuple: (detected, job_id)
    - detected: True|False|None (None = async job queued)
    - job_id: string if an async transcription job was created, else None
    """
    
    # Check if file exists and has content
    if not os.path.exists(webm_path) or os.path.getsize(webm_path) < 100:
        print("[WAKE WORD] Audio file too small or missing")
        return False
    
    # Convert WebM to WAV in-memory using ffmpeg stdin/stdout
    # ffmpeg -i pipe:0 -ar 16000 -ac 1 -c:a pcm_s16le -f wav pipe:1
    with open(webm_path, "rb") as f:
        webm_bytes = f.read()

    ffmpeg_cmd = [
        FFMPEG,
        "-i", "pipe:0",
        "-ar", "16000",
        "-ac", "1",
        "-c:a", "pcm_s16le",
        "-f", "wav",
        "pipe:1",
        "-y"
    ]

    try:
        p = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        wav_bytes, stderr = p.communicate(input=webm_bytes, timeout=10)
    except subprocess.TimeoutExpired:
        p.kill()
        print("[WAKE WORD] FFmpeg conversion timed out")
        return False

    if p.returncode != 0 or not wav_bytes:
        try:
            err_text = stderr.decode()
        except:
            err_text = ""
        print(f"[WAKE WORD] FFmpeg error: {err_text}")
        return False

    if len(wav_bytes) < 200:
        print("[WAKE WORD] WAV bytes too small")
        return False

    try:
        # First, try local Vosk detector if model available and enabled
        vosk_enabled = os.getenv("VOSK_ENABLE", "1") != "0"
        model_available = load_vosk_model() is not None
            if vosk_enabled and model_available:
            try:
                vk = detect_keywords_in_wav_bytes(wav_bytes, keywords=("studio",))
                if vk is True:
                    print("[WAKE WORD] Vosk detected wake-word 'studio'")
                    return True
                elif vk is False:
                    print("[WAKE WORD] Vosk processed audio; no keyword detected")
                    # continue to cloud ASR fallback
                else:
                    # vk is None meaning model couldn't process; fallthrough
                    pass
            except Exception as e:
                print(f"[WAKE WORD] Vosk check error: {e}")

        # Transcribe audio bytes; allow configurable async behavior
        async_mode = os.getenv("WAKE_WORD_ASYNC", "0") == "1"

        def do_transcribe_and_check(wav_b):
            transcript = transcribe_bytes_assemblyai(wav_b)
            if not transcript:
                print("[WAKE WORD] No transcript received")
                return False
            transcript_lower = transcript.lower().strip()
            wake_words = ["studio", "hey studio", "hello studio", "hi studio", "ok studio"]
            print(f"[WAKE WORD] Checking transcript: '{transcript}'")
            for wake_word in wake_words:
                if wake_word in transcript_lower:
                    print(f"[WAKE WORD] DETECTED: '{wake_word}' in '{transcript}'")
                    return True
            if transcript_lower == "studio" or transcript_lower.endswith(" studio"):
                print(f"[WAKE WORD] PARTIAL MATCH: '{transcript}'")
                return True
            print(f"[WAKE WORD] NOT DETECTED in: '{transcript}'")
            return False

        if async_mode:
            # Throttle cloud submissions to avoid flooding AssemblyAI
            now = time.time()
            global _last_cloud_submit
            if now - _last_cloud_submit < _min_interval:
                print(f"[WAKE WORD] Cloud submission throttled (last submit {now - _last_cloud_submit:.2f}s ago)")
                return (False, None)

            # Register job via transcription_manager which will always return a job id
            try:
                job_id = transcription_manager.submit_job(wav_bytes, timeout=None, interval=None)
                _last_cloud_submit = now
                print("[WAKE WORD] Transcription submitted (job_id=", job_id, ")")
                return (None, job_id)
            except Exception as e:
                print(f"[WAKE WORD] Failed to submit transcription job: {e}")
                # Fallback to spawning a background thread (not tracked)
                t = threading.Thread(target=do_transcribe_and_check, args=(wav_bytes,), daemon=True)
                t.start()
                print("[WAKE WORD] Transcription queued (background thread)")
                return (None, None)
        else:
            # Synchronous: try to submit but block if needed to respect concurrency
            fut = submit_transcription_bytes(wav_bytes, timeout=None, interval=None, block=True)
            if fut is None:
                # Shouldn't happen when block=True, but fallback to direct call
                result = do_transcribe_and_check(wav_bytes)
                return (result, None)
            else:
                # Wait for result
                result = fut.result()
                # result is transcript string
                if not result:
                    print("[WAKE WORD] No transcript received")
                    return (False, None)
                # reuse same check logic
                transcript_lower = result.lower().strip()
                wake_words = ["studio", "hey studio", "hello studio", "hi studio", "ok studio"]
                for wake_word in wake_words:
                    if wake_word in transcript_lower:
                        print(f"[WAKE WORD] DETECTED: '{wake_word}' in '{result}'")
                        return (True, None)
                if transcript_lower == "studio" or transcript_lower.endswith(" studio"):
                    print(f"[WAKE WORD] PARTIAL MATCH: '{result}'")
                    return (True, None)
                print(f"[WAKE WORD] NOT DETECTED in: '{result}'")
                return (False, None)
    except Exception as e:
        print(f"[WAKE WORD ERROR]: {e}")
        return (False, None)
    finally:
        # Cleanup original webm file (wav was in-memory)
        try:
            if os.path.exists(webm_path):
                os.remove(webm_path)
        except:
            pass