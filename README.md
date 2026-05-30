# Transcriber-LP

[![CI](https://github.com/garibald75/Transcriber-LP/actions/workflows/ci.yml/badge.svg)](https://github.com/garibald75/Transcriber-LP/actions/workflows/ci.yml)
![Version](https://img.shields.io/badge/version-0.1.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Current version: `0.1.0`

Offline desktop transcription app for macOS, built with PySide6, PyInstaller, FFmpeg, and `whisper.cpp`.

## What this project is

- Desktop UI built with PySide6.
- Local transcription through the `whisper.cpp` CLI.
- Audio extraction through `ffmpeg`.
- macOS packaging through PyInstaller.
- Optional model downloads stored in the user's Application Support directory.
- Offline-capable workflow with no server requirement.

The repository intentionally does not commit runtime binaries, model weights, virtual environments, or build products. Packaging inputs must be supplied locally under `third_party/macos/` and documented before any release artifact is distributed.

## Features

- drag & drop media input
- file browser selection
- output formats: `txt`, `srt`, `vtt`
- source language selection or auto-detect
- translate to English or keep the source language
- model manager with checksum-gated downloads
- stop/cancel for running jobs
- light/dark theme switch from `View > Theme`
- runtime help manual and open-source notice dialog
- GitHub CI for syntax and unit-test validation

## Versioning

Transcriber-LP uses semantic versioning starting at `0.1.0`.

- `0.x` releases are early public-ready builds where UI, packaging, and workflow details may still change.
- Patch releases fix bugs or documentation without changing behavior.
- Minor releases add user-visible features or packaging improvements.

The source of truth is `app/version.py`. macOS bundle metadata is read from that file during PyInstaller builds.

## Screenshot

![Transcriber-LP UI](docs/transcriber-lp-screenshot.svg)

## Appearance

The app defaults to the light theme. Use `View > Theme > Light` or `View > Theme > Dark` to switch the interface theme at runtime.

The selected theme is stored in the user settings and restored on the next launch. The theme system is palette-driven in `app/ui/main_window.py`, so new themes can be added by defining another entry in `THEME_PALETTES` and exposing it through the theme menu.

## Third-party components and licenses

- `ffmpeg` / `ffprobe`: LGPL/GPL-licensed media toolkit. Verify the upstream build license before bundling. See https://ffmpeg.org/legal.html
- `whisper.cpp` / `whisper-cli`: upstream project by Georgi Gerganov and contributors, typically licensed under MIT. See https://github.com/ggml-org/whisper.cpp
- `PySide6`: Qt for Python, licensed under LGPL. See https://doc.qt.io/qtforpython/
- `requests`: Apache License 2.0.
- Models (for example `ggml-base.bin`): may have separate licensing and distribution requirements.

This repository avoids committing binary distributions and model weights. Runtime binaries are supplied from `third_party/macos/` before packaging, and should only be added when their licenses are compatible with the distribution plan.

Transcriber-LP source code is licensed under the MIT License. See `LICENSE`.
Before publishing a packaged app, complete `docs/FFMPEG_BUILD.md`, `docs/MODEL_PROVENANCE.md`, and `docs/DISTRIBUTION_CHECKLIST.md`.

## Repository structure

- `app/` application source code
- `app/assets/` UI and icon assets (including a new SVG app icon)
- `tests/` unit tests and import checks
- `docs/USER_MANUAL.md` end-user manual
- `docs/THIRD_PARTY_NOTICE.md` open-source owners, licenses, and redistribution policy
- `docs/DISTRIBUTION_CHECKLIST.md` release readiness checklist
- `scripts/` packaging and helper scripts
- `third_party/macos/` local packaging inputs; only `.gitkeep` is tracked
- `.github/workflows/` CI pipeline

## Quick start

1. Create a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m app.main
```

## macOS Apple Silicon Build

The packaging target is Apple Silicon (`arm64`). Ensure these files are present before building:

- `third_party/macos/ffmpeg`
- `third_party/macos/ffprobe`
- `third_party/macos/whisper-cli`
- any `@rpath` `.dylib` dependencies reported by `otool -L third_party/macos/whisper-cli`
- `third_party/macos/models/ggml-base.bin`

Helper scripts:

```bash
bash scripts/build_whisper_cli.sh
bash scripts/download_default_model.sh
```

`ffmpeg` and `ffprobe` must be supplied from a license-compatible macOS arm64 build and recorded in `docs/FFMPEG_BUILD.md`.

Then run:

```bash
bash scripts/build_macos.sh
```

The application bundle is created in `dist/Transcriber-LP.app`.

If the bundle is prepared for distribution, build or export it outside cloud-synced folders such as OneDrive and run:

```bash
codesign --verify --deep --strict --verbose=2 dist/Transcriber-LP.app
```

## Intel / universal build

The current packaging is targeted for Apple Silicon (`arm64`).
For Intel support, build with a universal2 Python environment and compatible binaries, or use a separate Intel-specific build environment.

## Testing and CI

A GitHub Actions workflow is provided in `.github/workflows/ci.yml`.
The CI pipeline performs:

- checkout repository
- install Python dependencies
- compile all Python sources under `app/`
- run unit tests in `tests/`

Run tests locally with:

```bash
python -m unittest discover tests
```

For the same checks as CI, also run:

```bash
find app -name '*.py' | sort | xargs python -m py_compile
python -m unittest discover tests
```

If the checkout is inside a cloud-synced folder and Python cannot write its cache files, set `PYTHONPYCACHEPREFIX` to a local temporary directory before running `py_compile`.

## Runtime paths

- downloaded models: `~/Library/Application Support/Transcriber-LP/models`
- outputs: `~/Library/Application Support/Transcriber-LP/outputs`
- temporary files: `~/Library/Application Support/Transcriber-LP/tmp`

## Notes

- The app currently targets macOS packaging and does not include Windows/Linux installers.
- The repo is configured to keep binary artifacts out of version control.
- The UI includes light/dark themes, tooltips, and inline help.
- The app includes `Help > Open-source licenses` and `docs/THIRD_PARTY_NOTICE.md` to cite third-party owners and licenses.
- Release artifacts should include exact third-party license texts and provenance for bundled binaries and models.
