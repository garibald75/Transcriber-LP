# Distribution Checklist

Use this checklist before publishing a release artifact. It is intentionally stricter than the requirements for maintaining the source repository.

- Confirm `git status` is clean.
- Confirm CI is green on `main`.
- Confirm app version in `app/version.py` matches the changelog and release tag.
- Confirm no binaries, models, virtual environments, build outputs, caches, or backup files are committed.
- Confirm `LICENSE` is present for Transcriber-LP source code.
- Confirm `docs/THIRD_PARTY_NOTICE.md` is current.
- Confirm `docs/RELEASE_COMPLIANCE.md` has been followed.
- Confirm `README.md`, `docs/USER_MANUAL.md`, `TEST_PLAN.md`, and `docs/TECHNICAL_REVIEW.md` describe the current release features.
- Confirm bundled `ffmpeg`/`ffprobe` provenance is recorded in `docs/FFMPEG_BUILD.md`.
- Confirm no model weights are bundled by default.
- If a model is intentionally bundled, confirm `TRANSCRIBER_LP_BUNDLE_MODEL=1` was used and bundled model provenance is recorded in `docs/MODEL_PROVENANCE.md`.
- Confirm `whisper-cli` and all required `@rpath` `.dylib` files are bundled.
- Confirm exact third-party license texts are included with any packaged app bundle.
- Confirm the FFmpeg build license classification is compatible with the intended distribution model.
- Confirm the packaged app was smoke-tested on the target macOS architecture.
- Confirm media preview, quick transcript editing, batch import, output retrieval, and optional timestamp CSV sidecar export were smoke-tested.
- Confirm no generated user outputs, including transcripts, subtitle files, batch results, or timestamp CSV sidecars, are included in public release artifacts unless approved as sample assets.
- Confirm `codesign --verify --deep --strict --verbose=2 dist/Transcriber-LP.app` passes from a non-cloud-synced release directory.
- Create a signed Git tag such as `v0.3.1` when the release is final.
