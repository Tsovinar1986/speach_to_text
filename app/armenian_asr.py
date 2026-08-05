import os
import subprocess
import tempfile
import threading

# NVIDIA FastConformer-Hybrid Large (hy) — Armenian-only ASR, more accurate than
# Whisper for Armenian but doesn't handle other languages, so it's only used
# when the caller explicitly asks for language="hy".
MODEL_NAME = os.getenv("ARMENIAN_ASR_MODEL", "nvidia/stt_hy_fastconformer_hybrid_large_pc")

_model = None
_model_lock = threading.Lock()


def _get_model():
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:
                import nemo.collections.asr as nemo_asr

                _model = nemo_asr.models.EncDecHybridRNNTCTCBPEModel.from_pretrained(
                    model_name=MODEL_NAME
                )
                _model.eval()
    return _model


def _to_16k_mono_wav(src_path: str) -> str:
    fd, wav_path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    subprocess.run(
        ["ffmpeg", "-y", "-i", src_path, "-ac", "1", "-ar", "16000", wav_path],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return wav_path


def transcribe_armenian(path: str) -> str:
    model = _get_model()
    wav_path = _to_16k_mono_wav(path)
    try:
        output = model.transcribe([wav_path])
        result = output[0]
        return result.text if hasattr(result, "text") else str(result)
    finally:
        os.unlink(wav_path)
