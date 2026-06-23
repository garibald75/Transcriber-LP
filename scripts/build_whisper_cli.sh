#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# Pin the whisper.cpp version for reproducible builds. Keep in sync with
# BUNDLED_ENGINE_VERSION in app/core/engine_manager.py when re-vendoring.
WHISPER_CPP_TAG="${WHISPER_CPP_TAG:-v1.7.5}"
WORKDIR="${TMPDIR:-/tmp}/whispercpp-build"
rm -rf "$WORKDIR"
echo "Building whisper.cpp $WHISPER_CPP_TAG"
git clone --depth 1 --branch "$WHISPER_CPP_TAG" https://github.com/ggml-org/whisper.cpp.git "$WORKDIR"
cd "$WORKDIR"
cmake -B build
cmake --build build --config Release -j
mkdir -p "$ROOT/third_party/macos"
cp build/bin/whisper-cli "$ROOT/third_party/macos/"
cp -P build/src/libwhisper.1.dylib build/src/libwhisper.1.*.dylib "$ROOT/third_party/macos/"
cp -P build/ggml/src/libggml.0.dylib build/ggml/src/libggml.0.*.dylib "$ROOT/third_party/macos/"
cp -P build/ggml/src/libggml-base.0.dylib build/ggml/src/libggml-base.0.*.dylib "$ROOT/third_party/macos/"
cp -P build/ggml/src/libggml-cpu.0.dylib build/ggml/src/libggml-cpu.0.*.dylib "$ROOT/third_party/macos/"
cp -P build/ggml/src/ggml-blas/libggml-blas.0.dylib build/ggml/src/ggml-blas/libggml-blas.0.*.dylib "$ROOT/third_party/macos/"

if [[ -f build/ggml/src/ggml-metal/libggml-metal.0.dylib ]]; then
  cp -P build/ggml/src/ggml-metal/libggml-metal.0.dylib build/ggml/src/ggml-metal/libggml-metal.0.*.dylib "$ROOT/third_party/macos/"
fi

if command -v install_name_tool >/dev/null 2>&1; then
  install_name_tool -add_rpath "@executable_path" "$ROOT/third_party/macos/whisper-cli" 2>/dev/null || true
fi

echo "Copied whisper-cli to third_party/macos/"
