"""Autonomous Whisper engine (whisper.cpp) updates.

The app ships a bundled `whisper-cli` + dylibs as an offline fallback. When a
newer engine is published as a GitHub release of this project (built by CI from
a new whisper.cpp tag), the app can download and install it into the user's
Application Support directory and use it instead of the bundled one.

Compiling whisper.cpp on the end user's machine is not viable (no toolchain),
so "update" means: download the prebuilt, checksum-verified engine for the
current architecture. The bundled engine always remains as a fallback, so the
app keeps working offline if no update is installed.
"""
from __future__ import annotations

import hashlib
import json
import platform
import shutil
import subprocess
import tarfile
import tempfile
from pathlib import Path

import requests

from .paths import app_support_dir, bundled_bin

# GitHub repository that publishes prebuilt engine releases (built by CI).
ENGINE_REPO = "garibald75/Transcriber-LP"
# Engine releases are tagged "engine-<whisper.cpp tag>", e.g. "engine-v1.7.5".
ENGINE_TAG_PREFIX = "engine-"
# whisper.cpp version vendored in the app bundle. Keep in sync with
# scripts/build_whisper_cli.sh (WHISPER_CPP_TAG) when re-vendoring; it is the
# baseline the updater compares published releases against.
BUNDLED_ENGINE_VERSION = "v1.7.5"

_TIMEOUT = 15
_CHUNK = 1024 * 256


def current_arch() -> str:
    machine = platform.machine().lower()
    if machine in ("arm64", "aarch64"):
        return "arm64"
    return "x86_64"


def engine_root() -> Path:
    path = app_support_dir() / "engine"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _marker_path() -> Path:
    return engine_root() / "installed.json"


def _read_marker() -> dict:
    try:
        return json.loads(_marker_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _installed_dir_valid(dirname) -> bool:
    if not dirname:
        return False
    return (engine_root() / str(dirname) / "whisper-cli").exists()


def active_engine_dir() -> Path | None:
    """Directory of the installed downloaded engine, or None to use the bundle."""
    marker = _read_marker()
    dirname = marker.get("dir")
    if _installed_dir_valid(dirname):
        return engine_root() / str(dirname)
    return None


def installed_engine_version() -> str:
    """Version currently in use: the downloaded one if valid, else the bundled baseline."""
    marker = _read_marker()
    version = marker.get("engine_version")
    if version and _installed_dir_valid(marker.get("dir")):
        return str(version)
    return BUNDLED_ENGINE_VERSION


def whisper_cli_path() -> Path:
    """Path to the whisper-cli to run: downloaded engine if installed, else bundled."""
    active = active_engine_dir()
    if active is not None:
        return active / "whisper-cli"
    return bundled_bin("whisper-cli")


def engine_lib_dir() -> Path:
    """Directory holding the active whisper-cli and its dylibs (for DYLD lookup)."""
    return whisper_cli_path().parent


def parse_version(tag: str) -> tuple:
    """Turn a tag like 'v1.7.5' or 'engine-v1.7.5' into a comparable tuple."""
    text = str(tag or "").strip()
    if text.startswith(ENGINE_TAG_PREFIX):
        text = text[len(ENGINE_TAG_PREFIX):]
    text = text.lstrip("vV").split("-")[0].split("+")[0]
    parts = []
    for chunk in text.split("."):
        digits = "".join(ch for ch in chunk if ch.isdigit())
        parts.append(int(digits) if digits else 0)
    return tuple(parts) if parts else (0,)


def _version_from_tag(tag: str) -> str:
    text = str(tag or "")
    if text.startswith(ENGINE_TAG_PREFIX):
        text = text[len(ENGINE_TAG_PREFIX):]
    return text


def select_release_asset(release: dict, manifest: dict, arch: str | None = None) -> dict | None:
    """Resolve a release + manifest into download info for the given architecture.

    Returns {'version', 'tag', 'tarball_url', 'sha256'} or None if no asset matches.
    Kept pure (no network) so it can be unit-tested.
    """
    arch = arch or current_arch()
    tag = release.get("tag_name") or ""
    if not str(tag).startswith(ENGINE_TAG_PREFIX):
        return None
    assets = {a.get("name"): a for a in release.get("assets", []) if a.get("name")}
    arch_info = (manifest.get("assets") or {}).get(arch)
    if not arch_info:
        return None
    tar_asset = assets.get(arch_info.get("name"))
    if tar_asset is None:
        return None
    return {
        "version": manifest.get("engine_version") or _version_from_tag(tag),
        "tag": tag,
        "tarball_url": tar_asset.get("browser_download_url"),
        "sha256": str(arch_info.get("sha256") or "").lower(),
    }


def fetch_latest_release(timeout: int = _TIMEOUT) -> dict | None:
    """Find the newest engine release on GitHub and resolve it for this arch.

    Lists releases and picks the most recent one tagged ``engine-*`` (the repo
    also publishes app releases, so /releases/latest is not reliable here).
    """
    url = f"https://api.github.com/repos/{ENGINE_REPO}/releases?per_page=30"
    resp = requests.get(url, timeout=timeout, headers={"Accept": "application/vnd.github+json"})
    if resp.status_code != 200:
        return None
    for release in resp.json():
        if not str(release.get("tag_name", "")).startswith(ENGINE_TAG_PREFIX):
            continue
        assets = {a.get("name"): a for a in release.get("assets", []) if a.get("name")}
        manifest_asset = assets.get("manifest.json")
        if manifest_asset is None:
            continue
        manifest = requests.get(manifest_asset["browser_download_url"], timeout=timeout).json()
        resolved = select_release_asset(release, manifest)
        if resolved and resolved.get("tarball_url"):
            return resolved
    return None


def update_available(timeout: int = _TIMEOUT) -> dict | None:
    """Return release info if a newer engine is available for this arch, else None."""
    info = fetch_latest_release(timeout=timeout)
    if not info or not info.get("tarball_url"):
        return None
    if parse_version(info["version"]) > parse_version(installed_engine_version()):
        return info
    return None


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_extract(tar: tarfile.TarFile, dest: Path) -> None:
    base = dest.resolve()
    for member in tar.getmembers():
        target = (base / member.name).resolve()
        if base != target and base not in target.parents:
            raise ValueError(f"Unsafe path in engine archive: {member.name}")
    tar.extractall(base)


def _locate_engine_files(extract_dir: Path) -> Path:
    if (extract_dir / "whisper-cli").exists():
        return extract_dir
    for child in sorted(extract_dir.iterdir()):
        if child.is_dir() and (child / "whisper-cli").exists():
            return child
    raise FileNotFoundError("whisper-cli not found in engine archive")


def _post_install(dest: Path) -> None:
    cli = dest / "whisper-cli"
    if cli.exists():
        cli.chmod(cli.stat().st_mode | 0o111)
    # Strip quarantine so the freshly downloaded binary can run, matching how the
    # app bundle itself is de-quarantined after install.
    try:
        subprocess.run(
            ["xattr", "-dr", "com.apple.quarantine", str(dest)],
            check=False,
            capture_output=True,
        )
    except Exception:
        pass


def download_and_install(info: dict, progress_cb=None, timeout: int = _TIMEOUT) -> str:
    """Download, verify, and install the engine described by ``info``.

    Returns the installed version string. Raises on network or checksum errors.
    """
    version = str(info["version"])
    url = info["tarball_url"]
    expected = str(info.get("sha256") or "").lower()

    tmp_dir = Path(tempfile.mkdtemp(prefix="tlp-engine-"))
    try:
        tar_path = tmp_dir / "engine.tar.gz"
        with requests.get(url, stream=True, timeout=timeout) as resp:
            resp.raise_for_status()
            total = int(resp.headers.get("Content-Length", 0) or 0)
            done = 0
            with tar_path.open("wb") as out:
                for chunk in resp.iter_content(chunk_size=_CHUNK):
                    if not chunk:
                        continue
                    out.write(chunk)
                    done += len(chunk)
                    if progress_cb:
                        progress_cb(done, total)

        if expected:
            actual = _sha256_file(tar_path).lower()
            if actual != expected:
                raise ValueError(
                    f"Engine checksum mismatch: expected {expected}, got {actual}"
                )

        extract_dir = tmp_dir / "extract"
        extract_dir.mkdir()
        with tarfile.open(tar_path, "r:gz") as tar:
            _safe_extract(tar, extract_dir)
        src = _locate_engine_files(extract_dir)

        dest = engine_root() / version
        if dest.exists():
            shutil.rmtree(dest, ignore_errors=True)
        shutil.move(str(src), str(dest))
        _post_install(dest)

        _marker_path().write_text(
            json.dumps({"engine_version": version, "dir": version}),
            encoding="utf-8",
        )
        return version
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
