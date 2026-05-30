#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -f "third_party/macos/ffmpeg" ]]; then
  echo "Missing third_party/macos/ffmpeg"
  exit 1
fi

if [[ ! -f "third_party/macos/ffprobe" ]]; then
  echo "Missing third_party/macos/ffprobe"
  exit 1
fi

if [[ ! -f "third_party/macos/whisper-cli" ]]; then
  echo "Missing third_party/macos/whisper-cli"
  exit 1
fi

if [[ ! -f "third_party/macos/models/ggml-base.bin" ]]; then
  echo "Missing third_party/macos/models/ggml-base.bin"
  exit 1
fi

python -m PyInstaller \
  --noconfirm \
  --clean \
  Transcriber-LP.spec

echo "Built dist/Transcriber-LP.app"
