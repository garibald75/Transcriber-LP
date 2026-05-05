from __future__ import annotations

import os
import signal
import subprocess
import tempfile
import traceback
from dataclasses import dataclass
from pathlib import Path

from .paths import bundled_bin, outputs_dir, temp_dir


@dataclass
class TranscriptionOptions:
    input_file: Path
    model_file: Path
    language: str
    output_format: str
    task: str = "transcribe"
    target_language: str = "as_source"
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
            try:
                if log_cb:
                    log_cb("Cancellation requested. Stopping current process...")
                proc.terminate()
            except Exception as exc:
                if log_cb:
                    log_cb(f"Terminate failed: {exc}")
            try:
                proc.wait(timeout=3)
            except Exception:
                try:
                    if log_cb:
                        log_cb("Force killing current process...")
                    proc.kill()
                except Exception as exc:
                    if log_cb:
                        log_cb(f"Kill failed: {exc}")

    def transcribe(self, options: TranscriptionOptions, log_cb=None) -> Path:
        try:
            self._cancel_requested = False
            in_file = Path(options.input_file)
            if not in_file.exists():
                raise FileNotFoundError(str(in_file))

            tmp = temp_dir()
            out_dir = Path(options.output_dir) if getattr(options, "output_dir", None) else outputs_dir()
            out_dir.mkdir(parents=True, exist_ok=True)
            stem = options.output_name or in_file.stem
            wav_path = tmp / f"{stem}_{next(tempfile._get_candidate_names())}.wav"
            out_base = out_dir / stem

            self._log(log_cb, "=== TRANSCRIBER START ===")
            self._log(log_cb, f"CWD: {Path.cwd()}")
            self._log(log_cb, f"Input exists: {in_file.exists()} -> {in_file}")
            self._log(log_cb, f"Model exists: {Path(options.model_file).exists()} -> {options.model_file}")
            self._log(log_cb, f"ffmpeg: {self.ffmpeg_path}")
            self._log(log_cb, f"whisper-cli: {self.whisper_path}")
            self._log(log_cb, f"temp dir: {tmp}")
            self._log(log_cb, f"outputs dir: {out_dir}")
            self._log(log_cb, f"wav path: {wav_path}")
            self._log(log_cb, f"out base: {out_base}")

            ffmpeg_cmd = [
                str(self.ffmpeg_path),
                "-hide_banner",
                "-y",
                "-i", str(in_file),
                "-vn",
                "-ar", "16000",
                "-ac", "1",
                "-c:a", "pcm_s16le",
                str(wav_path),
            ]
            self._run("FFMPEG", ffmpeg_cmd, log_cb, env=os.environ.copy())

            fmt_flag = {
                "txt": ["-otxt"],
                "srt": ["-osrt"],
                "vtt": ["-ovtt"],
            }.get(options.output_format, ["-otxt"])

            whisper_cmd = [
                str(self.whisper_path),
                "-m", str(options.model_file),
                "-f", str(wav_path),
                "-of", str(out_base),
                *fmt_flag,
            ]

            source_language = str(getattr(options, "language", None) or "auto").strip().lower()
            target_language = str(getattr(options, "target_language", "") or "as source").strip().lower()
            task = "transcribe"

            if source_language not in ("", "auto"):
                whisper_cmd.extend(["-l", source_language])

            env = os.environ.copy()
            env["WHISPER_NO_METAL"] = "1"

            self._log(log_cb, f"Language option: {options.language!r}")
            self._log(log_cb, f"Task: {task}")
            self._log(log_cb, f"Target transcribed language: {target_language}")
            self._log(
                log_cb,
                "Language behavior: auto-detect" if source_language in ("", "auto")
                else f"Language behavior: forced '{source_language}'"
            )
            self._log(log_cb, f"WHISPER_NO_METAL={env['WHISPER_NO_METAL']}")
            self._log(log_cb, "Whisper started. This may take several minutes on CPU.")
            self._run("WHISPER", whisper_cmd, log_cb, env=env)

            ext = options.output_format
            output_file = Path(f"{out_base}.{ext}")
            self._log(log_cb, f"Expected output file: {output_file}")
            if not output_file.exists():
                raise FileNotFoundError(f"Expected output not found: {output_file}")

            self._log(log_cb, f"=== TRANSCRIBER END OK === {output_file}")
            return output_file

        except Exception:
            tb = traceback.format_exc()
            self._log(log_cb, "=== TRANSCRIBER TRACEBACK ===")
            self._log(log_cb, tb)
            raise
        finally:
            self._current_process = None

    @staticmethod
    def _log(log_cb, message: str) -> None:
        if log_cb:
            log_cb(message)

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
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            env=env,
            preexec_fn=os.setsid if os.name != "nt" else None,
        )
        self._current_process = process

        stdout_lines = []
        stderr_lines = []

        try:
            if process.stdout is not None:
                for line in process.stdout:
                    line = line.rstrip()
                    stdout_lines.append(line)
                    self._log(log_cb, f"[{label} STDOUT] {line}")
                    if self._cancel_requested:
                        self._terminate_process_group(process, log_cb, label)
                        raise RuntimeError("Operation cancelled by user.")

            if process.stderr is not None:
                for line in process.stderr:
                    line = line.rstrip()
                    stderr_lines.append(line)
                    self._log(log_cb, f"[{label} STDERR] {line}")
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
                    f"STDOUT:\n" + "\n".join(stdout_lines[-300:]) + "\n\n"
                    f"STDERR:\n" + "\n".join(stderr_lines[-300:])
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
