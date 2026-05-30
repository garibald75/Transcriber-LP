# Model Provenance

Transcriber-LP can use local `whisper.cpp` model files such as `ggml-base.bin`. Model files are not committed to this repository and are not bundled by default.

Before distributing a model inside a packaged app, record the exact provenance and redistribution terms below. The default app flow lets users open Settings from the `Current Model` placeholder when no model is installed, then verifies downloaded models by checksum before use.

## Required Release Information

- Model filename:
- Upstream model owner:
- Conversion/distribution source:
- Download URL:
- Source revision or immutable artifact digest:
- SHA-256:
- License or model card:
- Redistribution allowed: yes/no
- License/model card included in bundle: yes/no

## Current Development Defaults

The app can download model files from the `ggerganov/whisper.cpp` Hugging Face repository. Those files are derived from OpenAI Whisper models and converted for use by `whisper.cpp`.

Built-in downloads are enabled only for models that have a checksum in `app/core/model_manager.py`; models without a checksum must be installed manually after provenance has been verified. The default first-run placeholder opens Settings, where `ggml-base.bin` is one of the checksum-verified download options.

Do not redistribute a model file until its exact license and provenance have been verified for the specific artifact being shipped.

## Current Local Smoke-Test Model

This model is not committed to the repository or bundled by default. It can be downloaded by the app from Settings at runtime, and it was also used to validate a local macOS package.

- Model filename: `ggml-base.bin`
- Upstream model owner: OpenAI Whisper
- Conversion/distribution source: `ggerganov/whisper.cpp` Hugging Face repository
- Download URL: https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin
- SHA-1 used by local downloader: `465707469ff3a37a2b9b8d8f89f2f99de7299dac`
- SHA-256 observed locally: `60ed5bc3dd14eea856493d334349b405782ddcaf0028d4b5df4088345fba2efe`
- License or model card: OpenAI Whisper source is MIT; verify the exact Hugging Face artifact terms before redistribution
- Redistribution allowed: not asserted here
- License/model card included in bundle: no, local smoke-test only
