import tempfile
import unittest
from pathlib import Path

from app.core.model_manager import ModelManager, MODEL_DEFS


class ModelManagerTests(unittest.TestCase):
    def test_available_models_prefers_downloaded_models(self):
        manager = ModelManager()
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            bundled_dir = Path(tmpdir) / "bundled"
            user_dir.mkdir()
            bundled_dir.mkdir()

            base_filename = MODEL_DEFS["base"].filename
            (user_dir / base_filename).write_text("downloaded")
            (bundled_dir / base_filename).write_text("bundled")

            manager.user_models_dir = user_dir
            manager.bundled_dir = bundled_dir
            available = manager.available_models()

            self.assertTrue(any(source == "downloaded" for _, _, source in available))
            self.assertEqual(available[0][2], "downloaded")

    def test_resolve_model_path_raises_when_missing(self):
        manager = ModelManager()
        with tempfile.TemporaryDirectory() as tmpdir:
            manager.user_models_dir = Path(tmpdir) / "user"
            manager.bundled_dir = Path(tmpdir) / "bundled"

            with self.assertRaises(FileNotFoundError):
                manager.resolve_model_path("base")

    def test_has_models_reflects_available_models(self):
        manager = ModelManager()
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            bundled_dir = Path(tmpdir) / "bundled"
            user_dir.mkdir()
            bundled_dir.mkdir()
            manager.user_models_dir = user_dir
            manager.bundled_dir = bundled_dir

            self.assertFalse(manager.has_models())
            (user_dir / MODEL_DEFS["base"].filename).write_text("model")
            self.assertTrue(manager.has_models())

    def test_default_download_model_is_checksum_gated_base(self):
        manager = ModelManager()
        model = manager.default_download_model()

        self.assertEqual(model.key, "base")
        self.assertEqual(model.filename, "ggml-base.bin")
        self.assertTrue(model.sha1)

    def test_download_model_requires_checksum(self):
        manager = ModelManager()

        with self.assertRaisesRegex(ValueError, "without a checksum"):
            manager.download_model("large-v3")


if __name__ == "__main__":
    unittest.main()
