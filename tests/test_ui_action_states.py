import os
import sys
import time
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

CI_LINUX = os.environ.get("GITHUB_ACTIONS") == "true" and sys.platform.startswith("linux")

if not CI_LINUX:
    from PySide6.QtWidgets import QApplication

    from app.ui.main_window import MainWindow


@unittest.skipIf(
    CI_LINUX,
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

    def test_download_progress_updates_settings_dialog_only(self):
        self.window.show_model_settings()
        main_status = self.window.progress_label.text()
        self.window.active_download_model_key = "base"
        self.window.download_started_at = time.monotonic()

        self.window.on_download_progress(50, 100)

        self.assertEqual(self.window.progress_label.text(), main_status)
        self.assertEqual(self.window.model_download_progress.value(), 50)
        self.assertIn("Downloading Base", self.window.model_download_status_label.text())

    def _load_queue(self, count):
        self.window.batch_items = [
            {"path": Path(f"/tmp/file{i}.mp4"), "status": "queued", "output": None, "error": None}
            for i in range(count)
        ]
        self.window.refresh_batch_list()

    def _queue_names(self):
        return [Path(item["path"]).name for item in self.window.batch_items]

    def test_transcribe_button_label_follows_selection(self):
        self.assertEqual(self.window.transcribe_btn.text(), "Transcribe")

        self._load_queue(2)
        self.assertEqual(self.window.transcribe_btn.text(), "Transcribe selected")

        self.window.clear_batch_queue()
        self.assertEqual(self.window.transcribe_btn.text(), "Transcribe")

    def test_queue_reorder_moves_items_and_selection(self):
        self._load_queue(3)
        self.window.batch_list.setCurrentCell(0, 0)
        self.window.sync_action_controls()
        self.assertFalse(self.window.move_up_btn.isEnabled())
        self.assertTrue(self.window.move_down_btn.isEnabled())

        self.window.move_selected_queue_item(1)
        self.assertEqual(self._queue_names(), ["file1.mp4", "file0.mp4", "file2.mp4"])
        self.assertEqual(self.window.batch_list.currentRow(), 1)
        self.assertTrue(self.window.move_up_btn.isEnabled())

        self.window.move_selected_queue_item(-1)
        self.assertEqual(self._queue_names(), ["file0.mp4", "file1.mp4", "file2.mp4"])
        self.assertEqual(self.window.batch_list.currentRow(), 0)

    def test_queue_drop_reorder_uses_insertion_index(self):
        self._load_queue(3)
        # Drop row 0 at the end of the table (insertion index == row count).
        self.window.batch_list.setCurrentCell(0, 0)
        self.window.move_queue_row(0, 3)
        self.assertEqual(self._queue_names(), ["file1.mp4", "file2.mp4", "file0.mp4"])

    def test_queue_reorder_clears_header_sort(self):
        self._load_queue(2)
        self.window.queue_sort = (0, False)
        self.window.batch_list.setCurrentCell(0, 0)
        self.window.move_selected_queue_item(1)
        self.assertIsNone(self.window.queue_sort)

    def test_queue_reorder_blocked_while_busy(self):
        self._load_queue(2)
        self.window.batch_list.setCurrentCell(0, 0)
        self.window.current_worker = object()
        self.window.current_mode = "batch"
        self.window.sync_action_controls()
        self.assertFalse(self.window.move_up_btn.isEnabled())
        self.assertFalse(self.window.move_down_btn.isEnabled())

        self.window.move_selected_queue_item(1)
        self.assertEqual(self._queue_names(), ["file0.mp4", "file1.mp4"])

    def test_reset_workspace_clears_state(self):
        self._load_queue(2)
        self.window._confirm_reset = lambda: True
        self.window.selected_file = Path("/tmp/file0.mp4")
        self.window.current_transcript_path = Path("/tmp/out.txt")
        self.window.transcript_editor.setEnabled(True)
        self.window.transcript_editor.setPlainText("some transcript")
        self.window.transcript_label.setText("/tmp/out.txt")

        self.window.reset_workspace()

        self.assertEqual(self.window.batch_items, [])
        self.assertEqual(self.window.batch_list.rowCount(), 0)
        self.assertIsNone(self.window.selected_file)
        self.assertIsNone(self.window.current_transcript_path)
        self.assertEqual(self.window.transcript_editor.toPlainText(), "")
        self.assertFalse(self.window.transcript_editor.isEnabled())
        self.assertEqual(self.window.transcript_label.text(), "No transcript loaded")
        self.assertEqual(self.window.progress_label.text(), "Ready")
        self.assertEqual(self.window.transcribe_btn.text(), "Transcribe")

    def test_reset_workspace_respects_cancel_and_busy(self):
        self._load_queue(1)
        self.window._confirm_reset = lambda: False
        self.window.reset_workspace()
        self.assertEqual(len(self.window.batch_items), 1)

        self.window._confirm_reset = lambda: True
        self.window.current_worker = object()
        self.window.reset_workspace()
        self.assertEqual(len(self.window.batch_items), 1)

    def test_missing_model_prompt_can_start_default_download(self):
        actions = []
        self.window.model_combo.clear()
        self.window._prompt_model_download = lambda: "download"
        self.window.show_model_settings = lambda: actions.append("settings")
        self.window.download_model = lambda key: actions.append(("download", key))

        self.window.ensure_default_model_available(force=True)

        self.assertEqual(actions, ["settings", ("download", "base")])
        self.assertIn("Download a model", self.window.progress_label.text())


if __name__ == "__main__":
    unittest.main()
