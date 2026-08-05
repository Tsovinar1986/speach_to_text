import os
import subprocess
import urllib.request
from pathlib import Path

# Optional Armenian-specific engine: CrispASR (ggml/C++ runtime) running the
# GGUF-quantized NVIDIA FastConformer-Hybrid CTC model. Used only when
# language="hy" is requested AND the binary + model are available; otherwise
# app/main.py falls back to faster-whisper so this stays fully opt-in.
BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_BIN = BASE_DIR / "crispasr" / "build" / "bin" / "crispasr"
DEFAULT_MODEL = BASE_DIR / "models" / "stt-hy-fastconformer-hybrid-ctc-large-q4_k.gguf"
MODEL_URL = (
    "https://huggingface.co/cstr/stt-hy-fastconformer-hybrid-ctc-large-GGUF/"
    "resolve/main/stt-hy-fastconformer-hybrid-ctc-large-q4_k.gguf"
)

CRISPASR_BIN = Path(os.getenv("CRISPASR_BIN", str(DEFAULT_BIN)))
CRISPASR_MODEL = Path(os.getenv("CRISPASR_MODEL", str(DEFAULT_MODEL)))


def is_available() -> bool:
    return CRISPASR_BIN.is_file() and os.access(CRISPASR_BIN, os.X_OK)


def _ensure_model() -> None:
    if CRISPASR_MODEL.exists():
        return
    CRISPASR_MODEL.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = CRISPASR_MODEL.with_suffix(".gguf.part")
    urllib.request.urlretrieve(MODEL_URL, tmp_path)
    tmp_path.rename(CRISPASR_MODEL)


def transcribe_armenian_crispasr(path: str) -> str:
    """Transcribe Armenian audio with CrispASR. Caller should check is_available() first."""
    _ensure_model()
    result = subprocess.run(
        [
            str(CRISPASR_BIN),
            "--backend", "fastconformer-ctc",
            "-m", str(CRISPASR_MODEL),
            "-f", path,
            "-nt",  # no timestamps, plain text only
            "-np",  # no log/progress prints — stdout is just the transcript
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()
