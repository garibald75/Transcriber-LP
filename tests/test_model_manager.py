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


if __name__ == "__main__":
    unittest.main()
