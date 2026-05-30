from __future__ import annotations

from pathlib import Path


def build_ffmpeg_command(input_file: Path, wav_path: Path, executable: Path | str = "ffmpeg") -> list[str]:
    return [
        str(executable),
        "-hide_banner",
        "-y",
        "-i",
        str(input_file),
        "-vn",
        "-ar",
        "16000",
        "-ac",
        "1",
        "-c:a",
        "pcm_s16le",
        str(wav_path),
    ]


def build_whisper_command(
    model_file: Path,
    wav_path: Path,
    out_base: Path,
    output_format: str,
    source_language: str | None,
    target_language: str | None,
    save_timestamps: bool = False,
    executable: Path | str = "whisper-cli",
) -> list[str]:
    fmt_flag = {
        "txt": ["-otxt"],
        "srt": ["-osrt"],
        "vtt": ["-ovtt"],
    }.get(output_format, ["-otxt"])

    source_language = str(source_language or "auto").strip().lower()
    target_language = str(target_language or "as_source").strip().lower()
    task = "translate" if target_language in ("english", "en") else "transcribe"

    command = [
        str(executable),
        "-m",
        str(model_file),
        "-f",
        str(wav_path),
        "-of",
        str(out_base),
        "--no-gpu",
        *fmt_flag,
    ]

    if source_language:
        command.extend(["-l", source_language])

    if task == "translate":
        command.append("-tr")

    if save_timestamps:
        command.append("-ocsv")

    return command
