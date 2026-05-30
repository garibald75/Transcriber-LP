from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

import requests

from .paths import bundled_models_dir, models_dir


@dataclass(frozen=True)
class ModelDefinition:
    key: str
    filename: str
    label: str
    size_label: str
    multilingual: bool
    sha1: str

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


class ModelManager:
    def __init__(self) -> None:
        self.user_models_dir = models_dir()
        self.bundled_dir = bundled_models_dir()

    def available_models(self) -> list[tuple[str, Path, str]]:
        available: list[tuple[str, Path, str]] = []
        seen: set[str] = set()

        available.extend(self._collect_preferred_models(seen))
        available.extend(self._collect_custom_models(seen))
        return available

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

    def download_model(self, model_key: str, progress_cb=None) -> Path:
        if model_key not in MODEL_DEFS:
            raise ValueError(f"Unsupported model: {model_key}")

        model = MODEL_DEFS[model_key]
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

        self._verify_download(temp, model)
        temp.replace(target)
        return target

    @staticmethod
    def _verify_download(temp: Path, model: ModelDefinition) -> None:
        if model.sha1:
            sha1 = _sha1_file(temp)
            if sha1 != model.sha1:
                temp.unlink(missing_ok=True)
                raise ValueError(f"Checksum mismatch for {model.filename}")

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
