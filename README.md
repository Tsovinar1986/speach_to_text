# speach_to_text

Standalone speech-to-text API for video. Send it a video file, get back JSON with the transcribed text.
Uses [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (OpenAI Whisper, no training/fine-tuning needed) — Armenian is one of the ~99 languages it supports out of the box. Any video format ffmpeg can read (MP4, MOV, MKV, AVI, WEBM, etc.) is supported.

Optionally, `language=hy` can instead use [CrispASR](https://github.com/CrispStrobe/CrispASR) (built with only its `qwen3` backend) running a GGUF-quantized [Qwen3-ASR-0.6B](https://huggingface.co/cstr/qwen3-asr-0.6b-GGUF) model — a small C++ binary, no PyTorch. This is fully optional: if it isn't built, `language=hy` just uses whisper like every other language, no errors, no setup required.

## System dependencies

Besides Python, install:
- **ffmpeg** — needed by whisper for media handling. macOS: `brew install ffmpeg`. Windows: `winget install ffmpeg` (or download from ffmpeg.org and add to PATH). Linux: `apt install ffmpeg`.

### Optional: faster Armenian path (CrispASR)

```
./scripts/build_crispasr.sh
```

Clones and builds [CrispASR](https://github.com/CrispStrobe/CrispASR) into `./crispasr` (needs `cmake` and a C++17 compiler; only the `qwen3` ASR backend is kept, all other backends removed from the build) and downloads the Qwen3-ASR GGUF model into `./models`. Once built, `language=hy` requests automatically use it instead of whisper — nothing else to configure. Skip this step entirely if you don't need it; the API works fine without it.

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
- `WHISPER_MODEL_SIZE` (default `medium`) — e.g. `small`, `large-v3` for higher accuracy.
- `WHISPER_DEVICE` (default `cpu`) — set to `cuda` if a GPU is available.
- `MAX_UPLOAD_MB` (default `500`) — max upload size.
- `CRISPASR_BIN` (default `./crispasr/build/bin/crispasr`) — path to the CrispASR binary, if built.
- `CRISPASR_MODEL` (default `./models/qwen3-asr-0.6b-q4_k.gguf`) — path to the Qwen3-ASR GGUF model (auto-downloaded on first use if missing).

## License

[MIT](LICENSE)
