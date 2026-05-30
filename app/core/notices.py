from __future__ import annotations


THIRD_PARTY_NOTICE_TEXT = """Transcriber-LP uses only open-source third-party components.

Runtime components:
- Python: Python Software Foundation, PSF License.
- Qt / PySide6 / Shiboken: The Qt Company and the Qt Project, LGPLv3/GPLv3/commercial licensing.
- requests: Python Software Foundation / Requests maintainers; originally created by Kenneth Reitz, Apache-2.0.
- requests transitive dependencies: urllib3 contributors (MIT), certifi contributors / Mozilla CA bundle (MPL-2.0), charset-normalizer contributors (MIT), idna contributors (BSD-3-Clause).
- FFmpeg / ffmpeg / ffprobe: FFmpeg project contributors, LGPLv2.1-or-later or GPLv2-or-later depending on the build.
- whisper.cpp / whisper-cli and related ggml libraries: Georgi Gerganov and whisper.cpp contributors, MIT.
- Whisper model files: OpenAI Whisper models converted/distributed for whisper.cpp by Georgi Gerganov; verify each model file's upstream license before redistribution.

Build-only components:
- PyInstaller: PyInstaller Development Team, GPLv2-or-later with bootloader exception.
- PyInstaller transitive helpers such as altgraph, macholib, and packaging are open-source packages and must retain their notices when redistributed.

Policy:
- Do not commit or distribute proprietary binaries, codecs, or model weights.
- Do not bundle ffmpeg, whisper-cli, dynamic libraries, or model files unless the specific files are open-source, provenance is recorded, and license notices are included.
- See docs/THIRD_PARTY_NOTICE.md for source URLs and distribution guidance.
"""
