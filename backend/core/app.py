# backend/app.py

import sys
import os
import tempfile
import subprocess
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Load environment variables from backend/config/.env so all modules see them
backend_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(backend_root, "config", ".env")
load_dotenv(dotenv_path)
print("[INFO] Loaded ASSEMBLYAI KEY:", os.getenv("ASSEMBLYAI_API_KEY"))
print("[INFO] Loaded MURF KEY:", os.getenv("MURF_API_KEY"))

# Import your modules after loading env so they can read keys from environment
from integrations.audio.asr_api import transcribe_file_assemblyai
from assistants.simple_assistant import generate_reply
from integrations.audio.murf_api import synthesize_text_murf
from integrations.audio.wake_word_detection import detect_wake_word
from integrations.audio.transcription_manager import get_job as get_transcription_job

app = Flask(__name__)
CORS(app)

# ⭐ Full FFmpeg Path (your system)
FFMPEG = r"C:\Program Files\Softdeluxe\Free Download Manager\ffmpeg.exe"


@app.route("/asr", methods=["POST"])
def asr_handler():
    """
    Steps:
    1. Receive WebM audio
    2. Convert WebM → WAV using FFmpeg
    3. Send WAV to AssemblyAI
    4. Generate AI reply
    5. Convert reply to speech using Murf Falcon
    """
    if "audio" not in request.files:
        return jsonify({"ok": False, "error": "No audio file received"}), 400

    audio_file = request.files["audio"]

    # ---- SAVE WEBM INPUT ----
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
        webm_path = tmp.name
        audio_file.save(webm_path)

    print(f"[INFO] Saved WebM: {webm_path} ({os.path.getsize(webm_path)} bytes)")

    # ---- CONVERT WEBM → WAV ----
    wav_path = webm_path.replace(".webm", ".wav")

    cmd = [
        FFMPEG,          # full ffmpeg path
        "-i", webm_path,
        "-ar", "16000",  # sample rate
        "-ac", "1",      # mono
        "-c:a", "pcm_s16le",
        "-f", "wav",     # force wav format
        "-threads", "2", # use 2 threads for faster processing
        wav_path,
        "-y"
    ]

    print("[INFO] Running FFmpeg:", cmd)

    # Run FFmpeg safely
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    exit_status = result.returncode

    # Validate WAV output
    if (
        exit_status != 0
        or not os.path.exists(wav_path)
        or os.path.getsize(wav_path) < 500      # WAV too small → no speech
    ):
        print("[ERROR] FFmpeg Error Output:")
        print(result.stderr.decode())

        return jsonify({
            "ok": False,
            "error": "FFmpeg failed or audio too short. Try speaking louder/longer."
        }), 500

    print(f"[INFO] WAV Created: {wav_path} ({os.path.getsize(wav_path)} bytes)")

    # -------- PROCESS SPEECH --------
    try:
        # TRANSCRIPTION
        transcript = transcribe_file_assemblyai(wav_path)
        print("[INFO] Transcript:", transcript)

        if not transcript:
            return jsonify({
                "ok": False,
                "error": "No speech detected. Please try again."
            }), 500

        # AI REPLY
        reply_result = generate_reply(transcript)
        
        # Handle special responses (navigation, search, music)
        if isinstance(reply_result, dict) and reply_result.get("type") in ["navigation", "search", "music"]:
            reply_text = reply_result["message"]
            print(f"[INFO] {reply_result['type'].title()} Reply:", reply_text)
        else:
            reply_text = str(reply_result)
            print("[INFO] AI Reply:", reply_text)

        # TEXT → SPEECH (use clean message without URLs)
        audio_b64 = synthesize_text_murf(reply_text)

    except Exception as e:
        print("[ERROR]:", str(e))
        return jsonify({"ok": False, "error": str(e)}), 500

    # -------- SEND RESPONSE --------
    response_data = {
        "ok": True,
        "transcript": transcript,
        "reply": reply_text,
        "audio_base64": audio_b64
    }
    
    # Add navigation/search data if present
    if isinstance(reply_result, dict) and reply_result.get("type") == "navigation":
        response_data["navigation"] = {
            "redirect_url": reply_result["redirect_url"],
            "destination": reply_result["destination"]
        }
    elif isinstance(reply_result, dict) and reply_result.get("type") == "search":
        response_data["search"] = {
            "redirect_url": reply_result["redirect_url"],
            "query": reply_result["query"]
        }
    elif isinstance(reply_result, dict) and reply_result.get("type") == "music":
        response_data["music"] = {
            "redirect_url": reply_result["redirect_url"],
            "song": reply_result["song"]
        }
    
    return jsonify(response_data)


@app.route("/text", methods=["POST"])
def text_handler():
    """Handle text input with optional TTS"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        tts_enabled = data.get('tts_enabled', True)
        
        if not message:
            return jsonify({
                "ok": False,
                "error": "No message provided"
            }), 400
        
        # Generate AI reply
        reply_result = generate_reply(message)
        
        # Handle special responses (navigation, search, shutdown)
        if isinstance(reply_result, dict) and reply_result.get("type") == "navigation":
            response_data = {
                "ok": True,
                "message": message,
                "reply": reply_result["message"],
                "navigation": {
                    "redirect_url": reply_result["redirect_url"],
                    "destination": reply_result["destination"]
                }
            }
        elif isinstance(reply_result, dict) and reply_result.get("type") == "search":
            response_data = {
                "ok": True,
                "message": message,
                "reply": reply_result["message"],
                "search": {
                    "redirect_url": reply_result["redirect_url"],
                    "query": reply_result["query"]
                }
            }
        elif isinstance(reply_result, dict) and reply_result.get("type") == "shutdown":
            response_data = {
                "ok": True,
                "message": message,
                "reply": reply_result["message"],
                "shutdown": {
                    "action": reply_result["action"]
                }
            }
        elif isinstance(reply_result, dict) and reply_result.get("type") == "music":
            response_data = {
                "ok": True,
                "message": message,
                "reply": reply_result["message"],
                "music": {
                    "redirect_url": reply_result["redirect_url"],
                    "song": reply_result["song"]
                }
            }
        else:
            response_data = {
                "ok": True,
                "message": message,
                "reply": str(reply_result)
            }
        
        # Add TTS audio if enabled
        if tts_enabled:
            try:
                # Get the text to synthesize (use clean message without URLs)
                if isinstance(reply_result, dict) and reply_result.get("type") in ["navigation", "search", "music"]:
                    tts_text = reply_result["message"]
                else:
                    tts_text = str(reply_result)
                audio_b64 = synthesize_text_murf(tts_text)
                response_data["audio_base64"] = audio_b64
            except Exception as tts_error:
                print(f"[TTS ERROR]: {tts_error}")
                # Continue without TTS
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"[TEXT ERROR]: {str(e)}")
        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500

@app.route("/wake-word", methods=["POST"])
def wake_word_handler():
    """Handle wake word detection"""
    if "audio" not in request.files:
        return jsonify({"ok": False, "error": "No audio file received"}), 400

    audio_file = request.files["audio"]

    # Save WebM input
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
        webm_path = tmp.name
        audio_file.save(webm_path)

    try:
        # Detect wake word — updated function returns (detected, job_id)
        detected, job_id = detect_wake_word(webm_path)

        response = {"ok": True, "wake_word_detected": detected}
        if job_id:
            response["job_id"] = job_id

        return jsonify(response)

    except Exception as e:
        print(f"[WAKE WORD ERROR]: {str(e)}")
        return jsonify({
            "ok": False,
            "error": str(e),
            "wake_word_detected": False
        }), 500


@app.route('/transcription/<job_id>', methods=['GET'])
def transcription_status(job_id):
    """Query status/result for an async transcription job created by wake-word flow."""
    info = get_transcription_job(job_id)
    if info is None:
        return jsonify({"ok": False, "error": "job_id not found"}), 404

    return jsonify({"ok": True, "job": info})

@app.route("/test", methods=["POST"])
def test_endpoint():
    """Test endpoint for the HTML test file"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        # Generate response using assistant
        reply = generate_reply(query)
        
        return jsonify({
            "ok": True,
            "query": query,
            "reply": reply
        })
    except Exception as e:
        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500

if __name__ == "__main__":
    print("[INFO] Starting STUDIO server on http://127.0.0.1:5000")
    print("[INFO] Make sure to open frontend/index.html in your browser")
    app.run(host="0.0.0.0", port=5000, debug=True)
