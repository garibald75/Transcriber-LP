from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import requests

from .paths import bundled_models_dir, models_dir

# Maintainer-controlled catalog of models + checksums, kept up to date by CI from
# HuggingFace. The app reads it at runtime to learn about new/updated models and
# verifies every download against its checksum. The built-in MODEL_DEFS below is
# the offline fallback when the manifest can't be fetched.
MODELS_MANIFEST_URL = (
    "https://raw.githubusercontent.com/garibald75/Transcriber-LP/main/models-manifest.json"
)


@dataclass(frozen=True)
class ModelDefinition:
    key: str
    filename: str
    label: str
    size_label: str
    multilingual: bool
    sha1: str
    sha256: str = ""

    @property
    def url(self) -> str:
        return f"https://huggingface.co/ggerganov/whisper.cpp/resolve/main/{self.filename}?download=true"


MODEL_DEFS = {
    "base": ModelDefinition(
        key="base",
        filename="ggml-base.bin",
        label="Base",
        size_label="142 MiB",
        multilingual=True,
        sha1="465707469ff3a37a2b9b8d8f89f2f99de7299dac",
    ),
    "small": ModelDefinition(
        key="small",
        filename="ggml-small.bin",
        label="Small",
        size_label="466 MiB",
        multilingual=True,
        sha1="55356645c2b361a969dfd0ef2c5a50d530afd8d5",
    ),
    "medium": ModelDefinition(
        key="medium",
        filename="ggml-medium.bin",
        label="Medium",
        size_label="1.5 GiB",
        multilingual=True,
        sha1="fd9727b6e1217c2f614f9b698455c4ffd82463b4",
    ),
    "large-v3": ModelDefinition(
        key="large-v3",
        filename="ggml-large-v3.bin",
        label="Large v3",
        size_label="2.9 GiB",
        multilingual=True,
        sha1="",
    ),
    "large-v3-turbo-q5_0": ModelDefinition(
        key="large-v3-turbo-q5_0",
        filename="ggml-large-v3-turbo-q5_0.bin",
        label="Large v3 Turbo Q5",
        size_label="547 MiB",
        multilingual=True,
        sha1="e050f7970618a659205450ad97eb95a18d69c9ee",
    ),
}

DEFAULT_DOWNLOAD_MODEL_KEY = "base"


def parse_manifest(data: dict) -> dict[str, ModelDefinition]:
    """Turn a models-manifest.json payload into {key: ModelDefinition}.

    Pure (no network) so it can be unit-tested. Entries without a checksum are
    ignored, since downloads must be checksum-verified.
    """
    catalog: dict[str, ModelDefinition] = {}
    for entry in (data or {}).get("models", []):
        key = entry.get("key")
        filename = entry.get("filename")
        sha256 = str(entry.get("sha256") or "")
        if not key or not filename or not sha256:
            continue
        catalog[key] = ModelDefinition(
            key=key,
            filename=filename,
            label=entry.get("label") or key,
            size_label=entry.get("size_label") or "",
            multilingual=bool(entry.get("multilingual", True)),
            sha1=str(entry.get("sha1") or ""),
            sha256=sha256,
        )
    return catalog


def fetch_remote_catalog(timeout: int = 15) -> dict[str, ModelDefinition]:
    """Fetch the model manifest. Returns {} on any failure (never raises)."""
    try:
        resp = requests.get(MODELS_MANIFEST_URL, timeout=timeout)
        if resp.status_code != 200:
            return {}
        return parse_manifest(resp.json())
    except Exception:
        return {}


class ModelManager:
    def __init__(self, user_models_dir: Path | None = None, bundled_dir: Path | None = None) -> None:
        self.user_models_dir = user_models_dir if user_models_dir is not None else models_dir()
        self.bundled_dir = bundled_dir if bundled_dir is not None else bundled_models_dir()

    def available_models(self) -> list[tuple[str, Path, str]]:
        available: list[tuple[str, Path, str]] = []
        seen: set[str] = set()

        available.extend(self._collect_preferred_models(seen))
        available.extend(self._collect_custom_models(seen))
        return available

    def has_models(self) -> bool:
        return bool(self.available_models())

    def default_download_model(self) -> ModelDefinition:
        return MODEL_DEFS[DEFAULT_DOWNLOAD_MODEL_KEY]

    def _collect_preferred_models(self, seen: set[str]) -> list[tuple[str, Path, str]]:
        results: list[tuple[str, Path, str]] = []
        preferred_order = ["medium", "large-v3", "base", "small", "large-v3-turbo-q5_0"]
        for key in preferred_order:
            if key not in MODEL_DEFS:
                continue
            result = self._resolve_model_path(key)
            if result:
                path, source = result
                results.append((key, path, source))
                seen.add(key)
        return results

    def _collect_custom_models(self, seen: set[str]) -> list[tuple[str, Path, str]]:
        results: list[tuple[str, Path, str]] = []
        for folder, source in ((self.user_models_dir, "downloaded"), (self.bundled_dir, "bundled")):
            if not folder.exists():
                continue
            for path in sorted(folder.glob("ggml-*.bin")):
                key = path.name.removeprefix("ggml-").removesuffix(".bin")
                if key not in seen:
                    results.append((key, path, source))
                    seen.add(key)
        return results

    def _resolve_model_path(self, model_key: str) -> tuple[Path, str] | None:
        if model_key not in MODEL_DEFS:
            return None
        model = MODEL_DEFS[model_key]
        user_path = self.user_models_dir / model.filename
        bundled_path = self.bundled_dir / model.filename
        if user_path.exists():
            return user_path, "downloaded"
        if bundled_path.exists():
            return bundled_path, "bundled"
        return None

    def resolve_model_path(self, model_key: str) -> Path:
        if model_key in MODEL_DEFS:
            model = MODEL_DEFS[model_key]
            user_path = self.user_models_dir / model.filename
            bundled_path = self.bundled_dir / model.filename
            if user_path.exists():
                return user_path
            if bundled_path.exists():
                return bundled_path
            raise FileNotFoundError(f"Model not found: {model_key}")

        for folder in (self.user_models_dir, self.bundled_dir):
            candidate = folder / f"ggml-{model_key}.bin"
            if candidate.exists():
                return candidate

        raise FileNotFoundError(f"Model not found: {model_key}")

    def download_model(self, model_key: str, progress_cb=None, definition: ModelDefinition | None = None) -> Path:
        # ``definition`` lets the update flow pass a fresh manifest entry (with an
        # updated checksum); normal downloads fall back to the built-in catalog.
        model = definition or MODEL_DEFS.get(model_key)
        if model is None:
            raise ValueError(f"Unsupported model: {model_key}")
        if not (model.sha256 or model.sha1):
            raise ValueError(f"Model download is not enabled without a checksum: {model.filename}")

        target = self.user_models_dir / model.filename
        temp = target.with_suffix(".part")

        with requests.get(model.url, stream=True, timeout=30) as response:
            response.raise_for_status()
            total = int(response.headers.get("Content-Length", "0") or 0)
            downloaded = 0
            with open(temp, "wb") as fh:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if not chunk:
                        continue
                    fh.write(chunk)
                    downloaded += len(chunk)
                    if progress_cb:
                        progress_cb(downloaded, total)

        verified = self._verify_download(temp, model)
        temp.replace(target)
        self._record_checksum(model.filename, verified)
        return target

    @staticmethod
    def _verify_download(temp: Path, model: ModelDefinition) -> dict:
        """Verify the download against the strongest available checksum.

        Returns the verified checksums so they can be recorded for later
        update checks. Raises on mismatch.
        """
        verified: dict = {}
        if model.sha256:
            actual = _sha256_file(temp)
            if actual.lower() != model.sha256.lower():
                temp.unlink(missing_ok=True)
                raise ValueError(f"Checksum mismatch for {model.filename}")
            verified["sha256"] = actual.lower()
        elif model.sha1:
            actual = _sha1_file(temp)
            if actual != model.sha1:
                temp.unlink(missing_ok=True)
                raise ValueError(f"Checksum mismatch for {model.filename}")
            verified["sha1"] = actual
        return verified

    def _checksums_marker(self) -> Path:
        return self.user_models_dir / "checksums.json"

    def _read_checksums(self) -> dict:
        try:
            return json.loads(self._checksums_marker().read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}

    def _record_checksum(self, filename: str, checksums: dict) -> None:
        if not checksums:
            return
        data = self._read_checksums()
        data[filename] = checksums
        try:
            self._checksums_marker().write_text(json.dumps(data), encoding="utf-8")
        except OSError:
            pass

    def check_model_updates(self, timeout: int = 15) -> list[ModelDefinition]:
        """Return manifest models whose installed copy is superseded by a newer
        checksum. Cheap: compares the checksum recorded at download time against
        the manifest, without re-hashing the (multi-GB) model files.
        """
        remote = fetch_remote_catalog(timeout)
        if not remote:
            return []
        recorded = self._read_checksums()
        updates: list[ModelDefinition] = []
        for model in remote.values():
            if not model.sha256:
                continue
            if not (self.user_models_dir / model.filename).exists():
                continue
            have = (recorded.get(model.filename) or {}).get("sha256", "").lower()
            if have and have != model.sha256.lower():
                updates.append(model)
        return updates

    def installed_model_labels(self) -> list[str]:
        return [
            f"{MODEL_DEFS.get(key).label if key in MODEL_DEFS else key} ({source})"
            for key, _, source in self.available_models()
        ]


def _sha1_file(path: Path) -> str:
    h = hashlib.sha1()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()
