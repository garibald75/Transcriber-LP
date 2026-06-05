# Test Plan

Transcriber-LP keeps a small, repeatable test suite that can run in CI and in a clean local Python environment. The goal is to catch syntax, import, command construction, model-management, export, and queue-handling regressions before packaging.

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
- Command construction tests for FFmpeg and `whisper-cli`, including explicit `-l auto` language detection and optional timestamp CSV sidecar export
- Transcriber output path tests for dotted media stems and timestamp CSV sidecars
- Model manager tests for model discovery, missing models, and checksum enforcement
- UI helper tests for batch output naming and duplicate filename handling

## Manual Smoke Tests

### Development UI

```bash
python -m app.main
```

Verify file selection, drag and drop, output format selection, timestamp sidecar selection, model selection, theme switching, `Transcribe`, `Stop`, and the Help menu.

Also verify these UI interaction states:

- `Browse file...` looks and behaves like a clickable button, including hover feedback.
- Each dropdown is readable, has enough vertical spacing, and highlights the option currently under the mouse.
- The log `Auto-scroll` checkbox shows a visible checked marker and preserves scroll position when disabled.
- The media preview loads the selected source and the transcript editor opens generated `txt`, `srt`, and `vtt` files for quick correction.
- `Save changes` shows an overwrite confirmation before writing transcript edits back to the generated file.
- Window resizing keeps the main workflow, batch queue, preview player, editor, and log usable without overlapping controls.

### Batch Import

With two or more short media files:

- use `Add files` to populate the Batch Queue
- confirm `Remove` and `Clear` update the queue without affecting files on disk
- run `Transcribe batch` with one shared output folder
- confirm queue items move through pending, running, done, and failed states as appropriate
- select a completed item and use `Retrieve output` to reload the source media and generated transcript
- test duplicate base filenames and confirm outputs receive numeric suffixes instead of overwriting each other

### macOS Bundle

Prepare local runtime inputs under `third_party/macos/`, then run:

```bash
bash scripts/build_macos.sh
open -n dist/Transcriber-LP.app
```

Verify the app opens on the target architecture and that the bundled `ffmpeg`, `ffprobe`, `whisper-cli`, and downloaded or intentionally bundled model file are usable.

### Transcription Runtime

For a packaged Apple Silicon build, confirm:

- bundled executables are `arm64`
- `whisper-cli --help` runs from inside the app bundle
- a short audio file can be converted with bundled `ffmpeg`
- `whisper-cli` can load the selected model and produce a `txt`, `srt`, or `vtt` file
- `Auto-detect` language mode passes `-l auto`; known-language audio can be forced with a language code such as `-l it`
- enabling `Save timestamps` produces a `.csv` sidecar while preserving the selected main transcript format
- batch transcription writes one output per queued source and keeps completed outputs retrievable from the queue

## Known Release Checks

- Build and notarization should be performed outside cloud-synced folders when possible.
- `codesign --verify --deep --strict --verbose=2` should pass on the final release bundle.
- Release artifacts must include exact third-party license texts and provenance records.
- Generated transcripts, subtitle files, and timestamp CSV sidecars are user data and should not be bundled into public release artifacts unless they are intentional sample files with clear provenance and consent.

## Next Test Targets

- Add subprocess-mocked tests for `app/core/transcriber.py`.
- Add model-download tests with mocked HTTP responses.
- Add a minimal smoke test script for packaged bundle validation.
- Add widget-level tests for the batch queue and transcript editor when a stable Qt test harness is available.
