import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import armenian_whisper
from .transcription import transcribe_file
from .tts import synthesize_speech

app = FastAPI(title="Speech-to-Text Service")

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_MB", "500")) * 1024 * 1024
CHUNK_SIZE = 1024 * 1024


class TranscriptionResponse(BaseModel):
    text: str
    language: str | None = None


class TextToSpeechRequest(BaseModel):
    text: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/speech-to-text", response_model=TranscriptionResponse)
async def speech_to_text(file: UploadFile = File(...), language: str | None = None):
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

    try:
        if language == "hy":
            # Fine-tuned Armenian model, more accurate than stock whisper for hy.
            text = armenian_whisper.transcribe_armenian(tmp_path)
            detected_language = "hy"
        else:
            text, detected_language = transcribe_file(tmp_path, language=language)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        os.unlink(tmp_path)

    return TranscriptionResponse(text=text, language=detected_language)


@app.post("/api/text-to-speech")
async def text_to_speech(payload: TextToSpeechRequest):
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")
    try:
        audio_bytes = synthesize_speech(payload.text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return Response(content=audio_bytes, media_type="audio/wav")


app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
