#!/usr/bin/env bash
# Automatic macOS build - detects architecture and available binaries
# Can build ARM64-only, Intel-only, or universal based on what's available
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# Detect current machine architecture
MACHINE_ARCH="$(uname -m)"
echo "🔍 Machine architecture: $MACHINE_ARCH"

# Determine what binaries are available
ARM64_AVAILABLE=true
INTEL_AVAILABLE=true

# Check for common architecture indicators in binaries
if command -v file >/dev/null 2>&1 && [[ -f "third_party/macos/whisper-cli" ]]; then
  FILE_OUTPUT="$(file third_party/macos/whisper-cli)"
  
  if [[ ! "$FILE_OUTPUT" =~ "arm64" ]]; then
    ARM64_AVAILABLE=false
  fi
  if [[ ! "$FILE_OUTPUT" =~ "x86_64" ]]; then
    INTEL_AVAILABLE=false
  fi
else
  # If we can't verify, assume we have binaries for the current machine
  ARM64_AVAILABLE=false
  INTEL_AVAILABLE=false
  
  if [[ "$MACHINE_ARCH" == "arm64" ]]; then
    ARM64_AVAILABLE=true
  else
    INTEL_AVAILABLE=true
  fi
fi

echo ""
echo "📦 Binary availability:"
echo "   ARM64 (Apple Silicon):  $([ "$ARM64_AVAILABLE" = true ] && echo "✓ available" || echo "✗ not found")"
echo "   Intel x86_64:           $([ "$INTEL_AVAILABLE" = true ] && echo "✓ available" || echo "✗ not found")"
echo ""

# Determine build strategy
if [[ "$ARM64_AVAILABLE" == true && "$INTEL_AVAILABLE" == true ]]; then
  echo "🚀 Strategy: Building UNIVERSAL (ARM64 + Intel x86_64)"
  echo ""
  bash "$ROOT/scripts/build_macos_universal.sh" both
  
elif [[ "$ARM64_AVAILABLE" == true ]]; then
  echo "🚀 Strategy: Building ARM64 only (Apple Silicon)"
  echo ""
  bash "$ROOT/scripts/build_macos.sh"
  
elif [[ "$INTEL_AVAILABLE" == true ]]; then
  echo "🚀 Strategy: Building Intel only (x86_64)"
  echo ""
  bash "$ROOT/scripts/build_macos_intel.sh"
  
else
  echo "❌ Error: No compatible binaries found in third_party/macos/"
  echo ""
  echo "Required files (for your platform):"
  if [[ "$MACHINE_ARCH" == "arm64" ]]; then
    echo "  • third_party/macos/ffmpeg (ARM64)"
    echo "  • third_party/macos/ffprobe (ARM64)"
    echo "  • third_party/macos/whisper-cli (ARM64)"
  else
    echo "  • third_party/macos/ffmpeg (Intel x86_64)"
    echo "  • third_party/macos/ffprobe (Intel x86_64)"
    echo "  • third_party/macos/whisper-cli (Intel x86_64)"
  fi
  echo ""
  echo "See README.md for binary setup instructions."
  exit 1
fi

echo ""
echo "✅ Build complete!"
