import unittest

from app.ui.main_window import _format_milliseconds


class UiHelperTests(unittest.TestCase):
    def test_format_milliseconds_without_hours(self):
        self.assertEqual(_format_milliseconds(65_000), "01:05")

    def test_format_milliseconds_with_hours(self):
        self.assertEqual(_format_milliseconds(3_661_000), "01:01:01")


if __name__ == "__main__":
    unittest.main()
