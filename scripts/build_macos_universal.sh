#!/usr/bin/env bash
# Build universal macOS app (ARM64 + x86_64)
# Requires both ARM64 and Intel x86_64 binaries in third_party/macos/
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

ARCH="${1:-}"

if [[ -z "$ARCH" ]]; then
  echo "Usage: $0 <arm64|intel|both>"
  echo ""
  echo "Builds Transcriber-LP for different architectures:"
  echo "  arm64  - Build for Apple Silicon (ARM64)"
  echo "  intel  - Build for Intel x86_64"
  echo "  both   - Build for both architectures (requires universal binaries)"
  exit 1
fi

case "$ARCH" in
  arm64)
    echo "Building for ARM64 (Apple Silicon)..."
    "$ROOT/scripts/build_macos.sh"
    ;;
  intel)
    echo "Building for Intel x86_64..."
    "$ROOT/scripts/build_macos_intel.sh"
    ;;
  both)
    echo "Building for both ARM64 and x86_64..."
    echo ""
    echo "Step 1: Building ARM64 version..."
    "$ROOT/scripts/build_macos.sh"
    mv "$ROOT/dist/Transcriber-LP.app" "$ROOT/dist/Transcriber-LP-arm64.app"
    
    echo ""
    echo "Step 2: Building Intel x86_64 version..."
    "$ROOT/scripts/build_macos_intel.sh"
    mv "$ROOT/dist/Transcriber-LP.app" "$ROOT/dist/Transcriber-LP-intel.app"
    
    echo ""
    echo "Step 3: Creating universal binary..."
    lipo -create \
      "$ROOT/dist/Transcriber-LP-arm64.app/Contents/MacOS/Transcriber-LP" \
      "$ROOT/dist/Transcriber-LP-intel.app/Contents/MacOS/Transcriber-LP" \
      -output "$ROOT/dist/Transcriber-LP-universal.macho"
    
    # Copy ARM64 as base, replace the executable with universal binary
    cp -r "$ROOT/dist/Transcriber-LP-arm64.app" "$ROOT/dist/Transcriber-LP.app"
    cp "$ROOT/dist/Transcriber-LP-universal.macho" "$ROOT/dist/Transcriber-LP.app/Contents/MacOS/Transcriber-LP"
    
    # Cleanup intermediate files
    rm -f "$ROOT/dist/Transcriber-LP-universal.macho"
    
    echo "✓ Universal app created at dist/Transcriber-LP.app"
    echo ""
    echo "Arch info:"
    file "$ROOT/dist/Transcriber-LP.app/Contents/MacOS/Transcriber-LP"
    ;;
  *)
    echo "Error: Unknown architecture '$ARCH'"
    exit 1
    ;;
esac
