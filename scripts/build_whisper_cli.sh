#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORKDIR="${TMPDIR:-/tmp}/whispercpp-build"
rm -rf "$WORKDIR"
git clone https://github.com/ggml-org/whisper.cpp.git "$WORKDIR"
cd "$WORKDIR"
cmake -B build
cmake --build build --config Release -j
mkdir -p "$ROOT/third_party/macos"
cp build/bin/whisper-cli "$ROOT/third_party/macos/"

echo "Copied whisper-cli to third_party/macos/"
