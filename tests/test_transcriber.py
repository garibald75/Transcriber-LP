import unittest
from tempfile import TemporaryDirectory
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

    def test_format_timestamp_ms(self):
        self.assertEqual(Transcriber._format_timestamp_ms("7453060"), "02:04:13.060")

    def test_timestamped_text_lines_from_csv(self):
        with TemporaryDirectory() as tmp:
            timestamp_file = Path(tmp) / "movie.csv"
            timestamp_file.write_text(
                'start,end,text\n'
                '30000,33000," [Music]"\n'
                '148000,152000," Buona sera, buona sera a tutti."\n',
                encoding="utf-8",
            )

            self.assertEqual(
                Transcriber._timestamped_text_lines(timestamp_file),
                [
                    "[00:00:30.000 - 00:00:33.000] [Music]",
                    "[00:02:28.000 - 00:02:32.000] Buona sera, buona sera a tutti.",
                ],
            )

    def test_write_timestamped_text_file_overwrites_plain_txt(self):
        with TemporaryDirectory() as tmp:
            timestamp_file = Path(tmp) / "movie.csv"
            output_file = Path(tmp) / "movie.txt"
            timestamp_file.write_text('start,end,text\n1000,2500," Hello."\n', encoding="utf-8")
            output_file.write_text("Hello.\n", encoding="utf-8")

            Transcriber._write_timestamped_text_file(timestamp_file, output_file)

            self.assertEqual(output_file.read_text(encoding="utf-8"), "[00:00:01.000 - 00:00:02.500] Hello.\n")


if __name__ == "__main__":
    unittest.main()
