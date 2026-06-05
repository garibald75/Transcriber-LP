#!/usr/bin/env bash
# Build script for macOS packages.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

normalize_arch() {
  case "${1:-}" in
    arm64|aarch64)
      echo "arm64"
      ;;
    x86_64|amd64|intel)
      echo "x86_64"
      ;;
    universal|universal2)
      echo "universal2"
      ;;
    *)
      echo "Usage: $0 <arm64|x86_64|universal2>" >&2
      exit 2
      ;;
  esac
}

target_arch="$(normalize_arch "${1:-${TRANSCRIBER_LP_TARGET_ARCH:-arm64}}")"

if [[ -n "${TRANSCRIBER_LP_VENDOR_DIR:-}" ]]; then
  vendor_dir="$TRANSCRIBER_LP_VENDOR_DIR"
else
  candidate="$ROOT/third_party/macos/$target_arch"
  if [[ -f "$candidate/ffmpeg" || -f "$candidate/ffprobe" || -f "$candidate/whisper-cli" ]]; then
    vendor_dir="$candidate"
  else
    vendor_dir="$ROOT/third_party/macos"
  fi
fi

echo "Building Transcriber-LP for macOS $target_arch"
echo "Using vendor inputs: $vendor_dir"

"$ROOT/scripts/validate_macos_vendor.sh" "$target_arch" "$vendor_dir"
export TRANSCRIBER_LP_TARGET_ARCH="$target_arch"
export TRANSCRIBER_LP_VENDOR_DIR="$vendor_dir"

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
  Transcriber-LP.spec

xattr -cr dist/Transcriber-LP.app 2>/dev/null || true
find dist/Transcriber-LP.app -xattrname com.apple.FinderInfo -exec xattr -d com.apple.FinderInfo {} + 2>/dev/null || true
find dist/Transcriber-LP.app -xattrname com.apple.FinderInfo -exec xattr -d -s com.apple.FinderInfo {} + 2>/dev/null || true

echo "Built dist/Transcriber-LP.app ($target_arch)"
