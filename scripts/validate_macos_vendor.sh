#!/usr/bin/env bash
# Validate macOS vendor binaries before PyInstaller packaging.
set -euo pipefail

TARGET_ARCH="${1:-}"
VENDOR_DIR="${2:-}"

if [[ -z "$TARGET_ARCH" || -z "$VENDOR_DIR" ]]; then
  echo "Usage: $0 <arm64|x86_64|universal2> <vendor-dir>" >&2
  exit 2
fi

case "$TARGET_ARCH" in
  arm64|x86_64|universal2)
    ;;
  *)
    echo "Unsupported macOS target architecture: $TARGET_ARCH" >&2
    exit 2
    ;;
esac

if [[ ! -d "$VENDOR_DIR" ]]; then
  echo "Missing vendor directory: $VENDOR_DIR" >&2
  exit 1
fi

status=0

fail() {
  echo "ERROR: $*" >&2
  status=1
}

warn() {
  echo "WARN: $*" >&2
}

file_info() {
  file -L "$1" 2>/dev/null || true
}

check_arch() {
  local path="$1"
  local label="$2"
  local info

  if [[ ! -e "$path" ]]; then
    fail "Missing $label: $path"
    return
  fi

  info="$(file_info "$path")"
  if [[ "$info" != *"Mach-O"* ]]; then
    fail "$label is not a Mach-O binary or dylib: $path ($info)"
    return
  fi

  case "$TARGET_ARCH" in
    arm64)
      [[ "$info" == *"arm64"* ]] || fail "$label is not arm64: $path ($info)"
      ;;
    x86_64)
      [[ "$info" == *"x86_64"* ]] || fail "$label is not x86_64: $path ($info)"
      ;;
    universal2)
      [[ "$info" == *"arm64"* && "$info" == *"x86_64"* ]] || fail "$label is not universal2: $path ($info)"
      ;;
  esac
}

check_external_deps() {
  local path="$1"
  local dep

  command -v otool >/dev/null 2>&1 || return 0
  [[ -e "$path" ]] || return 0

  while IFS= read -r dep; do
    case "$dep" in
      ""|@*|/usr/lib/*|/System/Library/*)
        ;;
      *)
        warn "$(basename "$path") links to non-system dependency: $dep"
        ;;
    esac
  done < <(otool -L "$path" | awk 'NR > 1 {print $1}')
}

check_rpath_deps() {
  local path="$1"
  local dep
  local dylib
  local rpath
  local has_rpath_dep=0
  local has_relative_rpath=0

  command -v otool >/dev/null 2>&1 || return 0
  [[ -e "$path" ]] || return 0

  while IFS= read -r dep; do
    [[ -z "$dep" ]] && continue
    has_rpath_dep=1
    dylib="$(basename "$dep")"
    check_arch "$VENDOR_DIR/$dylib" "$dylib required by $(basename "$path")"
  done < <(otool -L "$path" | awk '/@rpath/ {print $1}')

  while IFS= read -r rpath; do
    [[ -z "$rpath" ]] && continue
    case "$rpath" in
      @executable_path*|@loader_path*)
        has_relative_rpath=1
        ;;
      /*)
        fail "$(basename "$path") has absolute LC_RPATH: $rpath"
        ;;
    esac
  done < <(otool -l "$path" | awk '/cmd LC_RPATH/ {getline; getline; sub(/^ *path /, ""); sub(/ \(offset.*$/, ""); print}')

  if [[ "$has_rpath_dep" -eq 1 && "$has_relative_rpath" -eq 0 ]]; then
    fail "$(basename "$path") uses @rpath dependencies but has no @executable_path or @loader_path LC_RPATH"
  fi
}

for required in ffmpeg ffprobe whisper-cli; do
  check_arch "$VENDOR_DIR/$required" "$required"
  check_external_deps "$VENDOR_DIR/$required"
done

if command -v find >/dev/null 2>&1; then
  while IFS= read -r dylib; do
    check_arch "$dylib" "$(basename "$dylib")"
  done < <(find "$VENDOR_DIR" -maxdepth 1 \( -type f -o -type l \) -name "*.dylib" | sort)
fi

check_rpath_deps "$VENDOR_DIR/whisper-cli"

if [[ "${TRANSCRIBER_LP_BUNDLE_MODEL:-0}" == "1" && ! -f "$VENDOR_DIR/models/ggml-base.bin" ]]; then
  fail "Missing $VENDOR_DIR/models/ggml-base.bin requested by TRANSCRIBER_LP_BUNDLE_MODEL=1"
fi

if [[ "$status" -ne 0 ]]; then
  echo "macOS vendor validation failed for target $TARGET_ARCH in $VENDOR_DIR" >&2
  exit "$status"
fi

echo "macOS vendor validation passed for $TARGET_ARCH"
