# backend/murf_api.py

import requests
import base64
import os
import tempfile

MURF_API_KEY = os.getenv("MURF_API_KEY")

MURF_ENDPOINT = "https://global.api.murf.ai/v1/speech/stream"

HEADERS = {
    "api-key": MURF_API_KEY,
    "Content-Type": "application/json"
}


def synthesize_text_murf(text):
    """
    Uses Murf Falcon real-time streaming TTS.
    Returns: Base64 WAV audio (so frontend can play directly)
    """
    if not MURF_API_KEY:
        raise RuntimeError("MURF_API_KEY missing in .env")

    payload = {
        "text": text,
        "model": "FALCON",
        "voiceId": "Matthew",
        "multiNativeLocale": "en-US",
        "format": "WAV"
    }

    response = requests.post(
        MURF_ENDPOINT,
        headers=HEADERS,
        json=payload,
        stream=True,  # streaming output
        timeout=10    # faster timeout
    )

    if response.status_code != 200:
        raise RuntimeError(f"Murf Error {response.status_code}: {response.text}")

    # Save file temporarily then return base64
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        for chunk in response.iter_content(chunk_size=1024):
            tmp.write(chunk)
        wav_path = tmp.name

    with open(wav_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    return encoded
