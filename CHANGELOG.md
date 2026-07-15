# Changelog

Transcriber-LP follows semantic versioning. The first tracked baseline starts at `0.1.0`.

## 0.8.2 - 2026-07-15

- Added an "Open output folder" button to the completion dialogs (single file and queue) that opens the folder containing the generated transcripts.
- Styled all message dialogs (completion, confirmations, prompts, errors) with the app theme — themed background and text in both light and dark mode — and widened dialog buttons so longer labels such as "Open output folder" are no longer clipped.

## 0.8.1 - 2026-07-15

- Fixed queue drag-and-drop removing the dragged row: the drop was accepted as a MoveAction, so Qt deleted the source row after the reorder had already been applied. The drop is now accepted as a copy and the reorder runs after the drag machinery unwinds, so rows are only ever repositioned.

## 0.8.0 - 2026-07-15

- Added manual queue reordering: drag rows to a new position, use the new up/down arrow buttons next to Remove, or right-click → "Sposta su" / "Sposta giù". Manual reordering replaces any active column sort and is disabled while a transcription is running.
- Renamed the single-file button to "Transcribe selected" whenever a queue row is selected, to make clear it transcribes only that file while "Transcribe queue" still processes every pending file.
- Added a "Reset" button that starts a new session: it empties the queue, unloads the media preview, clears the transcript editor and resets the progress bar (after confirmation; output files already saved on disk are untouched).

## 0.7.2 - 2026-06-24

- Removed the standalone file-path card under the "Add or Drop files here" button and gave the recovered space to the Queue. The selected file's full path is still available via the row tooltip (hover) and a new right-click → "Informazioni file" context menu on the queue, which shows name, full path, status, date, size, and (when present) output name and error.

## 0.7.1 - 2026-06-24

- Logged a closing line for the automatic engine/model update checks ("up to date" or "update available …") so the log no longer appears stuck on "Checking…".

## 0.7.0 - 2026-06-23

- Added checksum-verified model updates: the app reads a maintainer-controlled `models-manifest.json` (kept in sync with HuggingFace by CI), checks at startup and on demand whether an installed model has a newer published checksum, asks for consent, then re-downloads and verifies it. Downloads are now verified against SHA-256 when the manifest provides it, and the verified checksum is recorded so update checks are cheap (no re-hashing of multi-GB files).
- Added a `models-manifest.yml` CI workflow that refreshes model checksums from the HuggingFace API (no model downloads).
- Clarified the "macOS security & permissions" dialog to state that normally nothing needs changing.

## 0.6.0 - 2026-06-23

- Added autonomous Whisper engine updates: the app checks GitHub at startup (and on demand via Settings) for a newer prebuilt `whisper.cpp` engine, asks the user for consent, then downloads, checksum-verifies, and installs it into Application Support. The bundled engine stays as an offline fallback, so nothing breaks without an update.
- Added a "macOS security & permissions" help dialog (Help menu, and offered after an engine update) with step-by-step instructions and a button that opens System Settings → Privacy & Security, for allowing the app/engine and granting file access.
- Pinned `whisper.cpp` to a tag in `scripts/build_whisper_cli.sh` for reproducible builds, and added a CI workflow that builds and publishes `engine-<tag>` releases when a new upstream version ships.

## 0.5.1 - 2026-06-23

- Ordered multi-file drag-and-drop by file date (oldest to newest) so dropped files enter the queue chronologically.
- Turned the queue into a sortable table with File, Date, and Status columns; click a header to sort the queue (disabled while a transcription is running).
- Made the entire left panel a drop target instead of a small drop bar, with a highlighted overlay that fades in while files are dragged over it.
- Renamed the file button to "Add or Drop files here", let it add several files at once, and removed the now-redundant "Add files" queue button.
- Fixed the output-folder picker: it now uses the native macOS panel without `ShowDirsOnly` (which greyed out folders on recent macOS), so folders — including cloud / File-Provider folders such as kDrive and OneDrive — are listed and selectable, and the last chosen output folder is remembered between runs.

## 0.5.0 - 2026-06-22

- Unified single-file and batch transcription into one Queue: every file loaded via drag-and-drop, Browse, or Add files now joins the queue and stays there after transcribing.
- Replaced the textual `[status]` prefix with status glyphs — ○ queued, ▶ running, ✓ done, ✗ failed — so completed files keep a checkmark instead of disappearing.
- Showed queue progress as `X / Y` on the progress bar with a "Transcribing N/total: file" status line so it is clear what is running and which files are done.
- Made "Transcribe queue" skip files that are already done instead of re-running the whole queue.
- Added icon-only Clear done (removes completed items) and Clear all (empties the queue) buttons with tooltips.
- Fixed combo-box popups (including Source language) being clipped off-screen by clamping their height and flipping them above the control when there is not enough room below.
- Trimmed the stacked minimum heights (drop zone, queue list, media preview, editor, log) and tightened Settings spacing so the main window fits within a full-HD (1080p) height instead of forcing a ~1040px minimum.

## 0.4.19 - 2026-06-06

- Added a first-run missing-model prompt that offers to download the checksum-verified Base model or open model downloads in Settings.
- Kept packaged builds model-free by default while guiding users to runtime model downloads.

## 0.4.18 - 2026-06-05

- Changed timestamped `txt` exports to include segment timecodes in the main transcript file.
- Renamed the timestamp setting to clarify that `srt` and `vtt` already include timecodes while a CSV sidecar is still saved for timing data.

## 0.4.17 - 2026-06-05

- Fixed output verification for media filenames whose stems contain dotted suffixes such as `.H264`.
- Added transcriber output path tests for dotted stems and timestamp CSV sidecars.

## 0.4.16 - 2026-05-31

- Fixed action-button disabled styling so unavailable primary, danger, and secondary actions no longer appear active.
- Scoped action-button hover and pressed states to enabled buttons only.

## 0.4.15 - 2026-05-31

- Changed macOS icon generation to render SVG assets with a transparent Qt image so Dock icons keep alpha edges instead of a white square background.

## 0.4.14 - 2026-05-31

- Centralized UI action-state handling so buttons enable only when their workflow action is relevant.
- Restricted the main Stop button to active single-file or batch transcription jobs.
- Restored visible hover treatment for secondary action buttons.

## 0.4.13 - 2026-05-31

- Removed the subtitle under the app title to reclaim vertical space.
- Increased the initial Media Preview height in the review splitter.

## 0.4.12 - 2026-05-31

- Added checkmarks for current dropdown items without treating them as hover-selected.
- Aligned the timestamp export checkbox row with the Settings control rhythm.

## 0.4.11 - 2026-05-31

- Reworked Settings dropdown structure with labels above fields and attached frameless dropdown menus.
- Added an open-state chevron direction for custom dropdown controls.

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
