# Distribution Checklist

Use this checklist before publishing a release artifact.

- Confirm `git status` is clean.
- Confirm CI is green on `main`.
- Confirm app version in `app/version.py` matches the changelog and release tag.
- Confirm no binaries, models, virtual environments, build outputs, caches, or backup files are committed.
- Confirm `LICENSE` is present for Transcriber-LP source code.
- Confirm `docs/THIRD_PARTY_NOTICE.md` is current.
- Confirm bundled `ffmpeg`/`ffprobe` provenance is recorded in `docs/FFMPEG_BUILD.md`.
- Confirm bundled model provenance is recorded in `docs/MODEL_PROVENANCE.md`.
- Confirm exact third-party license texts are included with any packaged app bundle.
- Confirm the packaged app was smoke-tested on the target macOS architecture.
- Create a signed Git tag such as `v0.1.0` when the release is final.
