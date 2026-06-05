# macOS Architecture-Specific Builds

This document explains the four macOS build configurations for Transcriber-LP: Automatic (recommended), ARM64 (Apple Silicon), Intel x86_64, and universal binaries.

## Build Targets

### Target 0: Automatic Build (Recommended)

**When to use:** For most developers and CI/CD pipelines. Let the system figure out what to build.

**How it works:**
- Detects your Mac's architecture (ARM64 or Intel)
- Checks which binaries are available in `third_party/macos/`
- Automatically builds the right configuration:
  - If both architectures are present → builds **universal**
  - If only ARM64 is present → builds **ARM64-only**
  - If only Intel is present → builds **Intel-only**

**Build command:**
```bash
bash scripts/build_macos_auto.sh
```

**Output:** `dist/Transcriber-LP.app` (architecture depends on available binaries)

**Example output:**
```
🔍 Machine architecture: arm64

📦 Binary availability:
   ARM64 (Apple Silicon):  ✓ available
   Intel x86_64:           ✓ available

🚀 Strategy: Building UNIVERSAL (ARM64 + Intel x86_64)
```

---

### Target 1: ARM64 (Apple Silicon)

**When to use:** Building for modern Macs with Apple Silicon chips (M1, M2, M3, etc.)

**Requirements:**
- Python environment running on ARM64 or with ARM64 cross-compilation support
- ARM64 macOS binaries:
  - `third_party/macos/ffmpeg`
  - `third_party/macos/ffprobe`
  - `third_party/macos/whisper-cli`
  - Any `@rpath` `.dylib` dependencies

**Build command:**
```bash
bash scripts/build_macos.sh
```

**Output:** `dist/Transcriber-LP.app` (ARM64)

**Spec file:** `Transcriber-LP.spec` with `target_arch='arm64'`

---

### Target 2: Intel x86_64

**When to use:** Building for older Macs with Intel processors

**Requirements:**
- Python environment running on x86_64 or with x86_64 cross-compilation support
- Intel x86_64 macOS binaries:
  - `third_party/macos/ffmpeg` (Intel version)
  - `third_party/macos/ffprobe` (Intel version)
  - `third_party/macos/whisper-cli` (Intel version)
  - Any `@rpath` `.dylib` dependencies (Intel versions)

**Build command:**
```bash
bash scripts/build_macos_intel.sh
```

**Output:** `dist/Transcriber-LP.app` (Intel x86_64)

**Spec file:** `Transcriber-LP-intel.spec` with `target_arch='x86_64'`

**Important:** The Intel binaries must be the actual x86_64 builds, not ARM64 binaries. You can verify this with:
```bash
file third_party/macos/whisper-cli
# Should output: "Mach-O 64-bit executable x86_64"
```

---

### Target 3: Universal Binary (ARM64 + x86_64)

**When to use:** Creating a single app bundle that runs natively on both Apple Silicon and Intel Macs

**Requirements:**
- Both ARM64 and Intel x86_64 versions of all binaries
- The `lipo` tool (included with Xcode Command Line Tools)

**Build command:**
```bash
bash scripts/build_macos_universal.sh both
```

**What happens:**
1. Builds ARM64 version → `dist/Transcriber-LP-arm64.app`
2. Builds Intel x86_64 version → `dist/Transcriber-LP-intel.app`
3. Uses `lipo` to combine the two executables into a universal Mach-O binary
4. Creates final `dist/Transcriber-LP.app` with the universal executable
5. Cleans up intermediate files

**Output:** `dist/Transcriber-LP.app` (universal Mach-O, runs natively on both architectures)

**Verification:**
```bash
file dist/Transcriber-LP.app/Contents/MacOS/Transcriber-LP
# Should output: "Mach-O universal binary with 2 architectures: [x86_64:Mach-O 64-bit executable x86_64] [arm64:Mach-O 64-bit executable arm64]"
```

---

## Build Script Options

### Automatic Build (Recommended for most users)

The `build_macos_auto.sh` script intelligently detects your setup:

```bash
bash scripts/build_macos_auto.sh
```

It automatically:
- Detects your machine architecture
- Checks which binaries are available
- Builds the appropriate configuration without manual intervention

### Flexible Manual Build

The `build_macos_universal.sh` script gives you explicit control:

```bash
# Build only ARM64
bash scripts/build_macos_universal.sh arm64

# Build only Intel
bash scripts/build_macos_universal.sh intel

# Build both and create universal app
bash scripts/build_macos_universal.sh both
```

---

## Binary Verification

After building, verify the architecture of your app bundle:

```bash
# Check architecture
file dist/Transcriber-LP.app/Contents/MacOS/Transcriber-LP

# For ARM64:
# Mach-O 64-bit executable arm64

# For Intel:
# Mach-O 64-bit executable x86_64

# For universal:
# Mach-O universal binary with 2 architectures: ...
```

---

## Third-Party Binaries

### How to obtain x86_64 binaries

If you only have ARM64 binaries and need to build for Intel, you have these options:

1. **Compile on Intel hardware** - Build ffmpeg/ffprobe/whisper-cli on an Intel Mac
2. **Cross-compile from ARM64** - Use tools like `osxcross` (advanced)
3. **Use CI/cloud build service** - Build on Intel CI runners (GitHub Actions supports Intel runners)
4. **Find pre-built x86_64 binaries** - Some projects provide architecture-specific downloads

### Organizing binaries by architecture

If you have binaries for multiple architectures, consider organizing them:

```
third_party/
├── macos/
│   ├── arm64/
│   │   ├── ffmpeg
│   │   ├── ffprobe
│   │   ├── whisper-cli
│   │   └── *.dylib
│   ├── x86_64/
│   │   ├── ffmpeg
│   │   ├── ffprobe
│   │   ├── whisper-cli
│   │   └── *.dylib
│   └── models/
└── ...
```

Then update the PyInstaller spec files to reference the correct paths based on the target architecture.

---

## Distribution

- **ARM64 apps** run natively on Apple Silicon Macs (M1+)
- **Intel apps** run natively on Intel Macs but may be slower on Apple Silicon (Rosetta 2 translation)
- **Universal apps** run natively and optimally on both architectures

For maximum compatibility and performance, distributing a universal app is recommended.

---

## Environment Variables

All build scripts support the same optional environment variables:

```bash
# Include a bundled model with automatic build
TRANSCRIBER_LP_BUNDLE_MODEL=1 bash scripts/build_macos_auto.sh

# Include a bundled model with ARM64 build
TRANSCRIBER_LP_BUNDLE_MODEL=1 bash scripts/build_macos.sh

# Include a bundled model with Intel build
TRANSCRIBER_LP_BUNDLE_MODEL=1 bash scripts/build_macos_intel.sh

# Include a bundled model with universal build
TRANSCRIBER_LP_BUNDLE_MODEL=1 bash scripts/build_macos_universal.sh both
```

See `README.md` for more details on model bundling.

---

## Troubleshooting

### "Missing third_party/macos/..." errors
- Verify the binary exists and is for the correct architecture
- Check the build output for which specific binary is missing
- Ensure all `@rpath` `.dylib` dependencies are also present

### "lipo: can't open input file"
- Verify both ARM64 and Intel builds completed successfully
- Check that `dist/Transcriber-LP-arm64.app` and `dist/Transcriber-LP-intel.app` exist
- Ensure the executables are at the expected path

### App won't launch on target architecture
- Run `file` on the app executable to verify architecture
- On Apple Silicon, verify no ARM64 app is running (Rosetta 2 can conflict)
- Check system logs: `log stream --predicate 'eventMessage contains "Transcriber-LP"'`
