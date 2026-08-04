import os
import shutil
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .downloader import download_from_url
from .ocr import extract_pdf_text
from .transcription import transcribe_file

app = FastAPI(title="Speech-to-Text Service")

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_MB", "500")) * 1024 * 1024
CHUNK_SIZE = 1024 * 1024


class TranscriptionResponse(BaseModel):
    text: str
    language: str | None = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/speech-to-text", response_model=TranscriptionResponse)
async def speech_to_text(
    file: UploadFile | None = File(None),
    url: str | None = Form(None),
    language: str | None = None,
):
    if not file and not url:
        raise HTTPException(status_code=400, detail="Provide either 'file' or 'url'")
    if file and url:
        raise HTTPException(status_code=400, detail="Provide only one of 'file' or 'url'")

    tmp_dir = None
    if file:
        suffix = Path(file.filename or "").suffix
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp_path = tmp.name
            size = 0
            while chunk := await file.read(CHUNK_SIZE):
                size += len(chunk)
                if size > MAX_UPLOAD_BYTES:
                    tmp.close()
                    os.unlink(tmp_path)
                    raise HTTPException(status_code=413, detail="File too large")
                tmp.write(chunk)
    else:
        try:
            tmp_path, tmp_dir = download_from_url(url)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Could not download URL: {exc}") from exc

    try:
        if Path(tmp_path).suffix.lower() == ".pdf":
            text = extract_pdf_text(tmp_path)
            detected_language = None
        else:
            text, detected_language = transcribe_file(tmp_path, language=language)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        if tmp_dir:
            shutil.rmtree(tmp_dir, ignore_errors=True)
        else:
            os.unlink(tmp_path)

    return TranscriptionResponse(text=text, language=detected_language)


app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
