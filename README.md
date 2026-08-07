# speach_to_text

Standalone speech-to-text API for video. Send it a video file, get back JSON with the transcribed text.
Uses [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (OpenAI Whisper, no training/fine-tuning needed) — Armenian is one of the ~99 languages it supports out of the box. Any video format ffmpeg can read (MP4, MOV, MKV, AVI, WEBM, etc.) is supported.

Optionally, `language=hy` can instead use [Qwen3-ASR-0.6B](https://huggingface.co/Qwen/Qwen3-ASR-0.6B-hf) (loaded directly via `transformers`, no separate build step). **This is off by default** — Armenian is not among Qwen3-ASR's officially documented supported languages (30 languages + 22 Chinese dialects), so faster-whisper is the better-tested option for Armenian. Opt in with `QWEN_ARMENIAN=1` once you've verified transcription quality is acceptable for your use case.

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
- `QWEN_ARMENIAN` (default `0`) — set to `1` to use Qwen3-ASR instead of whisper for `language=hy` requests. See the caveat above.
- `QWEN_ASR_MODEL` (default `Qwen/Qwen3-ASR-0.6B-hf`) — e.g. `Qwen/Qwen3-ASR-1.7B-hf` for the larger variant.
- `TTS_MODEL` (default `facebook/mms-tts-hyw`) — text-to-speech model.

## License

[MIT](LICENSE)
