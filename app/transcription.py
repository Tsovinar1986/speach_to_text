import os
import threading

from faster_whisper import WhisperModel

# large-v3 has the best Armenian accuracy; override via env for a lighter/faster model.
MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "medium")
DEVICE = os.getenv("WHISPER_DEVICE", "cpu")
COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE_TYPE", "int8" if DEVICE == "cpu" else "float16")

_model: WhisperModel | None = None
_model_lock = threading.Lock()


def get_model() -> WhisperModel:
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:
                _model = WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE)
    return _model


def transcribe_file(path: str, language: str | None = None) -> tuple[str, str]:
    """Transcribe an audio or video file. Returns (text, detected_language)."""
    model = get_model()
    segments, info = model.transcribe(path, beam_size=5, language=language)
    text = "".join(segment.text for segment in segments).strip()
    return text, info.language
