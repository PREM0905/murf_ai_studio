import threading
import time
import uuid
from concurrent.futures import Future

from integrations.audio.asr_api import submit_transcription_bytes, transcribe_bytes_assemblyai

# Simple in-memory transcription job manager.
# Each job_id maps to a dict with a Future and metadata.
_jobs = {}
_lock = threading.Lock()

def _wrap_thread(func, future, *args, **kwargs):
    try:
        res = func(*args, **kwargs)
        future.set_result(res)
    except Exception as e:
        future.set_exception(e)

def submit_job(file_bytes, timeout=None, interval=None):
    """Submit a transcription job and return a job_id. The job is guaranteed
    to be registered immediately; the underlying execution may use the
    ASR executor or a local background thread if the executor is busy.
    """
    job_id = str(uuid.uuid4())
    fut = None

    # Try to get a future from the shared ASR submitter (non-blocking)
    try:
        fut = submit_transcription_bytes(file_bytes, timeout=timeout, interval=interval, block=False)
    except Exception:
        fut = None

    # If ASR submitter returned a Future, store it. Otherwise create a thread that runs the transcription.
    if fut is None:
        fut = Future()
        t = threading.Thread(target=_wrap_thread, args=(transcribe_bytes_assemblyai, fut, file_bytes, timeout, interval), daemon=True)
        t.start()

    with _lock:
        _jobs[job_id] = {
            "future": fut,
            "created": time.time()
        }

    return job_id

def get_job(job_id):
    """Return job status/result for a job_id. Returns None if job_id not found.
    Response shape: {status: "pending"|"done"|"error", result: <text>|None, error: <str>|None}
    """
    with _lock:
        info = _jobs.get(job_id)
    if not info:
        return None

    fut = info["future"]
    if not fut.done():
        return {"status": "pending", "result": None, "error": None}

    try:
        res = fut.result()
        return {"status": "done", "result": res, "error": None}
    except Exception as e:
        return {"status": "error", "result": None, "error": str(e)}

def cleanup_older_than(seconds=3600):
    """Remove jobs older than `seconds` to keep memory bounded."""
    cutoff = time.time() - float(seconds)
    with _lock:
        to_del = [jid for jid, info in _jobs.items() if info.get("created", 0) < cutoff]
        for jid in to_del:
            try:
                del _jobs[jid]
            except KeyError:
                pass
