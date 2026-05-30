# Model Provenance

Transcriber-LP can use local `whisper.cpp` model files such as `ggml-base.bin`. Model files are not committed to this repository.

Before distributing a model inside a packaged app, record the exact provenance and redistribution terms below.

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

Built-in downloads are enabled only for models that have a checksum in `app/core/model_manager.py`; models without a checksum must be installed manually after provenance has been verified.

Do not redistribute a model file until its exact license and provenance have been verified for the specific artifact being shipped.

## Current Local Smoke-Test Model

This model is not committed to the repository. It was used only to validate a local macOS package.

- Model filename: `ggml-base.bin`
- Upstream model owner: OpenAI Whisper
- Conversion/distribution source: `ggerganov/whisper.cpp` Hugging Face repository
- Download URL: https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin
- SHA-1 used by local downloader: `465707469ff3a37a2b9b8d8f89f2f99de7299dac`
- SHA-256 observed locally: `60ed5bc3dd14eea856493d334349b405782ddcaf0028d4b5df4088345fba2efe`
- License or model card: verify OpenAI Whisper and Hugging Face artifact terms for the exact artifact before redistribution
- Redistribution allowed: not asserted here
- License/model card included in bundle: no, local smoke-test only
