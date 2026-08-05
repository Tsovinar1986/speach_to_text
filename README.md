# speach_to_text

Standalone speech-to-text API. Send it a video/audio file or a PDF, get back JSON with the text.

- Armenian (`language=hy`) is transcribed with [NVIDIA FastConformer-Hybrid Large (hy)](https://huggingface.co/nvidia/stt_hy_fastconformer_hybrid_large_pc) — a model trained specifically for Armenian, more accurate than Whisper for it.
- Every other language (or auto-detect) uses [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (OpenAI Whisper, no training/fine-tuning needed, ~99 languages).
- PDFs are read directly, and scanned/image pages fall back to OCR ([Tesseract](https://github.com/tesseract-ocr/tesseract), Armenian + English + Russian by default).

## System dependencies

Besides Python, install:
- **ffmpeg** — needed for media handling and to convert audio for the Armenian model. macOS: `brew install ffmpeg`. Windows: `winget install ffmpeg` (or download from ffmpeg.org and add to PATH). Linux: `apt install ffmpeg`.
- **tesseract** — needed for OCR on scanned PDF pages. macOS: `brew install tesseract tesseract-lang` (the `-lang` package includes Armenian). Windows: install from [UB-Mannheim's build](https://github.com/UB-Mannheim/tesseract/wiki) and add it to PATH, then grab the `hye.traineddata` language file. Linux: `apt install tesseract-ocr tesseract-ocr-hye tesseract-ocr-rus`.

If tesseract isn't installed, everything still works except OCR on scanned (image-only) PDF pages — text-based PDFs are unaffected.

`nemo_toolkit[asr]` (in requirements.txt) pulls in PyTorch and is a large install (a few GB). It runs fine on CPU; a GPU just makes it faster.

## Run

macOS / Linux:
```
./run.sh
```

Windows:
```
run.bat
```

Or via Makefile (macOS/Linux, or Windows with GNU `make` installed):
```
make run
```

Windows without `make` installed — `make.bat` gives the same commands, no extra install needed:
```
make.bat run
make.bat dev
make.bat stop
make.bat clean
```

The first request for a given model downloads it (Whisper `medium` by default, or the NVIDIA Armenian model — both a few hundred MB to 1.5GB), so it can take a while. The server then listens on `http://localhost:8008`.

A small web UI is served at `http://localhost:8008/` — pick a file, hit the button, get the text back, no console needed.

## API

`POST /api/speech-to-text` — multipart form field `file` (audio, video, or PDF).

Optional query param `language`:
- `hy` — routes to the NVIDIA Armenian model
- any other code (`en`, `ru`, ...) or omitted — routes to Whisper (omitted = auto-detect)
- ignored for PDFs

```
curl -X POST "http://localhost:8008/api/speech-to-text?language=hy" \
  -F "file=@sample.mp3"

curl -X POST http://localhost:8008/api/speech-to-text \
  -F "file=@document.pdf"
```

Response:
```json
{ "text": "...", "language": "hy" }
```
`language` is `null` for PDFs (OCR text has no detected spoken language).

## Configuration

Environment variables:
- `WHISPER_MODEL_SIZE` (default `medium`) — e.g. `small`, `large-v3` for higher accuracy.
- `WHISPER_DEVICE` (default `cpu`) — set to `cuda` if a GPU is available.
- `ARMENIAN_ASR_MODEL` (default `nvidia/stt_hy_fastconformer_hybrid_large_pc`) — NeMo model name/path used for `language=hy`.
- `MAX_UPLOAD_MB` (default `500`) — max upload size.
- `OCR_LANGUAGES` (default `hye+eng+rus`) — Tesseract language codes to use on scanned PDF pages.
