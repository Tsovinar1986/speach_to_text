import os
import threading

import torch
from transformers import pipeline

# Chillarmo/whisper-large-v3-turbo-armenian: openai/whisper-large-v3-turbo
# fine-tuned on Armenian (Common Voice 20) — 15.31% WER / 2.86% CER, noticeably
# more accurate for Armenian than stock whisper. Used only for language="hy".
MODEL_NAME = os.getenv("ARMENIAN_WHISPER_MODEL", "Chillarmo/whisper-large-v3-turbo-armenian")
DEVICE = os.getenv("WHISPER_DEVICE", "cpu")

_pipe = None
_pipe_lock = threading.Lock()


def _get_pipeline():
    global _pipe
    if _pipe is None:
        with _pipe_lock:
            if _pipe is None:
                device = 0 if DEVICE == "cuda" and torch.cuda.is_available() else -1
                _pipe = pipeline(
                    "automatic-speech-recognition",
                    model=MODEL_NAME,
                    device=device,
                )
    return _pipe


def transcribe_armenian(path: str) -> str:
    """Transcribe Armenian audio/video with the Chillarmo whisper-large-v3-turbo-armenian model."""
    pipe = _get_pipeline()
    # Sequential long-form generation (no chunk_length_s) uses Whisper's built-in
    # fallback heuristics (temperature retry, compression-ratio/logprob checks) to
    # catch hallucination loops on long audio; the chunked mode has no such guard.
    result = pipe(path, return_timestamps=True, generate_kwargs={"language": "hy", "task": "transcribe"})
    return result["text"].strip()
