# freETarget Minimalist 0.3.5 — Universal Mac build validation

**Package:** macOS universal2 build-script update; application version remains 0.3.5-beta.1.

## Passed in development environment (Linux)

- **73 Python unit tests passed** (includes 7 new portable tests for universal2 build command, Mach-O architecture inspection, Intel-slice rejection, and Python selection).
- **Node.js scoring, UI, statistics, browser migration, desktop storage, iOS adapter and five-shot tests passed** via `python tests/run_ui.py`.
- `bash -n` passed for Mac build, native fallback, launch, iOS preparation and Python-selection scripts.
- Python syntax compilation passed for `tools/mac_tasks.py` and `tests/test_mac_universal.py`.
- Application HTML/JavaScript and `app/version.py` hashes match the original 0.3.5-beta.1 macOS release; no UI or data changes.
- Build script requests PyInstaller `universal2`, isolates its virtual environment, and validates arm64/x86_64 slices in all collected Mach-O binaries before writing the ZIP.

## Not tested / not claimed

- Running PyInstaller on macOS or producing an actual `.app` in this Linux environment.
- Running on an Intel Mac, Apple Silicon Mac, or testing a target via USB/Wi-Fi.
- Apple Developer ID signing, notarization, Gatekeeper approval or public distribution readiness.

A real Mac with universal2 Python and the required dependencies is needed to produce and test the final binary. If any dependency lacks a required architecture slice, the build intentionally fails rather than packaging a misleading universal2 ZIP.
