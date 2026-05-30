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

if [[ ! -f "$ICON_ICNS" || "$ICON_SVG" -nt "$ICON_ICNS" ]]; then
  if ! command -v qlmanage >/dev/null 2>&1; then
    echo "Missing qlmanage, required to render $ICON_SVG"
    exit 1
  fi

  if ! command -v iconutil >/dev/null 2>&1; then
    echo "Missing iconutil, required to build $ICON_ICNS"
    exit 1
  fi

  tmpdir="$(mktemp -d)"
  trap 'rm -rf "$tmpdir"' EXIT
  thumb_dir="$tmpdir/thumb"
  iconset="$tmpdir/transcriber_icon.iconset"
  mkdir -p "$thumb_dir" "$iconset"

  qlmanage -t -s 1024 -o "$thumb_dir" "$ICON_SVG" >/dev/null
  rendered="$thumb_dir/$(basename "$ICON_SVG").png"

  if [[ ! -f "$rendered" ]]; then
    echo "Failed to render $ICON_SVG"
    exit 1
  fi

  for size in 16 32 128 256 512; do
    sips -z "$size" "$size" "$rendered" --out "$iconset/icon_${size}x${size}.png" >/dev/null
    retina=$((size * 2))
    sips -z "$retina" "$retina" "$rendered" --out "$iconset/icon_${size}x${size}@2x.png" >/dev/null
  done

  xattr -cr "$iconset" 2>/dev/null || true
  iconutil -c icns "$iconset" -o "$ICON_ICNS"
fi

python -m PyInstaller \
  --noconfirm \
  --clean \
  Transcriber-LP.spec

xattr -cr dist/Transcriber-LP.app 2>/dev/null || true
find dist/Transcriber-LP.app -xattrname com.apple.FinderInfo -exec xattr -d com.apple.FinderInfo {} + 2>/dev/null || true
find dist/Transcriber-LP.app -xattrname com.apple.FinderInfo -exec xattr -d -s com.apple.FinderInfo {} + 2>/dev/null || true

echo "Built dist/Transcriber-LP.app"
