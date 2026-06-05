#!/usr/bin/env bash
# Build script for Intel x86_64 macOS
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

if command -v otool >/dev/null 2>&1; then
  while IFS= read -r dep; do
    dylib="$(basename "$dep")"
    if [[ ! -e "third_party/macos/$dylib" ]]; then
      echo "Missing third_party/macos/$dylib, required by whisper-cli"
      exit 1
    fi
  done < <(otool -L third_party/macos/whisper-cli | awk '/@rpath/ {print $1}')
fi

if [[ "${TRANSCRIBER_LP_BUNDLE_MODEL:-0}" == "1" && ! -f "third_party/macos/models/ggml-base.bin" ]]; then
  echo "Missing third_party/macos/models/ggml-base.bin requested by TRANSCRIBER_LP_BUNDLE_MODEL=1"
  exit 1
fi

ICON_SVG="app/assets/transcriber_icon.svg"
ICON_ICNS="app/assets/transcriber_icon.icns"

if [[ ! -f "$ICON_ICNS" || "$ICON_SVG" -nt "$ICON_ICNS" || "scripts/render_macos_icon.py" -nt "$ICON_ICNS" ]]; then
  if ! command -v iconutil >/dev/null 2>&1; then
    echo "Missing iconutil, required to build $ICON_ICNS"
    exit 1
  fi

  tmpdir="$(mktemp -d)"
  trap 'rm -rf "$tmpdir"' EXIT
  iconset="$tmpdir/transcriber_icon.iconset"

  python scripts/render_macos_icon.py "$ICON_SVG" "$iconset"

  xattr -cr "$iconset" 2>/dev/null || true
  iconutil -c icns "$iconset" -o "$ICON_ICNS"
fi

python -m PyInstaller \
  --noconfirm \
  --clean \
  Transcriber-LP-intel.spec

xattr -cr dist/Transcriber-LP.app 2>/dev/null || true
find dist/Transcriber-LP.app -xattrname com.apple.FinderInfo -exec xattr -d com.apple.FinderInfo {} + 2>/dev/null || true
find dist/Transcriber-LP.app -xattrname com.apple.FinderInfo -exec xattr -d -s com.apple.FinderInfo {} + 2>/dev/null || true

echo "Built dist/Transcriber-LP.app (Intel x86_64)"
