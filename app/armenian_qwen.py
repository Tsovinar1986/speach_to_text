import os
import threading

from transformers import AutoModelForMultimodalLM, AutoProcessor

# Optional Armenian-specific engine: Qwen3-ASR, loaded directly via
# transformers (no separate build step). NOTE: Armenian is not among
# Qwen3-ASR's officially documented supported languages (30 languages + 22
# Chinese dialects), unlike faster-whisper which is used for every other
# language. Off by default for that reason — opt in with QWEN_ARMENIAN=1
# once you've verified transcription quality is acceptable for your use case.
MODEL_NAME = os.getenv("QWEN_ASR_MODEL", "Qwen/Qwen3-ASR-0.6B-hf")
ENABLED = os.getenv("QWEN_ARMENIAN", "0") == "1"

_model = None
_processor = None
_model_lock = threading.Lock()


def is_enabled() -> bool:
    return ENABLED


def _get_model():
    global _model, _processor
    if _model is None:
        with _model_lock:
            if _model is None:
                _processor = AutoProcessor.from_pretrained(MODEL_NAME)
                _model = AutoModelForMultimodalLM.from_pretrained(MODEL_NAME, device_map="auto")
    return _model, _processor


def transcribe_armenian_qwen(path: str) -> str:
    """Transcribe audio with Qwen3-ASR. Caller should check is_enabled() first."""
    model, processor = _get_model()
    inputs = processor.apply_transcription_request(audio=path).to(model.device, model.dtype)
    output_ids = model.generate(**inputs, max_new_tokens=256)
    generated_ids = output_ids[:, inputs["input_ids"].shape[1] :]
    return processor.decode(generated_ids, return_format="transcription_only")[0].strip()
