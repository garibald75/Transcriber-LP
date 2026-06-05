# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for Intel x86_64 macOS builds

import os
from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules

root = Path.cwd()
vendor = root / "third_party" / "macos"
model_dir = vendor / "models"
version = (root / "app" / "version.py").read_text().split('APP_VERSION = "')[1].split('"')[0]
bundle_model = os.environ.get("TRANSCRIBER_LP_BUNDLE_MODEL") == "1"


datas = [
    (str(vendor / "ffmpeg"), "vendor"),
    (str(vendor / "ffprobe"), "vendor"),
    (str(vendor / "whisper-cli"), "vendor"),
    (str(root / "LICENSE"), "."),
    (str(root / "CHANGELOG.md"), "."),
    (str(root / "docs" / "THIRD_PARTY_NOTICE.md"), "docs"),
    (str(root / "docs" / "FFMPEG_BUILD.md"), "docs"),
    (str(root / "docs" / "MODEL_PROVENANCE.md"), "docs"),
    (str(root / "docs" / "DISTRIBUTION_CHECKLIST.md"), "docs"),
]

datas.extend((str(path), "vendor") for path in sorted(vendor.glob("*.dylib")))

if bundle_model:
    base_model = model_dir / "ggml-base.bin"
    if not base_model.exists():
        raise FileNotFoundError(f"Missing bundled model requested by TRANSCRIBER_LP_BUNDLE_MODEL=1: {base_model}")
    datas.append((str(base_model), "vendor/models"))


hiddenimports = [
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
    "PySide6.QtMultimedia",
    "PySide6.QtMultimediaWidgets",
    "app.core.transcriber",
] + collect_submodules("app") + collect_submodules("app.core")

a = Analysis(
    ['app/main.py'],
    pathex=[str(root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Transcriber-LP',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    target_arch='x86_64',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='Transcriber-LP',
)

app = BUNDLE(
    coll,
    name='Transcriber-LP.app',
    icon=str(root / "app" / "assets" / "transcriber_icon.icns"),
    bundle_identifier='com.local.transcriberlp',
    info_plist={
        'CFBundleShortVersionString': version,
        'CFBundleVersion': version,
    },
)
