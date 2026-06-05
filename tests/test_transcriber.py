import unittest
from pathlib import Path

from app.core.transcriber import Transcriber


class TranscriberOutputPathTests(unittest.TestCase):
    def test_output_file_appends_extension_to_dotted_stem(self):
        out_base = Path("/tmp/Roberto.Benigni.Pietro-Un.Uomo.Nel.Vento.2025.WEB-DL.1080p.ITA.H264")

        self.assertEqual(
            Transcriber._output_file(out_base, "txt"),
            Path("/tmp/Roberto.Benigni.Pietro-Un.Uomo.Nel.Vento.2025.WEB-DL.1080p.ITA.H264.txt"),
        )

    def test_timestamp_file_appends_csv_to_dotted_stem(self):
        out_base = Path("/tmp/movie.1080p.ITA.H264")

        self.assertEqual(
            Transcriber._output_file(out_base, ".csv"),
            Path("/tmp/movie.1080p.ITA.H264.csv"),
        )


if __name__ == "__main__":
    unittest.main()
