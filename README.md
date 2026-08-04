# speach_to_text

Standalone speech-to-text API. Send it a video/audio file, a social media link (Instagram Reels, TikTok, YouTube Shorts, etc.), or a PDF, and get back JSON with the text.
Uses [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (OpenAI Whisper, no training/fine-tuning needed) — Armenian is one of the ~99 languages it supports out of the box. PDFs are read directly, and scanned/image pages fall back to OCR ([Tesseract](https://github.com/tesseract-ocr/tesseract), Armenian + English + Russian by default).

## System dependencies

Besides Python, install:
- **ffmpeg** — needed by yt-dlp/whisper for media handling. macOS: `brew install ffmpeg`. Windows: `winget install ffmpeg` (or download from ffmpeg.org and add to PATH). Linux: `apt install ffmpeg`.
- **tesseract** — needed for OCR on scanned PDF pages. macOS: `brew install tesseract tesseract-lang` (the `-lang` package includes Armenian). Windows: install from [UB-Mannheim's build](https://github.com/UB-Mannheim/tesseract/wiki) and add it to PATH, then grab the `hye.traineddata` language file. Linux: `apt install tesseract-ocr tesseract-ocr-hye tesseract-ocr-rus`.

If tesseract isn't installed, everything still works except OCR on scanned (image-only) PDF pages — text-based PDFs are unaffected.

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

The first request downloads the Whisper model (`medium` by default), so it can take a while. The server then listens on `http://localhost:8008`.

A small web UI is served at `http://localhost:8008/` — pick a file, hit the button, get the text back, no console needed.

## API

`POST /api/speech-to-text` — provide exactly one of:
- multipart form field `file` — audio, video, or PDF
- multipart form field `url` — a public link (Instagram Reels, TikTok, YouTube Shorts, etc.); the server downloads it with `yt-dlp` and transcribes it the same as an uploaded video

Optional query param `language` (e.g. `hy`, `en`, `ru`) forces a language instead of auto-detecting. Ignored for PDFs.

```
curl -X POST http://localhost:8008/api/speech-to-text \
  -F "file=@sample.mp4"

curl -X POST http://localhost:8008/api/speech-to-text \
  -F "url=https://www.instagram.com/reel/xxxxxxxx/"

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
- `MAX_UPLOAD_MB` (default `500`) — max upload/download size.
- `MAX_DOWNLOAD_SECONDS` (default `1800`) — max duration for `url` downloads.
- `OCR_LANGUAGES` (default `hye+eng+rus`) — Tesseract language codes to use on scanned PDF pages.
