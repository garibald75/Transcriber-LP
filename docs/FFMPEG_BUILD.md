# FFmpeg Build Provenance

Transcriber-LP does not commit `ffmpeg` or `ffprobe` binaries. If a packaged app bundles them, document the exact build here before release.

## Required Release Information

- Binary provider:
- FFmpeg version:
- Download URL or source repository:
- Build date:
- Target architecture:
- Configure flags:
- Enabled external libraries/codecs:
- License classification: LGPL or GPL
- Corresponding source URL:
- License text included in bundle: yes/no

## Current Local Smoke-Test Build

These binaries are not committed to the repository. They were used only to validate a local macOS Apple Silicon package.

- Binary provider: Martin Riedl's FFmpeg Build Server
- FFmpeg / FFprobe version: 8.1.1-https://www.martin-riedl.de
- Download URLs:
  - https://ffmpeg.martin-riedl.de/redirect/latest/macos/arm64/release/ffmpeg.zip
  - https://ffmpeg.martin-riedl.de/redirect/latest/macos/arm64/release/ffprobe.zip
- Build date: upstream page reports 14 May 2026 for macOS Apple Silicon release builds
- Target architecture: macOS Apple Silicon arm64
- SHA-256:
  - ffmpeg: `ef4fe121377039053b0d7bed4a9aa46e7912918f5ba6424a1dd155f4eed625b0`
  - ffprobe: `3ec76ddd72068162294249465c36257d6c1add564f9b078e31e173837832967d`
- Configure flags: includes `--enable-gpl`, `--enable-openssl`, `--enable-libx264`, `--enable-libx265`, `--enable-libmp3lame`, and other external libraries reported by `ffmpeg -version`
- License classification: GPL build because `--enable-gpl` is present
- Corresponding source URL: https://ffmpeg.org/download.html and the provider's build-script link from https://ffmpeg.martin-riedl.de/
- License text included in bundle: no, local smoke-test only

## Distribution Rules

- Use only open-source FFmpeg builds.
- Do not bundle proprietary codecs or non-redistributable builds.
- If the build is LGPL, preserve user relinking rights and include license notices.
- If the build is GPL, the distributed app bundle must comply with GPL obligations for the combined distribution.
- Keep the exact license text and source offer with the release artifact.
- For a portfolio/interview source repository, do not commit these binaries. For a public packaged release, either use a license-compatible FFmpeg build and include exact notices, or publish the combined distribution under GPL-compatible terms.

See https://ffmpeg.org/legal.html for FFmpeg's official guidance.
