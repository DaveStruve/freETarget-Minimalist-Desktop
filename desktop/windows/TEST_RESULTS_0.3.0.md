# freETarget Minimalist 0.3.0-beta.1 — Validation

- Windows source: 37 Python tests passed (Linux), including data storage, desktop bridge, backup/restore and controller tests.
- macOS source: 47 Python tests passed (Linux), including Mac/iOS preview packaging checks; the iOS preview remains unchanged.
- Node.js regression suites: scoring/session, five-shot timing, statistics, storage bootstrap and browser migration checks passed in local runs. A few full-suite runs exceeded the available execution window; individual suites passed.
- Chromium browser smoke checks passed separately on both source trees: new sidebar, collapse/expand, app icon, navigation, settings tab placement, default toggles, USB first-run default, station/AP switching, fixed AP address, station address preservation and save/reopen behavior.
- Visual screenshots inspected in Chromium at 1440×900 for light/dark expanded/collapsed and connection/backup settings.
- Not yet tested: native Windows PyInstaller executable/installer, macOS .app build, actual WebView2/WKWebView rendering, signing/notarization, USB hardware, Wi-Fi hardware and live target shooting. Build and acceptance-test on each operating system before sharing with beta testers.
- Existing `freETarget/DesktopBeta` data folder and database schema preserved. Back up data before upgrading.
