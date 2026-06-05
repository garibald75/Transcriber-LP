#!/usr/bin/env bash
# Compatibility wrapper for Intel x86_64 macOS builds.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec "$ROOT/scripts/build_macos.sh" x86_64
