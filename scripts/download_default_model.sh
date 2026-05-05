#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TARGET_DIR="$ROOT/third_party/macos/models"
mkdir -p "$TARGET_DIR"

URL="https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin?download=true"
OUT="$TARGET_DIR/ggml-base.bin"

curl -L "$URL" -o "$OUT"
shasum "$OUT"
