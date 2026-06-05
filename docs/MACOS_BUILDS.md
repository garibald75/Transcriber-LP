# macOS Build Targets

Transcriber-LP can be packaged for different macOS architectures by selecting a target at build time. The repository does not commit runtime binaries, model weights, virtual environments, or build products.

## Targets

- `arm64`: Apple Silicon Macs
- `x86_64`: Intel Macs
- `universal2`: one app bundle containing both Apple Silicon and Intel slices

Use one command:

```bash
bash scripts/build_macos.sh arm64
bash scripts/build_macos.sh x86_64
bash scripts/build_macos.sh universal2
```

The output is always:

```text
dist/Transcriber-LP.app
```

## Vendor Inputs

Put target-specific inputs in the matching local directory:

```text
third_party/macos/arm64/
third_party/macos/x86_64/
third_party/macos/universal2/
```

Each directory must contain:

```text
ffmpeg
ffprobe
whisper-cli
*.dylib required by whisper-cli
```

The flat `third_party/macos/` directory is still accepted for local one-target builds, but target directories are preferred. They prevent accidental mixes such as an Intel `whisper-cli` with ARM64 `libwhisper` libraries.

To use a different local vendor directory:

```bash
TRANSCRIBER_LP_VENDOR_DIR=/path/to/vendor bash scripts/build_macos.sh arm64
```

## Validation

`scripts/build_macos.sh` runs `scripts/validate_macos_vendor.sh` before PyInstaller. The validator checks:

- required binaries exist
- `ffmpeg`, `ffprobe`, `whisper-cli`, and bundled `.dylib` files match the selected architecture
- `whisper-cli` has its `@rpath` dependencies present in the selected vendor directory
- `whisper-cli` does not rely on absolute build-machine `LC_RPATH` entries
- optional bundled model input exists when `TRANSCRIBER_LP_BUNDLE_MODEL=1`

Run validation directly with:

```bash
bash scripts/validate_macos_vendor.sh arm64 third_party/macos/arm64
bash scripts/validate_macos_vendor.sh x86_64 third_party/macos/x86_64
bash scripts/validate_macos_vendor.sh universal2 third_party/macos/universal2
```

Warnings about non-system FFmpeg dependencies mean the bundle may work only on machines with the same local libraries installed. For distributable packages, use self-contained or properly bundled FFmpeg builds and document provenance in `docs/FFMPEG_BUILD.md`.

## Universal2

`universal2` is not created by combining only the PyInstaller launcher. A valid universal2 app needs compatible universal2 inputs across the whole bundle:

- a Python/PyInstaller environment capable of producing universal2 macOS executables
- PySide6/Qt components compatible with universal2 packaging
- universal2 `ffmpeg`, `ffprobe`, `whisper-cli`, and required `.dylib` files

If only separate `arm64` and `x86_64` third-party binaries are available, build and distribute separate app bundles instead of creating a partial universal app.

## Compatibility Wrappers

These wrappers remain available for older instructions:

```bash
bash scripts/build_macos_auto.sh
bash scripts/build_macos_intel.sh
bash scripts/build_macos_universal.sh
```

- `build_macos_auto.sh` builds for the current Mac architecture.
- `build_macos_intel.sh` calls `build_macos.sh x86_64`.
- `build_macos_universal.sh` calls `build_macos.sh universal2` by default.

## Bundled Model

The default bundle does not include model weights. To bundle `ggml-base.bin`, place it under the selected vendor directory:

```text
third_party/macos/arm64/models/ggml-base.bin
```

Then run:

```bash
TRANSCRIBER_LP_BUNDLE_MODEL=1 bash scripts/build_macos.sh arm64
```

Only bundle model weights after completing `docs/MODEL_PROVENANCE.md` and including required license/provenance notices in the release artifact.

## Smoke Checks

After building:

```bash
file dist/Transcriber-LP.app/Contents/MacOS/Transcriber-LP
codesign --verify --deep --strict --verbose=2 dist/Transcriber-LP.app
```

Then run the app on the target architecture and verify:

- media import
- FFmpeg conversion
- whisper transcription
- output save/open workflow
