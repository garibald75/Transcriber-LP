from PyInstaller.utils.hooks import collect_submodules
# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

root = Path.cwd()
vendor = root / "third_party" / "macos"
model_dir = vendor / "models"
version = (root / "app" / "version.py").read_text().split('APP_VERSION = "')[1].split('"')[0]


datas = [
    (str(model_dir), "vendor/models"),
    (str(root / "LICENSE"), "."),
    (str(root / "CHANGELOG.md"), "."),
    (str(root / "docs" / "THIRD_PARTY_NOTICE.md"), "docs"),
    (str(root / "docs" / "FFMPEG_BUILD.md"), "docs"),
    (str(root / "docs" / "MODEL_PROVENANCE.md"), "docs"),
    (str(root / "docs" / "DISTRIBUTION_CHECKLIST.md"), "docs"),
]


hiddenimports = ["PySide6.QtCore", "PySide6.QtGui", "PySide6.QtWidgets", "app.core.transcriber"] + collect_submodules("app") + collect_submodules("app.core")

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
    icon=None,
    bundle_identifier='com.local.transcriberlp',
    info_plist={
        'CFBundleShortVersionString': version,
        'CFBundleVersion': version,
    },
)
