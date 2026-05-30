# Technical Review Notes

This document summarizes the engineering decisions that are most relevant when reviewing Transcriber-LP as a portfolio project.

## Product Scope

Transcriber-LP is a local-first macOS desktop app for creating `txt`, `srt`, and `vtt` transcripts from media files. The app is intentionally scoped around offline transcription, predictable packaging, and clear handling of third-party binaries and model files.

## Architecture

- `app/ui/` contains the PySide6 desktop interface, menus, theme handling, help dialogs, and user interaction flow.
- `app/core/` contains transcription command construction, subprocess orchestration, model discovery, model downloads, and runtime paths.
- `scripts/` contains repeatable setup and packaging helpers for macOS Apple Silicon builds.
- `tests/` covers import stability, command construction, checksum behavior, and model manager edge cases.

## Reliability Choices

- Transcription runs through local command-line tools rather than a hosted API.
- Supported model downloads are checksum-gated before they are accepted by the app.
- Runtime binaries and model weights are kept out of Git history.
- CI compiles all Python files and runs unit tests on multiple Python versions.

## Packaging And Compliance

The repository separates source code from distributable runtime inputs. `ffmpeg`, `ffprobe`, `whisper-cli`, dynamic libraries, and model files must be supplied locally under `third_party/macos/` before packaging.

Release documentation is split by responsibility:

- `docs/THIRD_PARTY_NOTICE.md` records owners, licenses, and source locations.
- `docs/FFMPEG_BUILD.md` records exact FFmpeg build provenance.
- `docs/MODEL_PROVENANCE.md` records exact model artifact provenance.
- `docs/DISTRIBUTION_CHECKLIST.md` lists checks required before publishing a release artifact.

## Known Boundaries

- The current packaged target is macOS Apple Silicon.
- The repository does not publish third-party binaries or model weights.
- Public release artifacts require final license-text bundling, signing, and notarization checks.
