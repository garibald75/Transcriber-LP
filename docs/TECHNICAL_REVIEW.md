# Technical Review Notes

This document summarizes the engineering decisions that are most relevant when reviewing Transcriber-LP as a portfolio project.

## Product Scope

Transcriber-LP is a local-first macOS desktop app for creating `txt`, `srt`, and `vtt` transcripts from media files, with optional timestamp CSV sidecars for review and downstream tooling. The app is intentionally scoped around offline transcription, batch processing, quick transcript correction, predictable packaging, and clear handling of third-party binaries and model files.

## Architecture

- `app/ui/` contains the PySide6 desktop interface, menus, responsive layout, media preview, transcript editor, batch queue, theme handling, help dialogs, and user interaction flow.
- `app/core/` contains transcription command construction, subprocess orchestration, timestamp sidecar support, model discovery, checksum-gated model downloads, and runtime paths.
- `scripts/` contains repeatable setup and packaging helpers for macOS Apple Silicon builds.
- `tests/` covers import stability, command construction, timestamp export flags, checksum behavior, model manager edge cases, and batch output naming helpers.

The UI keeps a small atomic design token layer for shared control metrics such as field height, radius, padding, dropdown width, and popup item spacing. This keeps Settings controls visually aligned across light and dark themes.

## Reliability Choices

- Transcription runs through local command-line tools rather than a hosted API.
- Batch import processes queued media sequentially, which keeps resource use predictable and makes per-item logging easier to inspect.
- The review workflow keeps the source media preview and transcript editor in the same window so a user can correct recognition errors or typos immediately after generation.
- Optional timestamp export is implemented as a sidecar output, so users can keep a human-readable transcript format while preserving segment timing separately.
- If no model is installed, the app prompts for the Base model download and accepts it only after checksum verification.
- Runtime binaries and model weights are kept out of Git history.
- CI compiles all Python files and runs unit tests on multiple Python versions.

## Packaging And Compliance

The repository separates source code from distributable runtime inputs. `ffmpeg`, `ffprobe`, `whisper-cli`, and dynamic libraries must be supplied locally under `third_party/macos/` before packaging. Model weights are not bundled by default; bundling a model is an explicit release decision controlled by `TRANSCRIBER_LP_BUNDLE_MODEL=1`.

Generated transcripts, subtitle files, and timestamp CSV sidecars are treated as user data. They are not third-party components and should not be included in public release artifacts unless they are deliberate samples with clear provenance and consent.

Release documentation is split by responsibility:

- `docs/THIRD_PARTY_NOTICE.md` records owners, licenses, and source locations.
- `docs/FFMPEG_BUILD.md` records exact FFmpeg build provenance.
- `docs/MODEL_PROVENANCE.md` records exact model artifact provenance.
- `docs/RELEASE_COMPLIANCE.md` records the release policy for binaries, models, and license texts.
- `docs/DISTRIBUTION_CHECKLIST.md` lists checks required before publishing a release artifact.

## Known Boundaries

- The current packaged target is macOS Apple Silicon.
- The repository does not publish third-party binaries or model weights.
- Public release artifacts require final license-text bundling, signing, and notarization checks.
- Linux, Windows, Intel macOS, and universal builds require platform-specific binary provenance, packaging scripts, and smoke tests before they can be treated as official release targets.
