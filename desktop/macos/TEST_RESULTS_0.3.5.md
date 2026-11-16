# freETarget Minimalist 0.3.5 — QA Results

**Environment:** Linux, Python 3.13, Node.js 22, headless Chromium. No native Windows/macOS build machine or connected freETarget hardware.

- Windows Python unittest suite: **56 tests passed**, including five new 0.3.5 release regression tests.
- macOS Python unittest suite: **66 tests passed**, including five new 0.3.5 release regression tests.
- Node.js UI/scoring, five-shot, statistics, desktop bootstrap, exporter, and storage suites: passed on both platform sources. The macOS iOS adapter suite also passed.
- Chromium UI acceptance: passed on Windows and macOS at **1550×960**, **1280×800**, and **1000×750**. Verified all six dashboard widgets have collapse controls, both new widgets save and restore independent collapse state, picker hide/show preserves state, collapsed cards show only their headers, widget padding matches existing cards, the Session Details fields contain only Session and Structure, and the Edit Widgets label stays adjacent to the icon. Spanish label translation verified.
- Visual check: Small Recent Shots and Session Details displayed side-by-side with matching expanded heights at 1550×960; narrow viewports stack appropriately. Session Details elapsed/remaining clocks stack without overlapping.
- Existing 0.3.4 footer/layout improvements and original scoring behavior retained.

**Not tested:** Native Windows/macOS builds, live Wi-Fi/USB target reception, installed voices, and long-running shooting sessions.
