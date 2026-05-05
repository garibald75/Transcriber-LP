from __future__ import annotations

import os
import sys
from pathlib import Path

APP_NAME = "Transcriber-LP"


def app_support_dir() -> Path:
    home = Path.home()
    if sys.platform == "darwin":
        return home / "Library" / "Application Support" / APP_NAME
    if sys.platform.startswith("win"):
        base = Path(os.environ.get("APPDATA", home / "AppData" / "Roaming"))
        return base / APP_NAME
    return home / ".local" / "share" / APP_NAME


def models_dir() -> Path:
    path = app_support_dir() / "models"
    path.mkdir(parents=True, exist_ok=True)
    return path


def outputs_dir() -> Path:
    path = app_support_dir() / "outputs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def temp_dir() -> Path:
    path = app_support_dir() / "tmp"
    path.mkdir(parents=True, exist_ok=True)
    return path


def resource_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS"))
    return Path(__file__).resolve().parents[2]


def _candidate_roots() -> list[Path]:
    root = resource_root()
    return [
        root / "vendor",
        root / "third_party" / "macos",
    ]


def bundled_bin(name: str) -> Path:
    for base in _candidate_roots():
        candidate = base / name
        if candidate.exists():
            return candidate
    return _candidate_roots()[0] / name


def bundled_models_dir() -> Path:
    for base in _candidate_roots():
        candidate = base / "models"
        if candidate.exists():
            return candidate
    return _candidate_roots()[0] / "models"
