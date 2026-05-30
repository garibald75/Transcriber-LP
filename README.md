#  Transcriber-LP

Offline desktop app for local video/audio transcription with a bundled engine, bundled FFmpeg, a default bundled Whisper model, and optional model updates stored outside the app bundle.

## What this project is

- Desktop UI: PySide6
- Packaging: PyInstaller
- Speech engine: `whisper.cpp` CLI
- Audio extraction: `ffmpeg`
- Default model: bundled in the app
- Updated models: stored in `Application Support/Transcriber-LP/models`
- No server required for transcription

## Current target

This repository is designed for macOS on both Intel and Apple Silicon. The source code is portable, but the provided packaging scripts focus on macOS.

## Project structure

- `app/` application code
- `scripts/` build and vendor preparation scripts
- `third_party/macos/` place built binaries here before packaging
- `build/` temporary build outputs

## Runtime binary layout expected before packaging

Put these files here:

- `third_party/macos/ffmpeg`
- `third_party/macos/ffprobe`
- `third_party/macos/whisper-cli`
- `third_party/macos/models/ggml-base.bin`

## Build whisper.cpp CLI

Example:

```bash
cd /tmp
git clone https://github.com/ggml-org/whisper.cpp.git
cd whisper.cpp
cmake -B build
cmake --build build --config Release -j
```

Then copy:

```bash
cp build/bin/whisper-cli /path/to/video_transcriber_app/third_party/macos/
```

## Get the default bundled model

The repo includes a helper script:

```bash
bash scripts/download_default_model.sh
```

It downloads `ggml-base.bin` into `third_party/macos/models/`.

## FFmpeg

Place redistributable `ffmpeg` and `ffprobe` binaries into `third_party/macos/`.

## Dev run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.main
```

## Build macOS app bundle

```bash
bash scripts/build_macos.sh
```

The output goes to `dist/Transcriber-LP.app`.

## Universal2 build note

To build a single macOS app bundle that runs on Intel and Apple Silicon, use a universal2 Python environment and universal2-compatible dependencies and binaries. The provided build script passes PyInstaller's macOS target architecture flag as `universal2`.

## Updateable models behavior

At runtime the app looks for models in this order:

1. user-downloaded models in `Application Support/Transcriber-LP/models`
2. bundled default model inside the app resources

So the app works immediately offline, but can later download a newer or larger model without rebuilding the app.

## What works in the UI

- Drag and drop video/audio files
- Choose language hint
- Choose output format (`txt`, `srt`, `vtt`)
- Choose active model
- Download additional models
- Start local transcription
- Open output folder

## Limits

- Progress is coarse because `whisper.cpp` CLI is invoked as a subprocess
- Packaging for Windows/Linux is not included in these scripts yet
- Final notarization/signing is not included
