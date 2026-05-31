import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from app.ui.main_window import MainWindow


@unittest.skipIf(
    os.environ.get("GITHUB_ACTIONS") == "true" and sys.platform.startswith("linux"),
    "UI smoke tests require a stable Qt desktop runtime; Linux CI covers non-GUI tests.",
)
class UiActionStateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def setUp(self):
        self.window = MainWindow()
        self.window.model_combo.clear()
        self.window.sync_action_controls()

    def tearDown(self):
        self.window.close()

    def test_transcribe_requires_file_and_model(self):
        self.assertFalse(self.window.transcribe_btn.isEnabled())

        self.window.selected_file = Path("/tmp/source.mp4")
        self.window.sync_action_controls()
        self.assertFalse(self.window.transcribe_btn.isEnabled())

        self.window.model_combo.addItem("Medium", "medium")
        self.window.sync_action_controls()
        self.assertTrue(self.window.transcribe_btn.isEnabled())

    def test_empty_workspace_disables_unavailable_actions(self):
        self.assertFalse(self.window.transcribe_btn.isEnabled())
        self.assertFalse(self.window.batch_transcribe_btn.isEnabled())
        self.assertFalse(self.window.stop_btn.isEnabled())
        self.assertFalse(self.window.retrieve_batch_btn.isEnabled())
        self.assertFalse(self.window.save_transcript_btn.isEnabled())
        self.assertFalse(self.window.play_pause_btn.isEnabled())
        self.assertFalse(self.window.media_stop_btn.isEnabled())
        self.assertFalse(self.window.media_slider.isEnabled())

    def test_main_stop_only_enables_for_transcription_workers(self):
        self.window.selected_file = Path("/tmp/source.mp4")
        self.window.model_combo.addItem("Medium", "medium")
        self.window.current_worker = object()

        self.window.current_mode = "download"
        self.window.sync_action_controls()
        self.assertFalse(self.window.stop_btn.isEnabled())

        self.window.current_mode = "single"
        self.window.sync_action_controls()
        self.assertTrue(self.window.stop_btn.isEnabled())

        self.window.current_mode = "batch"
        self.window.sync_action_controls()
        self.assertTrue(self.window.stop_btn.isEnabled())

        self.window.current_worker = None
        self.window.current_mode = None
        self.window.sync_action_controls()
        self.assertFalse(self.window.stop_btn.isEnabled())

    def test_disabled_action_buttons_use_inactive_cursors(self):
        self.assertEqual(self.window.transcribe_btn.cursor().shape(), self.window.stop_btn.cursor().shape())
        self.assertEqual(self.window.transcribe_btn.cursor().shape().name, "ArrowCursor")


if __name__ == "__main__":
    unittest.main()
