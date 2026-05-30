# Test Plan

Transcriber-LP keeps a small, repeatable test suite that can run in CI and in a clean local Python environment. The goal is to catch syntax, import, command construction, and model-management regressions before packaging.

## Automated Checks

Run the same checks locally before pushing changes:

```bash
find app -name '*.py' | sort | xargs python -m py_compile
python -m unittest discover tests
```

For checkouts inside cloud-synced folders, run `py_compile` with a temporary cache directory, for example:

```bash
find app -name '*.py' | sort | env PYTHONPYCACHEPREFIX=/private/tmp/transcriber-pycache xargs python -m py_compile
```

CI runs these checks on Python 3.9 and 3.11 using `.github/workflows/ci.yml`.

## Current Coverage

- Python syntax validation for all modules under `app/`
- Basic import coverage for core and UI modules
- Command construction tests for FFmpeg and `whisper-cli`
- Model manager tests for model discovery, missing models, and checksum enforcement

## Manual Smoke Tests

### Development UI

```bash
python -m app.main
```

Verify file selection, drag and drop, output format selection, model selection, theme switching, `Transcribe`, `Stop`, and the Help menu.

### macOS Bundle

Prepare local runtime inputs under `third_party/macos/`, then run:

```bash
bash scripts/build_macos.sh
open -n dist/Transcriber-LP.app
```

Verify the app opens on the target architecture and that the bundled `ffmpeg`, `ffprobe`, `whisper-cli`, and model file are usable.

### Transcription Runtime

For a packaged Apple Silicon build, confirm:

- bundled executables are `arm64`
- `whisper-cli --help` runs from inside the app bundle
- a short audio file can be converted with bundled `ffmpeg`
- `whisper-cli` can load the bundled model and produce a `txt`, `srt`, or `vtt` file

## Known Release Checks

- Build and notarization should be performed outside cloud-synced folders when possible.
- `codesign --verify --deep --strict --verbose=2` should pass on the final release bundle.
- Release artifacts must include exact third-party license texts and provenance records.

## Next Test Targets

- Add subprocess-mocked tests for `app/core/transcriber.py`.
- Add model-download tests with mocked HTTP responses.
- Add a minimal smoke test script for packaged bundle validation.
