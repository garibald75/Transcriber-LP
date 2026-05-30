#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TARGET_DIR="$ROOT/third_party/macos/models"
mkdir -p "$TARGET_DIR"

URL="https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin?download=true"
OUT="$TARGET_DIR/ggml-base.bin"
EXPECTED_SHA1="465707469ff3a37a2b9b8d8f89f2f99de7299dac"

curl -L "$URL" -o "$OUT"
actual_sha1="$(shasum "$OUT" | awk '{print $1}')"
if [[ "$actual_sha1" != "$EXPECTED_SHA1" ]]; then
  echo "Checksum mismatch for $OUT"
  echo "Expected: $EXPECTED_SHA1"
  echo "Actual:   $actual_sha1"
  rm -f "$OUT"
  exit 1
fi

echo "Downloaded $OUT"
echo "SHA1: $actual_sha1"
