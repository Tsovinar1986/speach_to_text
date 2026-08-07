import io
import os
import threading
import wave

import numpy as np
import torch
from transformers import AutoTokenizer, VitsModel

# facebook/mms-tts-hyw: Meta MMS text-to-speech for Western Armenian.
MODEL_NAME = os.getenv("TTS_MODEL", "facebook/mms-tts-hyw")

_model: VitsModel | None = None
_tokenizer: AutoTokenizer | None = None
_model_lock = threading.Lock()


def _get_model() -> tuple[VitsModel, AutoTokenizer]:
    global _model, _tokenizer
    if _model is None:
        with _model_lock:
            if _model is None:
                _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
                _model = VitsModel.from_pretrained(MODEL_NAME)
                _model.eval()
    return _model, _tokenizer


def synthesize_speech(text: str) -> bytes:
    """Synthesize Western Armenian speech from text. Returns mono 16-bit PCM WAV bytes."""
    model, tokenizer = _get_model()
    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        waveform = model(**inputs).waveform[0].cpu().numpy()

    pcm = np.clip(waveform, -1.0, 1.0)
    pcm_int16 = (pcm * 32767).astype(np.int16)

    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(model.config.sampling_rate)
        wav_file.writeframes(pcm_int16.tobytes())
    return buffer.getvalue()
