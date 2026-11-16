# 0.3.8-beta.1 verification

- Windows Python unit tests: 71/71 passed (`python -m unittest discover -s tests -p 'test_*.py' -q`).
- macOS Python unit tests: 88/88 passed (same command).
- Windows Node regression runner: passed (`python tests/run_ui.py`).
- macOS Node regression runner: passed (`python tests/run_ui.py`), including iOS adapter tests.
- Chromium browser UI: passed at 1440×900, 1100×700, and 800×650. Validated expanded/collapsed logo center alignment, sidebar tab position, Connect Target placement and scroll independence, and centered Previous Target selector. Inspected Light/Dark snapshots.
- Browser shim provided local desktop storage without live hardware, so connection behavior was not tested end-to-end.
- Source ZIP integrity verified by CRC and SHA-256 manifests. Native builds and hardware not tested here.

Test note: The pre-existing `tests/test_ui.cjs` expectations for Previous Target's visible series label were corrected from the old long-form text to the `N / N` text introduced in 0.3.7. No application behavior was changed to satisfy that correction.
