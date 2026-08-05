# speach_to_text

Standalone speech-to-text API. Send it a video/audio file or a PDF, get back JSON with the text.
Uses [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (OpenAI Whisper, no training/fine-tuning needed) — Armenian is one of the ~99 languages it supports out of the box. PDFs are read directly, and scanned/image pages fall back to OCR ([Tesseract](https://github.com/tesseract-ocr/tesseract), Armenian + English + Russian by default).

Optionally, `language=hy` can instead use [CrispASR](https://github.com/CrispStrobe/CrispASR) running a GGUF-quantized [NVIDIA FastConformer-Hybrid CTC (Armenian)](https://huggingface.co/cstr/stt-hy-fastconformer-hybrid-ctc-large-GGUF) model — a small C++ binary, no PyTorch, faster than whisper for Armenian specifically. This is fully optional: if it isn't built, `language=hy` just uses whisper like every other language, no errors, no setup required.

## System dependencies

Besides Python, install:
- **ffmpeg** — needed by whisper for media handling. macOS: `brew install ffmpeg`. Windows: `winget install ffmpeg` (or download from ffmpeg.org and add to PATH). Linux: `apt install ffmpeg`.
- **tesseract** — needed for OCR on scanned PDF pages. macOS: `brew install tesseract tesseract-lang` (the `-lang` package includes Armenian). Windows: install from [UB-Mannheim's build](https://github.com/UB-Mannheim/tesseract/wiki) and add it to PATH, then grab the `hye.traineddata` language file. Linux: `apt install tesseract-ocr tesseract-ocr-hye tesseract-ocr-rus`.

If tesseract isn't installed, everything still works except OCR on scanned (image-only) PDF pages — text-based PDFs are unaffected.

### Optional: faster Armenian path (CrispASR)

```
./scripts/build_crispasr.sh
```

Clones and builds [CrispASR](https://github.com/CrispStrobe/CrispASR) into `./crispasr` (needs `cmake` and a C++17 compiler) and downloads the Armenian GGUF model into `./models`. Once built, `language=hy` requests automatically use it instead of whisper — nothing else to configure. Skip this step entirely if you don't need it; the API works fine without it.

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

`POST /api/speech-to-text` — multipart form field `file` (audio, video, or PDF), optional query param `language` (e.g. `hy`, `en`, `ru`) to force a language instead of auto-detecting. Ignored for PDFs.

```
curl -X POST http://localhost:8008/api/speech-to-text \
  -F "file=@sample.mp4"

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
- `MAX_UPLOAD_MB` (default `500`) — max upload size.
- `OCR_LANGUAGES` (default `hye+eng+rus`) — Tesseract language codes to use on scanned PDF pages.
- `CRISPASR_BIN` (default `./crispasr/build/bin/crispasr`) — path to the CrispASR binary, if built.
- `CRISPASR_MODEL` (default `./models/stt-hy-fastconformer-hybrid-ctc-large-q4_k.gguf`) — path to the Armenian GGUF model (auto-downloaded on first use if missing).
