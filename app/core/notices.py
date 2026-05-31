from __future__ import annotations


THIRD_PARTY_NOTICE_TEXT = """Transcriber-LP uses only open-source third-party components.

Runtime components:
- Python: Python Software Foundation, PSF License.
- Qt / PySide6 / Shiboken: The Qt Company and the Qt Project, LGPLv3/GPLv3/commercial licensing.
- requests: Python Software Foundation / Requests maintainers; originally created by Kenneth Reitz, Apache-2.0.
- requests transitive dependencies: urllib3 contributors (MIT), certifi contributors / Mozilla CA bundle (MPL-2.0), charset-normalizer contributors (MIT), idna contributors (BSD-3-Clause).
- FFmpeg / ffmpeg / ffprobe: FFmpeg project contributors, LGPLv2.1-or-later or GPLv2-or-later depending on the build.
- whisper.cpp / whisper-cli and related ggml libraries: Georgi Gerganov and whisper.cpp contributors, MIT.
- Whisper model files: OpenAI Whisper models converted/distributed for whisper.cpp by Georgi Gerganov; downloaded at runtime by default and verified by checksum before use.

Build-only components:
- PyInstaller: PyInstaller Development Team, GPLv2-or-later with bootloader exception.
- PyInstaller transitive helpers such as altgraph, macholib, and packaging are open-source packages and must retain their notices when redistributed.

Platform and trademark notice:
- Apple, macOS, Mac, Finder, and Apple Silicon are trademarks of Apple Inc., registered in the U.S. and other countries and regions.
- References to Apple platform features are descriptive compatibility notes only. Transcriber-LP is not affiliated with, endorsed by, or sponsored by Apple Inc.
- Transcriber-LP does not bundle Apple proprietary software, SDK assets, system icons, or Apple documentation content.

Policy:
- Do not commit or distribute proprietary binaries, codecs, or model weights.
- Do not bundle model weights by default; use checksum-verified runtime downloads unless a release explicitly documents bundled model provenance.
- Do not bundle ffmpeg, whisper-cli, dynamic libraries, or model files unless the specific files are open-source, provenance is recorded, and license notices are included.
- See docs/THIRD_PARTY_NOTICE.md for source URLs and distribution guidance.
"""
