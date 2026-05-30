# FFmpeg Build Provenance

Transcriber-LP does not commit `ffmpeg` or `ffprobe` binaries. If you distribute a packaged app that bundles them, document the exact build here before release.

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

## Distribution Rules

- Use only open-source FFmpeg builds.
- Do not bundle proprietary codecs or non-redistributable builds.
- If the build is LGPL, preserve user relinking rights and include license notices.
- If the build is GPL, the distributed app bundle must comply with GPL obligations for the combined distribution.
- Keep the exact license text and source offer with the release artifact.

See https://ffmpeg.org/legal.html for FFmpeg's official guidance.
