# Changelog

Transcriber-LP follows semantic versioning. The first tracked baseline starts at `0.1.0`.

## 0.1.0 - 2026-05-30

- Added the first public-ready repository baseline.
- Added PySide6 desktop UI with drag and drop, model selection, language controls, stop/cancel, progress, logs, tooltips, and help dialogs.
- Added local transcription flow using bundled `ffmpeg` and `whisper-cli` paths.
- Added CPU-safe `whisper-cli` command construction for packaged runtime smoke tests.
- Added model discovery and download support.
- Added open-source attribution notices in documentation and in-app help.
- Added GitHub landing screenshot, user manual, test plan, unit tests, and CI workflow.
- Added macOS PyInstaller packaging metadata and runtime-library checks.
- Added release-readiness documentation for third-party binary and model provenance.
- Added technical review notes for portfolio and interview review.
- Added automatic checksum-gated Base model download prompt when no model is installed.
- Made bundled model weights opt-in for macOS packages via `TRANSCRIBER_LP_BUNDLE_MODEL=1`.
- Added release compliance policy for binaries, model weights, and license-text obligations.
- Fixed source language command construction so `Auto-detect` is passed explicitly to `whisper-cli` as `-l auto`.
