# Release Compliance Policy

This project separates source distribution from binary app distribution.

This document is not legal advice. It records the release policy used by this repository so that release candidates can be reviewed consistently before publication.

## Source Repository Policy

- Do not commit runtime binaries, model weights, virtual environments, PyInstaller output, caches, or local release packages.
- Keep `third_party/macos/` as local packaging input only; only `.gitkeep` is tracked.
- Keep model downloads checksum-gated in `app/core/model_manager.py`.
- Keep dependency owners, licenses, and source URLs aligned in `docs/THIRD_PARTY_NOTICE.md` and the in-app open-source notice.

## Default App Distribution Policy

- Do not bundle Whisper model weights by default.
- When no model is installed, the app prompts the user to download the Base model into the user's Application Support directory.
- Accept downloaded models only after checksum verification.
- Bundle `ffmpeg`, `ffprobe`, `whisper-cli`, and required dynamic libraries only when their exact provenance and license obligations are documented.

## Optional Bundled Model Policy

Bundling `ggml-base.bin` is opt-in and must be treated as a release decision.

To create a bundle with the Base model included:

```bash
TRANSCRIBER_LP_BUNDLE_MODEL=1 bash scripts/build_macos.sh
```

Before distributing that bundle:

- complete `docs/MODEL_PROVENANCE.md`
- include the exact model license or model-card notice in the release artifact
- document the model checksum used for the released artifact
- confirm the model redistribution terms are compatible with the intended release

## FFmpeg Policy

FFmpeg license obligations depend on the exact build. A build produced with `--enable-gpl` is treated as GPL for distribution purposes.

For a broadly redistributable non-GPL app release, use an LGPL-compatible FFmpeg build without GPL or nonfree configuration flags. If a GPL FFmpeg build is distributed, the combined distribution must satisfy GPL obligations.

## Release Artifact Checklist

Before publishing a `.app`, `.dmg`, or archive:

- include Transcriber-LP `LICENSE`
- include third-party license texts for bundled runtime components
- include FFmpeg provenance and license classification
- include model provenance only if a model is bundled
- run `python -m unittest discover tests`
- run `codesign --verify --deep --strict --verbose=2` on the exported app from a non-cloud-synced directory
- sign and notarize if the artifact is intended for public macOS distribution
