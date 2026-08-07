# speach_to_text

Standalone speech-to-text API for video. Send it a video file, get back JSON with the transcribed text.
Uses [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (OpenAI Whisper, no training/fine-tuning needed) for every language, including Armenian — one of the ~99 languages it supports out of the box. Any video format ffmpeg can read (MP4, MOV, MKV, AVI, WEBM, etc.) is supported.

The app also exposes a text-to-speech endpoint for Western Armenian using [facebook/mms-tts-hyw](https://huggingface.co/facebook/mms-tts-hyw) (Meta MMS).

## System dependencies

Besides Python, install:
- **ffmpeg** — needed by whisper for media handling. macOS: `brew install ffmpeg`. Windows: `winget install ffmpeg` (or download from ffmpeg.org and add to PATH). Linux: `apt install ffmpeg`.

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

A small web UI is served at `http://localhost:8008/` — pick a file, hit the button, get the text back, no console needed. It also has a text-to-speech box for Western Armenian.

## API

`POST /api/speech-to-text` — multipart form field `file` (video), optional query param `language` (e.g. `hy`, `en`, `ru`) to force a language instead of auto-detecting.

```
curl -X POST http://localhost:8008/api/speech-to-text \
  -F "file=@sample.mp4"
```

Response:
```json
{ "text": "...", "language": "hy" }
```

`POST /api/text-to-speech` — JSON body `{ "text": "..." }`, returns `audio/wav` (Western Armenian, via facebook/mms-tts-hyw).

```
curl -X POST http://localhost:8008/api/text-to-speech \
  -H "Content-Type: application/json" \
  -d '{"text": "Բարև ձեզ"}' \
  --output speech.wav
```

## Configuration

Environment variables:
- `WHISPER_MODEL_SIZE` (default `medium`) — e.g. `small`, `large-v3` for higher accuracy.
- `WHISPER_DEVICE` (default `cpu`) — set to `cuda` if a GPU is available.
- `MAX_UPLOAD_MB` (default `500`) — max upload size.
- `TTS_MODEL` (default `facebook/mms-tts-hyw`) — text-to-speech model.

## License

[MIT](LICENSE)
