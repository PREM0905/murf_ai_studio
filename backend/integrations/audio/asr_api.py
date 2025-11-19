# backend/asr_api.py

import time
import requests
import os
import io
import threading
import concurrent.futures
import math

ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")

# Allow configurable polling via env vars
DEFAULT_POLL_TIMEOUT = float(os.getenv("ASR_POLL_TIMEOUT", "15"))
DEFAULT_POLL_INTERVAL = float(os.getenv("ASR_POLL_INTERVAL", "0.5"))

UPLOAD_ENDPOINT = "https://api.assemblyai.com/v2/upload"
TRANSCRIBE_ENDPOINT = "https://api.assemblyai.com/v2/transcript"

HEADERS = {
    "authorization": ASSEMBLYAI_API_KEY
}

# Concurrency control for AssemblyAI uploads/transcriptions
MAX_CONCURRENCY = int(os.getenv("ASR_MAX_CONCURRENCY", "2"))
ASR_MAX_RETRIES = int(os.getenv("ASR_MAX_RETRIES", "3"))
ASR_BACKOFF_FACTOR = float(os.getenv("ASR_BACKOFF_FACTOR", "1.0"))

# Thread pool and semaphore to limit concurrent requests to AssemblyAI
_executor = concurrent.futures.ThreadPoolExecutor(max_workers=MAX_CONCURRENCY)
_semaphore = threading.BoundedSemaphore(MAX_CONCURRENCY)


def _requests_with_retries(method, url, max_retries=ASR_MAX_RETRIES, backoff_factor=ASR_BACKOFF_FACTOR, **kwargs):
    """Helper to call requests with retries on 429/5xx responses using exponential backoff."""
    attempt = 0
    while True:
        try:
            resp = requests.request(method, url, **kwargs)
        except Exception as e:
            # Network-level error - retry
            attempt += 1
            if attempt > max_retries:
                raise
            sleep_for = backoff_factor * (2 ** (attempt - 1))
            time.sleep(sleep_for)
            continue

        # If rate-limited or server error, retry
        if resp.status_code in (429, 502, 503, 504) and attempt < max_retries:
            attempt += 1
            sleep_for = backoff_factor * (2 ** (attempt - 1))
            time.sleep(sleep_for)
            continue

        return resp



def upload_file_to_assemblyai(filepath):
    """
    Upload WAV file to AssemblyAI and return the 'upload_url'.
    """
    if not ASSEMBLYAI_API_KEY:
        raise RuntimeError("ASSEMBLYAI_API_KEY is missing in .env")

    with open(filepath, "rb") as f:
        response = _requests_with_retries('POST', UPLOAD_ENDPOINT, headers=HEADERS, data=f)

    if response.status_code not in (200, 201):
        raise RuntimeError(f"AssemblyAI Upload Error {response.status_code}: {response.text}")

    return response.json().get("upload_url")


def upload_bytes_to_assemblyai(file_bytes):
    """
    Upload bytes to AssemblyAI (useful for in-memory conversion) and return upload_url
    """
    if not ASSEMBLYAI_API_KEY:
        raise RuntimeError("ASSEMBLYAI_API_KEY is missing in .env")

    # requests can stream bytes via io.BytesIO
    bio = io.BytesIO(file_bytes)
    bio.seek(0)
    response = _requests_with_retries('POST', UPLOAD_ENDPOINT, headers=HEADERS, data=bio)

    if response.status_code not in (200, 201):
        raise RuntimeError(f"AssemblyAI Upload Error {response.status_code}: {response.text}")

    return response.json().get("upload_url")


def request_transcription(upload_url):
    """
    Start transcription job and return the transcript ID.
    """
    payload = {
        "audio_url": upload_url,
        "language_code": "en"
    }

    response = _requests_with_retries('POST', TRANSCRIBE_ENDPOINT, headers=HEADERS, json=payload)

    if response.status_code not in (200, 201):
        raise RuntimeError(f"AssemblyAI Transcription Error {response.status_code}: {response.text}")

    return response.json().get("id")


def poll_transcript(transcript_id, timeout=None, interval=None):
    """
    Poll until AssemblyAI finishes transcription.
    """
    url = f"{TRANSCRIBE_ENDPOINT}/{transcript_id}"
    if timeout is None:
        timeout = DEFAULT_POLL_TIMEOUT
    if interval is None:
        interval = DEFAULT_POLL_INTERVAL

    end_time = time.time() + float(timeout)

    while time.time() < end_time:
        response = _requests_with_retries('GET', url, headers=HEADERS)
        data = response.json()

        if data.get("status") == "completed":
            return data.get("text", "")

        if data.get("status") == "error":
            raise RuntimeError(f"AssemblyAI Error: {data.get('error')}")

        time.sleep(float(interval))

    raise TimeoutError("AssemblyAI transcription timeout.")


def transcribe_file_assemblyai(filepath):
    """
    Complete STT Pipeline:
    1. Upload to AAI
    2. Request transcription
    3. Poll for result
    """
    # Keep compatibility: read file bytes and forward to bytes-based uploader
    with open(filepath, "rb") as f:
        data = f.read()

    return transcribe_bytes_assemblyai(data)


def transcribe_bytes_assemblyai(file_bytes, timeout=None, interval=None):
    """
    Upload bytes and transcribe. Returns transcript text or empty string on timeout.
    """
    upload_url = upload_bytes_to_assemblyai(file_bytes)
    transcript_id = request_transcription(upload_url)
    try:
        return poll_transcript(transcript_id, timeout=timeout, interval=interval)
    except TimeoutError:
        return ""


def submit_transcription_bytes(file_bytes, timeout=None, interval=None, block=False):
    """
    Submit transcription task to a background pool with limited concurrency.
    Returns a Future if accepted, or None if the concurrency limit is reached and block=False.
    If block=True this will wait until a slot is available.
    """
    acquired = _semaphore.acquire(blocking=block)
    if not acquired:
        return None

    def _worker(bts, to, itv):
        try:
            return transcribe_bytes_assemblyai(bts, timeout=to, interval=itv)
        finally:
            try:
                _semaphore.release()
            except Exception:
                pass

    future = _executor.submit(_worker, file_bytes, timeout, interval)
    return future
