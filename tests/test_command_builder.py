import unittest
from pathlib import Path

from app.core.command_builder import build_ffmpeg_command, build_whisper_command


class CommandBuilderTests(unittest.TestCase):
    def test_build_ffmpeg_command(self):
        input_path = Path("input.mp4")
        output_path = Path("/tmp/output.wav")

        command = build_ffmpeg_command(input_path, output_path)

        self.assertEqual(command[0], "ffmpeg")
        self.assertIn(str(input_path), command)
        self.assertIn(str(output_path), command)
        self.assertIn("-ar", command)
        self.assertIn("16000", command)
        self.assertIn("-ac", command)
        self.assertIn("1", command)

    def test_build_ffmpeg_command_accepts_explicit_executable(self):
        command = build_ffmpeg_command(
            Path("input.mp4"),
            Path("/tmp/output.wav"),
            executable=Path("/bundle/ffmpeg"),
        )

        self.assertEqual(command[0], "/bundle/ffmpeg")

    def test_build_whisper_command_for_text(self):
        model_file = Path("ggml-base.bin")
        wav_path = Path("/tmp/input.wav")
        out_base = Path("/tmp/output")

        command = build_whisper_command(
            model_file=model_file,
            wav_path=wav_path,
            out_base=out_base,
            output_format="txt",
            source_language="auto",
            target_language="as_source",
        )

        self.assertEqual(command[0], "whisper-cli")
        self.assertIn("-m", command)
        self.assertIn(str(model_file), command)
        self.assertIn("-f", command)
        self.assertIn(str(wav_path), command)
        self.assertIn("-of", command)
        self.assertIn(str(out_base), command)
        self.assertIn("-otxt", command)

    def test_build_whisper_command_accepts_explicit_executable(self):
        command = build_whisper_command(
            model_file=Path("ggml-base.bin"),
            wav_path=Path("/tmp/input.wav"),
            out_base=Path("/tmp/output"),
            output_format="txt",
            source_language="auto",
            target_language="as_source",
            executable=Path("/bundle/whisper-cli"),
        )

        self.assertEqual(command[0], "/bundle/whisper-cli")

    def test_build_whisper_command_with_translation(self):
        model_file = Path("ggml-base.bin")
        wav_path = Path("/tmp/input.wav")
        out_base = Path("/tmp/output")

        command = build_whisper_command(
            model_file=model_file,
            wav_path=wav_path,
            out_base=out_base,
            output_format="srt",
            source_language="en",
            target_language="english",
        )

        self.assertIn("-osrt", command)
        self.assertIn("-l", command)
        self.assertIn("en", command)
        self.assertIn("-tr", command)


if __name__ == "__main__":
    unittest.main()
