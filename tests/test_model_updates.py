import json
import tempfile
import unittest
from pathlib import Path

from app.core import model_manager as mm
from app.core.model_manager import ModelManager, ModelDefinition


class ParseManifestTests(unittest.TestCase):
    def test_parses_valid_entries(self):
        data = {
            "models": [
                {"key": "base", "filename": "ggml-base.bin", "label": "Base",
                 "size_label": "142 MiB", "multilingual": True, "sha256": "aaa"},
                {"key": "broken", "filename": "ggml-broken.bin"},  # no sha256 -> ignored
            ]
        }
        catalog = mm.parse_manifest(data)
        self.assertIn("base", catalog)
        self.assertNotIn("broken", catalog)
        self.assertEqual(catalog["base"].sha256, "aaa")

    def test_empty(self):
        self.assertEqual(mm.parse_manifest({}), {})


class CheckModelUpdatesTests(unittest.TestCase):
    def setUp(self):
        self._user = tempfile.TemporaryDirectory()
        self._bundled = tempfile.TemporaryDirectory()
        self.manager = ModelManager(
            user_models_dir=Path(self._user.name),
            bundled_dir=Path(self._bundled.name),
        )
        self._orig_fetch = mm.fetch_remote_catalog

    def tearDown(self):
        mm.fetch_remote_catalog = self._orig_fetch
        self._user.cleanup()
        self._bundled.cleanup()

    def _install(self, filename: str, recorded_sha256: str):
        (Path(self._user.name) / filename).write_text("dummy model bytes")
        (Path(self._user.name) / "checksums.json").write_text(
            json.dumps({filename: {"sha256": recorded_sha256}})
        )

    def _catalog(self, sha256: str):
        return {
            "medium": ModelDefinition(
                key="medium", filename="ggml-medium.bin", label="Medium",
                size_label="1.5 GiB", multilingual=True, sha1="", sha256=sha256,
            )
        }

    def test_flags_superseded_model(self):
        self._install("ggml-medium.bin", recorded_sha256="old")
        mm.fetch_remote_catalog = lambda timeout=15: self._catalog("new")
        updates = self.manager.check_model_updates()
        self.assertEqual([m.key for m in updates], ["medium"])

    def test_no_update_when_checksum_matches(self):
        self._install("ggml-medium.bin", recorded_sha256="same")
        mm.fetch_remote_catalog = lambda timeout=15: self._catalog("same")
        self.assertEqual(self.manager.check_model_updates(), [])

    def test_not_installed_is_ignored(self):
        # recorded checksum but file absent -> not an update
        (Path(self._user.name) / "checksums.json").write_text(
            json.dumps({"ggml-medium.bin": {"sha256": "old"}})
        )
        mm.fetch_remote_catalog = lambda timeout=15: self._catalog("new")
        self.assertEqual(self.manager.check_model_updates(), [])

    def test_no_remote_catalog_means_no_updates(self):
        self._install("ggml-medium.bin", recorded_sha256="old")
        mm.fetch_remote_catalog = lambda timeout=15: {}
        self.assertEqual(self.manager.check_model_updates(), [])


if __name__ == "__main__":
    unittest.main()
