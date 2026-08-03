# speach_to_text

Standalone speech-to-text API. Send it a video or audio file, get back JSON with the spoken text.
Uses [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (OpenAI Whisper, no training/fine-tuning needed) — Armenian is one of the ~99 languages it supports out of the box.

## Run

macOS / Linux:
```
./run.sh
```

Windows:
```
run.bat
```

Or via Makefile (macOS/Linux, or Windows with `make` installed):
```
make run
```

The first request downloads the Whisper model (`medium` by default), so it can take a while. The server then listens on `http://localhost:8008`.

A small web UI is served at `http://localhost:8008/` — pick a file, hit the button, get the text back, no console needed.

## API

`POST /api/speech-to-text` — multipart form field `file` (audio or video), optional query param `language` (e.g. `hy`, `en`, `ru`) to force a language instead of auto-detecting.

```
curl -X POST http://localhost:8008/api/speech-to-text \
  -F "file=@sample.mp4"
```

Response:
```json
{ "text": "...", "language": "hy" }
```

## Configuration

Environment variables:
- `WHISPER_MODEL_SIZE` (default `medium`) — e.g. `small`, `large-v3` for higher accuracy.
- `WHISPER_DEVICE` (default `cpu`) — set to `cuda` if a GPU is available.
- `MAX_UPLOAD_MB` (default `500`) — max upload size.
