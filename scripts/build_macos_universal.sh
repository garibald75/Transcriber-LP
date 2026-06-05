#!/usr/bin/env bash
# Compatibility wrapper for universal2 macOS builds.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

case "${1:-universal2}" in
  arm64)
    exec "$ROOT/scripts/build_macos.sh" arm64
    ;;
  intel|x86_64)
    exec "$ROOT/scripts/build_macos.sh" x86_64
    ;;
  both|universal|universal2)
    exec "$ROOT/scripts/build_macos.sh" universal2
    ;;
  *)
    echo "Usage: $0 [arm64|x86_64|universal2]" >&2
    exit 2
    ;;
esac
