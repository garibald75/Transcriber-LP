# Changelog

Transcriber-LP follows semantic versioning. The first tracked baseline starts at `0.1.0`.

## 0.4.10 - 2026-05-31

- Replaced horizontal scrolling in the model Settings list with ellipsized rows and full-name tooltips.

## 0.4.9 - 2026-05-31

- Replaced the native dropdown popup frame with a frameless custom popup list.
- Reduced the main Settings panel to the current model selector and transcription settings.
- Moved installed-model listing and model downloads into a Settings dialog.
- Added a first-run current-model placeholder that opens model downloads.

## 0.4.8 - 2026-05-31

- Restored visible dropdown popup items after removing the wrong native popup frame layer.
- Aligned Settings labels with explicit label widgets sized to the dropdown rows.

## 0.4.7 - 2026-05-31

- Restored normal closed-state borders on Settings dropdown controls.
- Removed the native frame from open dropdown popups.
- Aligned Settings form labels consistently from the left while keeping vertical centering.

## 0.4.6 - 2026-05-30

- Simplified the macOS app icon to a microphone with a compact wave mark.

## 0.4.5 - 2026-05-30

- Centered Settings form labels vertically against their controls.
- Drew dropdown chevrons directly in the combo box widget so arrows are always visible.
- Removed the popup view frame around open dropdown menus.

## 0.4.4 - 2026-05-30

- Removed the default gray border from Settings dropdowns.
- Added explicit popup mouse tracking and custom item painting so dropdown rows highlight under the pointer.

## 0.4.3 - 2026-05-30

- Fixed Settings dropdown arrows by replacing the fragile QSS triangle with a packaged chevron asset.
- Made dropdown popup hover reliable by selecting the row under the pointer.
- Improved model download button readability with a two-column layout and shorter labels.

## 0.4.2 - 2026-05-30

- Unified dropdown controls with shared atomic design tokens for height, spacing, hover, and popup item sizing.
- Improved Settings dropdown readability so model, language, format, and translation selectors are less compressed.

## 0.4.1 - 2026-05-30

- Added a gears icon to the Settings panel that now contains model management controls.

## 0.4.0 - 2026-05-30

- Moved model download controls into the Settings panel alongside model selection.

## 0.3.2 - 2026-05-30

- Added an overwrite confirmation dialog before saving edited transcript changes back to an existing file.

## 0.3.1 - 2026-05-30

- Added an export setting to save timestamp data as a CSV sidecar independent of the selected transcript format.
- Persisted the timestamp export preference in user settings.
- Updated user, test, distribution, technical review, and compliance documentation for the 0.3.1 workflow.

## 0.3.0 - 2026-05-30

- Added batch import with a queue for sequentially transcribing multiple media files.
- Added per-item batch status logging for queued, running, completed, failed, and cancelled items.
- Added batch output retrieval so completed queue items can be reopened in the transcript editor.
- Added duplicate-stem output naming for batch runs to avoid overwriting files with the same base name.

## 0.2.1 - 2026-05-30

- Improved window resize behavior so the media preview, transcript editor, log panel, and model list scale proportionally.

## 0.2.0 - 2026-05-30

- Added an in-app media preview player for checking the source audio or video during review.
- Added a quick transcript editor that opens completed `txt`, `srt`, and `vtt` outputs for correction.
- Added direct save support for corrected transcript files.
- Updated packaging metadata to include Qt multimedia modules.

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
- Documented source/community support expectations for Linux, Windows, Intel macOS, and future packaging contributions.
- Fixed source language command construction so `Auto-detect` is passed explicitly to `whisper-cli` as `-l auto`.
- Added a persistent `Auto-scroll` control for the runtime log panel, with an explicit checked marker.
- Improved dropdown hover styling and made the media browse control read more clearly as a button.
