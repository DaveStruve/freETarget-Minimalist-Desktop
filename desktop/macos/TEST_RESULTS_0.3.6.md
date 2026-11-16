# freETarget Minimalist 0.3.6-beta.1 — Test results

- Windows Python `unittest discover`: 60 tests passed.
- macOS Python `unittest discover`: 77 tests passed.
- Windows Node.js `tests/run_ui.py`: passed UI/scoring/finals/five-shot/statistics/desktop bootstrap/export/storage tests.
- macOS Node.js `tests/run_ui.py`: passed the same tests plus iOS adapter.
- Chromium UI acceptance on Windows and Mac HTML variants: all 1550×960, 1280×800, 1000×750 scenarios passed, including both large and small Previous Target layouts and click-driven Edit Widgets changes.
- macOS universal2 packaging unit tests passed, including architecture verification and interpreter selector fixture isolation.
- No native Windows/macOS installers or `.app` binaries were built in this Linux test environment; physical target hardware and native WebKit were not tested.
