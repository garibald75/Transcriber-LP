import unittest
import os
import sys

from pathlib import Path

CI_LINUX = os.environ.get("GITHUB_ACTIONS") == "true" and sys.platform.startswith("linux")

if not CI_LINUX:
    from app.ui.main_window import _batch_output_name, _count_stems, _format_milliseconds


@unittest.skipIf(CI_LINUX, "UI helpers import Qt UI modules on Linux CI.")
class UiHelperTests(unittest.TestCase):
    def test_format_milliseconds_without_hours(self):
        self.assertEqual(_format_milliseconds(65_000), "01:05")

    def test_format_milliseconds_with_hours(self):
        self.assertEqual(_format_milliseconds(3_661_000), "01:01:01")

    def test_batch_output_name_allows_unique_stems_to_use_default(self):
        counts = _count_stems([Path("first.mp4"), Path("second.mp4")])

        self.assertIsNone(_batch_output_name(Path("first.mp4"), 0, counts))

    def test_batch_output_name_suffixes_duplicate_stems(self):
        counts = _count_stems([Path("/a/clip.mp4"), Path("/b/clip.mov")])

        self.assertEqual(_batch_output_name(Path("/b/clip.mov"), 1, counts), "clip_02")


if __name__ == "__main__":
    unittest.main()
