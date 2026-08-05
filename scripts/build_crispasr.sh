#!/usr/bin/env bash
# Optional: builds the CrispASR C++ runtime, used for a faster/lighter Armenian
# STT path (nvidia/stt_hy_fastconformer_hybrid_large_pc, quantized to GGUF).
# If you skip this, the app still works fine — Armenian just goes through
# faster-whisper like every other language.
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
MODEL_PATH="models/stt-hy-fastconformer-hybrid-ctc-large-q4_k.gguf"
if [ ! -f "$MODEL_PATH" ]; then
  curl -L -o "$MODEL_PATH" \
    "https://huggingface.co/cstr/stt-hy-fastconformer-hybrid-ctc-large-GGUF/resolve/main/stt-hy-fastconformer-hybrid-ctc-large-q4_k.gguf"
fi

echo "Done. Binary: crispasr/build/bin/crispasr"
echo "Model:  $MODEL_PATH"
