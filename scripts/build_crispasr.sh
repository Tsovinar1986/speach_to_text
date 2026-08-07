#!/usr/bin/env bash
# Optional: builds the CrispASR C++ runtime (qwen3 backend only), used for a
# lighter Armenian STT path (Qwen3-ASR-0.6B, quantized to GGUF). If you skip
# this, the app still works fine — Armenian just goes through faster-whisper
# like every other language.
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -d crispasr ]; then
  git clone --recursive https://github.com/CrispStrobe/CrispASR crispasr
fi

cd crispasr
git submodule update --init --recursive

CMAKE_FLAGS="-DCMAKE_BUILD_TYPE=Release"
case "$(uname -s)" in
  Darwin) CMAKE_FLAGS="$CMAKE_FLAGS -DGGML_METAL=ON" ;;
esac

cmake -B build $CMAKE_FLAGS
cmake --build build -j"$(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 4)" --target crispasr-cli

cd ..
mkdir -p models
MODEL_PATH="models/qwen3-asr-0.6b-q4_k.gguf"
if [ ! -f "$MODEL_PATH" ]; then
  curl -L -o "$MODEL_PATH" \
    "https://huggingface.co/cstr/qwen3-asr-0.6b-GGUF/resolve/main/qwen3-asr-0.6b-q4_k.gguf"
fi

echo "Done. Binary: crispasr/build/bin/crispasr"
echo "Model:  $MODEL_PATH"
