# Third-Party Software Notice

Last reviewed: 2026-05-30.

Transcriber-LP is intended to use only open-source third-party software and open-source model assets. This file identifies the current owners/maintainers, licenses, and source locations for components used by the app or by the build system.

This notice is not legal advice. Before distributing a packaged app, verify the exact binaries and model files you ship.

## Runtime Components

| Component | Owner / maintainer | License | Used for | Source |
| --- | --- | --- | --- | --- |
| Python | Python Software Foundation | PSF License | Application runtime | https://www.python.org/psf/ |
| Qt | The Qt Company / Qt Project | LGPLv3 or GPLv3, with commercial option | GUI framework used through PySide6 | https://doc.qt.io/qt-6/licensing.html |
| PySide6 / Shiboken | The Qt Company / Qt Project | LGPLv3/GPLv3/commercial Qt for Python terms | Python bindings for Qt | https://wiki.qt.io/PySide |
| requests | Python Software Foundation / Requests maintainers; originally created by Kenneth Reitz | Apache-2.0 | Model downloads | https://pypi.org/project/requests/ |
| urllib3 | urllib3 contributors | MIT | Transitive dependency of requests | https://pypi.org/project/urllib3/ |
| certifi | certifi contributors; Mozilla CA certificate bundle | MPL-2.0 | TLS certificate bundle used by requests | https://pypi.org/project/certifi/ |
| charset-normalizer | charset-normalizer contributors | MIT | Transitive dependency of requests | https://pypi.org/project/charset-normalizer/ |
| idna | idna contributors | BSD-3-Clause | Transitive dependency of requests | https://pypi.org/project/idna/ |
| FFmpeg / ffmpeg / ffprobe | FFmpeg project contributors | LGPLv2.1-or-later, or GPLv2-or-later depending on build configuration | Media probing and audio extraction | https://ffmpeg.org/legal.html |
| whisper.cpp / whisper-cli | Georgi Gerganov and whisper.cpp contributors | MIT | Local speech-to-text engine | https://github.com/ggml-org/whisper.cpp |
| Whisper model files | OpenAI Whisper models, converted/distributed for whisper.cpp by Georgi Gerganov | Verify the exact model file before redistribution; OpenAI Whisper source is MIT | Local transcription model weights | https://github.com/openai/whisper and https://huggingface.co/ggerganov/whisper.cpp |

## Build-Only Components

| Component | Owner / maintainer | License | Used for | Source |
| --- | --- | --- | --- | --- |
| PyInstaller | PyInstaller Development Team | GPLv2-or-later with bootloader exception | macOS app packaging | https://pyinstaller.org/en/stable/license.html |
| altgraph | Ronald Oussoren and contributors | MIT | PyInstaller dependency | https://pypi.org/project/altgraph/ |
| macholib | Ronald Oussoren and contributors | MIT | PyInstaller dependency on macOS | https://pypi.org/project/macholib/ |
| packaging | PyPA / packaging contributors | Apache-2.0 or BSD-2-Clause | Python package metadata handling | https://pypi.org/project/packaging/ |

## Repository Distribution Policy

- Do not commit runtime binaries, model weights, `.bin` files, PyInstaller output, virtual environments, caches, or local backup files.
- Do not bundle proprietary codecs, proprietary ffmpeg builds, proprietary speech engines, or model weights whose redistribution terms are unclear.
- If distributing `ffmpeg`/`ffprobe`, include the license text for the exact build and comply with LGPL/GPL source and relinking requirements.
- If distributing `PySide6`/Qt, comply with LGPLv3 or GPLv3 obligations, including license text and user rights required by the selected license.
- If distributing model files, document the exact model source, owner, license, and conversion provenance.
- Keep this notice, README, and the in-app `Help > Open-source licenses` dialog aligned whenever dependencies change.

## Release Documentation

- Record FFmpeg binary provenance in `docs/FFMPEG_BUILD.md`.
- Record model provenance in `docs/MODEL_PROVENANCE.md`.
- Use `docs/DISTRIBUTION_CHECKLIST.md` before publishing a release artifact.
- Include `LICENSE`, this notice, and the exact third-party license texts inside distributed app bundles.
