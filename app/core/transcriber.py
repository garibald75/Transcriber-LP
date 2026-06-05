from __future__ import annotations

import os
import signal
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .command_builder import build_ffmpeg_command, build_whisper_command
from .paths import bundled_bin, outputs_dir, temp_dir


@dataclass
class TranscriptionOptions:
    input_file: Path
    model_file: Path
    language: str
    output_format: str
    task: str = "transcribe"
    target_language: str = "as_source"
    save_timestamps: bool = False
    output_name: str | None = None
    output_dir: str | None = None


class Transcriber:
    def __init__(self) -> None:
        self.ffmpeg_path = self._ensure_executable(bundled_bin("ffmpeg"))
        self.whisper_path = self._ensure_executable(bundled_bin("whisper-cli"))
        self._current_process: subprocess.Popen | None = None
        self._cancel_requested = False

    @staticmethod
    def _ensure_executable(path: Path) -> Path:
        if not path.exists():
            raise FileNotFoundError(f"Missing bundled binary: {path}")
        mode = path.stat().st_mode
        path.chmod(mode | 0o111)
        return path

    def cancel(self, log_cb=None) -> None:
        self._cancel_requested = True
        proc = self._current_process
        if proc and proc.poll() is None:
            self._terminate_process_group(proc, log_cb, "current")

    def transcribe(self, options: TranscriptionOptions, log_cb=None) -> Path:
        self._cancel_requested = False
        input_file = Path(options.input_file)
        self._validate_file(input_file, "Input file")
        self._validate_file(Path(options.model_file), "Model file")

        wav_path, out_dir, out_base = self._prepare_paths(input_file, options)
        self._log(log_cb, "=== TRANSCRIBER START ===")
        self._log_debug(log_cb, input_file, options, wav_path, out_dir, out_base)

        self._run(
            "FFMPEG",
            build_ffmpeg_command(input_file, wav_path, executable=self.ffmpeg_path),
            log_cb,
            env=os.environ.copy(),
        )

        whisper_cmd = build_whisper_command(
            Path(options.model_file),
            wav_path,
            out_base,
            options.output_format,
            options.language,
            options.target_language,
            save_timestamps=options.save_timestamps,
            executable=self.whisper_path,
        )

        env = self._build_environment()
        self._run("WHISPER", whisper_cmd, log_cb, env=env)

        output_file = self._output_file(out_base, options.output_format)
        self._verify_output_file(output_file)
        if options.save_timestamps:
            timestamp_file = self._output_file(out_base, "csv")
            self._verify_output_file(timestamp_file)
            self._log(log_cb, f"Timestamp sidecar saved: {timestamp_file}")
        self._log(log_cb, f"=== TRANSCRIBER END OK === {output_file}")
        return output_file

    def _validate_file(self, path: Path, label: str) -> None:
        if not path.exists():
            raise FileNotFoundError(f"{label} not found: {path}")

    def _prepare_paths(self, input_file: Path, options: TranscriptionOptions) -> tuple[Path, Path, Path]:
        tmp = temp_dir()
        out_dir = Path(options.output_dir) if options.output_dir else outputs_dir()
        out_dir.mkdir(parents=True, exist_ok=True)
        stem = options.output_name or input_file.stem
        wav_path = tmp / f"{stem}_{next(tempfile._get_candidate_names())}.wav"
        out_base = out_dir / stem
        return wav_path, out_dir, out_base

    @staticmethod
    def _build_environment() -> dict[str, str]:
        env = os.environ.copy()
        env["WHISPER_NO_METAL"] = "1"
        return env

    @staticmethod
    def _verify_output_file(output_file: Path) -> None:
        if not output_file.exists():
            raise FileNotFoundError(f"Expected output not found: {output_file}")

    @staticmethod
    def _output_file(out_base: Path, extension: str) -> Path:
        return Path(f"{out_base}.{extension.lstrip('.')}")

    @staticmethod
    def _log(log_cb, message: str) -> None:
        if log_cb:
            log_cb(message)

    def _log_debug(
        self,
        log_cb,
        input_file: Path,
        options: TranscriptionOptions,
        wav_path: Path,
        out_dir: Path,
        out_base: Path,
    ) -> None:
        self._log(log_cb, f"CWD: {Path.cwd()}")
        self._log(log_cb, f"Input exists: {input_file.exists()} -> {input_file}")
        self._log(log_cb, f"Model exists: {Path(options.model_file).exists()} -> {options.model_file}")
        self._log(log_cb, f"ffmpeg: {self.ffmpeg_path}")
        self._log(log_cb, f"whisper-cli: {self.whisper_path}")
        self._log(log_cb, f"temp dir: {temp_dir()}")
        self._log(log_cb, f"outputs dir: {out_dir}")
        self._log(log_cb, f"wav path: {wav_path}")
        self._log(log_cb, f"out base: {out_base}")

    def _run(self, label: str, cmd: list[str], log_cb=None, env=None) -> None:
        if self._cancel_requested:
            raise RuntimeError("Operation cancelled before process start.")

        self._log(log_cb, f"=== {label} COMMAND ===")
        self._log(log_cb, " ".join(cmd))
        if env:
            interesting = {k: env.get(k) for k in ["WHISPER_NO_METAL", "PATH"] if k in env}
            self._log(log_cb, f"=== {label} ENV === {interesting}")

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=env,
            preexec_fn=os.setsid if os.name != "nt" else None,
        )
        self._current_process = process

        output_lines: list[str] = []

        try:
            if process.stdout is not None:
                for line in process.stdout:
                    line = line.rstrip()
                    output_lines.append(line)
                    self._log(log_cb, f"[{label}] {line}")
                    if self._cancel_requested:
                        self._terminate_process_group(process, log_cb, label)
                        raise RuntimeError("Operation cancelled by user.")

            rc = process.wait()
            self._log(log_cb, f"=== {label} EXIT CODE === {rc}")

            if self._cancel_requested:
                raise RuntimeError("Operation cancelled by user.")

            if rc != 0:
                raise RuntimeError(
                    f"{label} failed with exit code {rc}\n"
                    f"CMD: {' '.join(cmd)}\n"
                    f"OUTPUT:\n" + "\n".join(output_lines[-300:])
                )
        finally:
            self._current_process = None

    def _terminate_process_group(self, process: subprocess.Popen, log_cb, label: str) -> None:
        try:
            self._log(log_cb, f"Stopping {label} process...")
            if os.name != "nt":
                os.killpg(process.pid, signal.SIGTERM)
            else:
                process.terminate()
        except Exception as exc:
            self._log(log_cb, f"Graceful stop failed: {exc}")
        try:
            process.wait(timeout=3)
        except Exception:
            try:
                self._log(log_cb, f"Force killing {label} process...")
                if os.name != "nt":
                    os.killpg(process.pid, signal.SIGKILL)
                else:
                    process.kill()
            except Exception as exc:
                self._log(log_cb, f"Force kill failed: {exc}")
