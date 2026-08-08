# speach_to_text

Standalone speech-to-text API for video. Send it a video file, get back JSON with the transcribed text.
Uses [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (OpenAI Whisper) for every language, one of the ~99 it supports out of the box. `language=hy` (Armenian) instead uses [Chillarmo/whisper-large-v3-turbo-armenian](https://huggingface.co/Chillarmo/whisper-large-v3-turbo-armenian) — `openai/whisper-large-v3-turbo` fine-tuned on Armenian, 15.31% WER / 2.86% CER, noticeably more accurate for Armenian than stock whisper. Any video format ffmpeg can read (MP4, MOV, MKV, AVI, WEBM, etc.) is supported.

For Armenian results, the transcript is then rewritten from standard/literary Eastern Armenian into colloquial spoken Yerevan Armenian, via a local [Ollama](https://ollama.com) model (default `qwen2.5:7b`). Requires an Ollama server running locally with that model pulled (`ollama pull qwen2.5:7b`); if Ollama isn't reachable, the request fails rather than silently skipping the rewrite. Quality depends on the model's Armenian ability, which is limited — expect a conservative rewrite rather than a bold dialect transformation.

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

The first request downloads the Whisper model (`medium` by default), so it can take a while. The server then listens on `http://localhost:8008` — override with `PORT`/`HOST` env vars (e.g. `PORT=9000 ./run.sh`) if 8008 is already taken by something else.

A small web UI is served at `http://localhost:8008/` — pick a file, hit the button, get the text back, no console needed.

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

## Configuration

Environment variables:
- `WHISPER_MODEL_SIZE` (default `medium`) — e.g. `small`, `large-v3` for higher accuracy (non-Armenian languages).
- `WHISPER_DEVICE` (default `cpu`) — set to `cuda` if a GPU is available.
- `MAX_UPLOAD_MB` (default `500`) — max upload size.
- `ARMENIAN_WHISPER_MODEL` (default `Chillarmo/whisper-large-v3-turbo-armenian`) — model used for `language=hy`.
- `OLLAMA_URL` (default `http://localhost:11434/api/chat`) — Ollama chat endpoint used for the spoken-Yerevan rewrite.
- `OLLAMA_MODEL` (default `qwen2.5:7b`) — Ollama model used for the rewrite.

## License

[MIT](LICENSE)
