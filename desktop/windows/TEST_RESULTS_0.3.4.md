# freETarget Minimalist 0.3.4 — QA Results

**Environment:** Linux, Python 3.13, Node.js 22, headless Chromium; no native Windows/macOS or real target hardware available.

- Windows Python unittest suite: **51 tests passed**.
- macOS Python unittest suite: **61 tests passed**.
- Node.js baseline UI, five-shot, statistics, desktop bootstrap, exporter, and storage tests: passed on both platform sources; macOS iOS adapter suite also passed.
- JavaScript syntax checks: passed on both desktop sources.
- Chromium acceptance: passed on both sources at 1550×960, 1280×800, and 1000×750. The Customize Dashboard icon is immediately left of the theme icon, editing and widget picker still work, icon is hidden on Statistics and restored on Live Scoring, the bottom fade is gone, the Ready label under Log Score & End is hidden, and the target SVG occupies the restored square panel.
- Existing 0.3.3 functionality remains subject to prior regression suites and release tests.

**Not tested:** Native builds, installed voices, live Wi-Fi/USB target reception, and long-running hardware sessions.
