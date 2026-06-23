import io
import tarfile
import tempfile
import unittest
from pathlib import Path

from app.core import engine_manager as em


class ParseVersionTests(unittest.TestCase):
    def test_orders_versions(self):
        self.assertGreater(em.parse_version("v1.7.5"), em.parse_version("v1.7.4"))
        self.assertGreater(em.parse_version("engine-v1.8.0"), em.parse_version("v1.7.9"))
        self.assertEqual(em.parse_version("v1.7.5"), em.parse_version("1.7.5"))

    def test_handles_garbage(self):
        self.assertEqual(em.parse_version(""), (0,))
        self.assertEqual(em.parse_version(None), (0,))


class SelectReleaseAssetTests(unittest.TestCase):
    def _release(self):
        return {
            "tag_name": "engine-v1.7.6",
            "assets": [
                {"name": "whisper-engine-macos-arm64.tar.gz",
                 "browser_download_url": "https://example/arm64.tgz"},
                {"name": "manifest.json", "browser_download_url": "https://example/m.json"},
            ],
        }

    def _manifest(self):
        return {
            "engine_version": "v1.7.6",
            "assets": {"arm64": {"name": "whisper-engine-macos-arm64.tar.gz", "sha256": "ABC123"}},
        }

    def test_resolves_matching_arch(self):
        info = em.select_release_asset(self._release(), self._manifest(), arch="arm64")
        self.assertIsNotNone(info)
        self.assertEqual(info["version"], "v1.7.6")
        self.assertEqual(info["tarball_url"], "https://example/arm64.tgz")
        self.assertEqual(info["sha256"], "abc123")

    def test_no_asset_for_arch(self):
        self.assertIsNone(em.select_release_asset(self._release(), self._manifest(), arch="x86_64"))

    def test_ignores_non_engine_tag(self):
        release = self._release()
        release["tag_name"] = "v0.5.1"  # an app release, not an engine release
        self.assertIsNone(em.select_release_asset(release, self._manifest(), arch="arm64"))


class SafeExtractTests(unittest.TestCase):
    def test_rejects_path_traversal(self):
        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode="w:gz") as tar:
            data = b"x"
            info = tarfile.TarInfo(name="../escape.txt")
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
        buf.seek(0)
        with tempfile.TemporaryDirectory() as d:
            with tarfile.open(fileobj=buf, mode="r:gz") as tar:
                with self.assertRaises(ValueError):
                    em._safe_extract(tar, Path(d))


class InstalledVersionTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._orig = em.app_support_dir
        em.app_support_dir = lambda: Path(self._tmp.name)

    def tearDown(self):
        em.app_support_dir = self._orig
        self._tmp.cleanup()

    def test_falls_back_to_bundled_when_no_marker(self):
        self.assertEqual(em.installed_engine_version(), em.BUNDLED_ENGINE_VERSION)
        self.assertIsNone(em.active_engine_dir())

    def test_uses_installed_engine_when_present(self):
        version = "v9.9.9"
        d = em.engine_root() / version
        d.mkdir(parents=True)
        (d / "whisper-cli").write_text("#!/bin/sh\n")
        em._marker_path().write_text(
            '{"engine_version": "v9.9.9", "dir": "v9.9.9"}', encoding="utf-8"
        )
        self.assertEqual(em.installed_engine_version(), version)
        self.assertEqual(em.active_engine_dir(), d)
        self.assertEqual(em.whisper_cli_path(), d / "whisper-cli")

    def test_invalid_marker_falls_back(self):
        # marker points at a dir without whisper-cli -> treated as not installed
        em._marker_path().write_text(
            '{"engine_version": "v9.9.9", "dir": "v9.9.9"}', encoding="utf-8"
        )
        self.assertEqual(em.installed_engine_version(), em.BUNDLED_ENGINE_VERSION)
        self.assertIsNone(em.active_engine_dir())


if __name__ == "__main__":
    unittest.main()
