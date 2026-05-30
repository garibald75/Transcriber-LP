# Transcriber-LP User Manual

Current version: `0.1.0`

Versioning starts at `0.1.0` for the first tracked public-ready baseline. The source of truth is `app/version.py`.

## Start the App

Run the app from a development environment with:

```bash
python -m app.main
```

For a packaged build, open `dist/Transcriber-LP.app`.

## Transcribe a File

1. Drag an audio/video file into the drop area, or use `Browse`.
2. Choose the output format: `txt`, `srt`, or `vtt`.
3. Select a model from the model list.
4. Leave source language on `Auto-detect`, or choose a known language.
5. Keep the original language, or choose `Translate to English`.
6. Click `Transcribe`.
7. Choose the output folder when prompted.

Use `Stop` to cancel a running transcription.

## Appearance

Transcriber-LP starts with the light theme by default.

Use `View > Theme > Light` or `View > Theme > Dark` to switch the interface while the app is running. The selected theme is saved in user settings and restored on the next launch.

## Models

The app looks for models in this order:

1. downloaded models in `~/Library/Application Support/Transcriber-LP/models`
2. bundled models in the app/vendor resources

The model manager can download supported `whisper.cpp` models into the user models directory.

If no model is installed, the app automatically asks whether to download the Base model. The download is saved outside the app bundle and accepted only after checksum verification.

Only models with a checksum in `app/core/model_manager.py` are enabled for in-app download. Models without a checksum must be installed manually after their provenance is verified.

## Outputs

Transcription files are saved to the folder selected when transcription starts. The default output area used by the app is:

```text
~/Library/Application Support/Transcriber-LP/outputs
```

## Packaging Requirements

Before building a macOS app bundle, provide these local files:

```text
third_party/macos/ffmpeg
third_party/macos/ffprobe
third_party/macos/whisper-cli
third_party/macos/<whisper-cli @rpath dylibs>
```

Use `otool -L third_party/macos/whisper-cli` to identify the `.dylib` files required by the local `whisper-cli` build. `scripts/build_whisper_cli.sh` copies these libraries for the default macOS build flow.

Model files are not bundled by default. If a release intentionally bundles `ggml-base.bin`, build with `TRANSCRIBER_LP_BUNDLE_MODEL=1` and complete the model provenance and license checks first.

Only distribute third-party binaries and models when their licenses allow it. Complete `docs/DISTRIBUTION_CHECKLIST.md` before publishing a release.

## Open-Source Licenses and Owners

Use `Help > Open-source licenses` inside the app to view the runtime attribution notice.

The app is intended to use only open-source components. The current third-party owners, licenses, and source URLs are documented in:

```text
docs/THIRD_PARTY_NOTICE.md
```

Before distributing a packaged app, verify the exact `ffmpeg`, `ffprobe`, `whisper-cli`, dynamic libraries, and model files you ship. Do not bundle proprietary binaries, codecs, or model weights with unclear redistribution terms.
