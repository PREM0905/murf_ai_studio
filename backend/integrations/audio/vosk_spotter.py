import os
import io
import wave
import json

try:
    from vosk import Model, KaldiRecognizer
except Exception:
    Model = None

_model = None


def load_vosk_model():
    """Lazy-load Vosk model from path specified in env `VOSK_MODEL_PATH`.
    Returns model instance or None if not available.
    """
    global _model
    if _model is not None:
        return _model

    if Model is None:
        return None

    model_path = os.getenv("VOSK_MODEL_PATH", os.path.join(os.path.dirname(__file__), "../models/vosk-model-small-en-us-0.15"))
    model_path = os.path.abspath(model_path)
    if not os.path.exists(model_path):
        return None

    try:
        _model = Model(model_path)
        return _model
    except Exception:
        return None


def detect_keywords_in_wav_bytes(wav_bytes, keywords=("studio",), min_confidence=0.3):
    """Run Vosk on WAV bytes (PCM16 16k mono) and check if any keyword appears in transcript.
    Returns True if detected, False if processed and not detected, or None if model not available.
    """
    model = load_vosk_model()
    if model is None:
        return None

    try:
        wf = wave.open(io.BytesIO(wav_bytes), "rb")
    except Exception:
        return None

    # Ensure compatible params (we expect 16k mono PCM16)
    try:
        sr = wf.getframerate()
        channels = wf.getnchannels()
    except Exception:
        return None

    if sr != 16000 or channels != 1:
        # model expects 16k mono; if not, we could resample but skip to avoid heavy deps
        pass

    rec = KaldiRecognizer(model, sr)
    detected = False

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())
            text = res.get("text", "")
            if text:
                lower = text.lower()
                for kw in keywords:
                    if kw in lower:
                        detected = True
                        break
        if detected:
            break

    # Check final partials
    if not detected:
        final = json.loads(rec.FinalResult())
        final_text = final.get("text", "")
        lower = final_text.lower()
        for kw in keywords:
            if kw in lower:
                detected = True
                break

    return bool(detected)
