import unittest


class ImportTests(unittest.TestCase):
    def test_core_imports(self):
        import app.core.paths  # noqa: F401
        import app.core.model_manager  # noqa: F401
        import app.core.notices  # noqa: F401
        import app.core.transcriber  # noqa: F401
        import app.version  # noqa: F401

    def test_ui_imports(self):
        import app.ui.main_window  # noqa: F401
        import app.ui.workers  # noqa: F401

    def test_entrypoint_import(self):
        import app.main  # noqa: F401


if __name__ == '__main__':
    unittest.main()
