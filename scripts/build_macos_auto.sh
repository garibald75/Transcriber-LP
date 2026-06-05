#!/usr/bin/env bash
# Build for the current Mac architecture.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

MACHINE_ARCH="$(uname -m)"
exec "$ROOT/scripts/build_macos.sh" "$MACHINE_ARCH"
