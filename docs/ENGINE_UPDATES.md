# Whisper Engine Updates

This document explains how Transcriber-LP keeps its transcription engine
(`whisper.cpp`) up to date: what the app does, what the CI workflow does, and
the practical limits to be aware of.

## Why this exists

The engine (`whisper-cli` + its `ggml`/`whisper` dynamic libraries) is a
**compiled** program. Building it requires a developer toolchain (CMake, a C/C++
compiler, the Metal toolchain) that end users normally do not have, so it cannot
be compiled on the user's Mac. Something must compile it ahead of time and make
the ready-to-run binary available.

That "something" is the **engine-release CI workflow**. The app then downloads
the prebuilt engine at runtime, with the user's consent.

Analogy: `whisper.cpp` publishes the *recipe* (source). The CI workflow is an
automatic *bakery* that bakes the bread (compiles) and puts it on a *shelf*
(GitHub Releases) with a tamper seal (checksum). The app is the *customer* that
checks the shelf and, with your permission, takes the freshest loaf.

## App side (what the user sees)

1. Shortly after launch — and any time via **Settings > Check for Whisper engine
   updates...** — the app checks GitHub for a newer engine release.
2. If a newer engine exists, the app explains that updating downloads the
   required components and **asks for consent**.
3. On **Update now**, the app autonomously downloads the engine, verifies its
   SHA-256 checksum, and installs it under
   `~/Library/Application Support/Transcriber-LP/engine/<version>/`. The next
   transcription uses it.
4. On **Later**, nothing changes — the current engine is kept.

The engine bundled inside the `.app` always remains as an **offline fallback**,
so the app works on first run and without internet even if no update is ever
installed. Models and transcripts are never touched by an engine update.

Implementation: [`app/core/engine_manager.py`](../app/core/engine_manager.py)
resolves which `whisper-cli` to run (downloaded engine if present and valid,
else bundled) and performs the download/verify/install;
[`app/ui/main_window.py`](../app/ui/main_window.py) handles the startup check,
the consent prompt, and the progress UI.

### macOS security & permissions

The app and the downloaded engine are not signed by an identified Apple
developer, so macOS may block them the first time. The app ships a
**Help > macOS security & permissions...** dialog with step-by-step instructions
and a button that opens **System Settings > Privacy & Security**, where the user
clicks **Open Anyway** to allow the app/engine (and, if needed, grants access to
protected or cloud folders).

## CI side (what produces the releases)

The workflow [`.github/workflows/engine-release.yml`](../.github/workflows/engine-release.yml)
runs on a macOS runner and:

1. Resolves the target `whisper.cpp` tag (the manual input, or upstream's latest
   release if no input is given).
2. Skips the build if an `engine-<tag>` release already exists (for scheduled
   runs), so it never rebuilds the same version.
3. Clones and builds `whisper.cpp` at that tag.
4. Assembles `whisper-cli` + its dylibs, packages a `tar.gz`, computes a
   SHA-256, and writes a `manifest.json`.
5. Publishes a GitHub release tagged `engine-<tag>` with those assets.

The app lists the repository's releases, picks the newest one tagged `engine-*`,
reads its `manifest.json` to find the asset and checksum for the current
architecture, and compares the version against the installed/bundled one.

### Running it

- **Automatically**: weekly (Mondays 06:00 UTC). Each run tracks upstream's
  latest release and publishes it if it is not already on the shelf.
- **Manually**: GitHub repo > **Actions** > **Build Whisper engine release** >
  **Run workflow**. Leave the tag blank for upstream latest, or pin a specific
  `whisper.cpp` tag (e.g. `v1.7.5`).

## Practical limits

- **Not instant.** Scheduled runs are weekly, so a new upstream release can take
  up to ~7 days to appear. Use **Run workflow** to publish one immediately.
- **GitHub pauses cron on inactive repos.** If the repository has no activity for
  60 days, scheduled workflows are paused until the next push/activity. This is a
  GitHub policy.
- **Latest stable, arm64 only.** The workflow builds upstream's latest *stable*
  release (not pre-releases) for Apple Silicon. Intel (x86_64) is not produced
  unless the workflow is extended.
- **A failed build publishes nothing.** If upstream changes its build layout the
  run may fail; you will see a red run under Actions and no new release is
  created.

## Maintainer tasks

- **Keep the bundled baseline in sync.** `BUNDLED_ENGINE_VERSION` in
  [`app/core/engine_manager.py`](../app/core/engine_manager.py) and
  `WHISPER_CPP_TAG` in
  [`scripts/build_whisper_cli.sh`](../scripts/build_whisper_cli.sh) describe the
  engine baked into the app bundle. Set both to the real `whisper.cpp` tag you
  vendor, and bump them together when you re-vendor the bundled engine.
- **The bundled fallback does not auto-update.** The workflow keeps the
  *downloadable* engine current; the version baked into the `.app` only changes
  when you rebuild the app with an updated pin. Raising the bundled baseline is a
  manual release step.
- **Signing/notarization.** Downloaded binaries are not notarized, so users may
  need the macOS security dialog above. A full notarized distribution would
  require an Apple Developer ID and a signing/notarization step in the build.
