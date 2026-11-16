freETarget Minimalist 0.3.10-beta.1 — see RELEASE_NOTES_0.3.10.md for the latest changes.
 
For the 32-bit Windows 10 portable build, see [BUILD_WINDOWS_X86.md](BUILD_WINDOWS_X86.md).

> See `RELEASE_NOTES_0.3.10.md` for all new UI features. The existing `DesktopBeta` data folder is retained for upgrade compatibility.

# freETarget Minimalist — Desktop Beta 0.3.10

Windows 10/11 x64 • Based on freETarget Live v1.7.9 TEST

This package contains the desktop app source, a Windows launcher, and scripts to build a portable executable and optional installer. **It does not contain a compiled `.exe`.** The native Windows window, compiled release and real target still need a Windows acceptance run. Storage, migration and simulated target regressions were tested on Linux; see TEST_RESULTS.md.

## Start on your Windows PC

1. Extract the complete ZIP into a writable folder, such as `Documents\freETargetMinimalistBeta`. Keep the files together. Stop your old freETarget bridge first so it does not hold the target connection or migration port.
2. Install **Python 3.12 x64** from https://www.python.org/downloads/windows/ if needed. Enable the Python launcher during installation. The source launcher supports Python 3.10–3.13 x64.
3. Ensure **Microsoft Edge WebView2 Runtime** is installed: https://developer.microsoft.com/microsoft-edge/webview2/ . Windows also needs **.NET Framework 4.8**, normally present on current Windows 10/11 PCs: https://dotnet.microsoft.com/download/dotnet-framework/net48 .
4. Double-click **START_DESKTOP.bat**. On first use it creates a private `.venv` beside the source and installs the pinned dependencies. This first setup needs internet access and may take a few minutes. Subsequent launches use that environment. `SETUP_DESKTOP.bat` can repair/reinstall dependencies.
5. The app opens in its own window and starts its local bridge automatically. Configure TCP or USB in Settings → Connection and use Connect as before. USB uses the same serial driver your target normally needs.

No separate bridge terminal or browser tab is required. All the existing scoring, History, shooter statistics, centered logo and Five-Shot Standard voice sequences are retained. Native audio playback and device timing must be checked on your Windows PC. Five-Shot Standard remains a browser-engine-guided format, with the same timing and scoring limits described in BASELINE_v1.7.9_README.txt.

## Bring your browser data across

The desktop app begins with its own storage. It cannot automatically access another browser's private data.

1. In the desktop app, open **Settings → General → Export Existing Browser Data**. Stop the old bridge first; this helper needs port 8765.
2. In the **original browser and original browser profile**, open `http://127.0.0.1:8765/`. If you previously used `http://localhost:8765/`, use that exact address instead. These are separate browser storage origins. The helper is a read-only export page at the old app address.
3. Check the shooter, gun and History counts, then choose **Download Browser Backup**. A custom logo in the old IndexedDB store is included. If counts are zero, check the original address/browser/profile before proceeding. Existing browser data is not changed or deleted.
4. Return to the desktop app. Finish and log or discard any active session, then disconnect the target. Choose **Settings → General → Restore / Migrate Data** and select the downloaded JSON.
5. Review the incoming and existing counts, then choose **Replace Desktop Data**. Restore replaces all desktop records/settings; it does not merge them. Existing desktop data is backed up first. The app reloads after a successful restore. Reconnect the target when ready.

Keep the original browser data and export file until you have checked profiles, gun selection, a saved session, statistics and the custom logo in the desktop app. Summary-only records from older versions remain summary-only.

## Where records are saved

`%LOCALAPPDATA%\freETarget\DesktopBeta\`

- `freetarget.sqlite3`: profiles, guns, saved History, preferences and logo.
- `backups\`: startup/exit and pre-restore JSON backups. The latest 30 automatic/pre-restore copies are retained. A daily startup backup is skipped if one already exists that day. Empty stores produce no automatic backup.
- `logs\desktop.log`: rotating diagnostic logs.
- `webview\`: private WebView2 browser-engine files. Scoring records are stored in SQLite rather than this cache.

Use **Settings → General → Export Backup** to save a complete JSON copy somewhere else. Export includes saved data only: log a current result first. **Open Data Folder** opens this location in Explorer. App folders can be replaced without moving these records. The optional installer preserves this data on uninstall. Only one instance may use a data folder at a time.

Unlogged shots live in memory until you log them. Closing a live/unsaved session stops or pauses it and asks whether to discard its unlogged result. Cancel leaves the app open; restart a stopped Five-Shot series using its normal restart flow. Abrupt termination or power loss can lose unlogged shots.

## Build an executable on Windows

Double-click **BUILD_WINDOWS.bat** on a Windows x64 machine with the Python/runtime prerequisites above. It installs build dependencies, runs Python regressions, and uses PyInstaller to produce:

- `release\freETargetMinimalist\freETargetMinimalist.exe`
- `release\freETargetMinimalist-0.3.10-beta.1-Windows-x64.zip`

Keep the **whole** executable folder together, including `_internal`; the `.exe` alone is insufficient. Recipients of this built release need WebView2 and .NET 4.8, but do not need Python. A dependency list and SHA-256 build manifest are included in the portable package.

For an optional per-user installer, install **Inno Setup 6** from https://jrsoftware.org/isinfo.php and run **BUILD_INSTALLER.bat** after the portable build. Output goes to `release\installer\`. The scripts do not download or install Inno Setup, WebView2, .NET or device drivers automatically. Generated executables/installers are unsigned unless you sign them separately.

Windows binaries must be built on Windows. A successful package build is followed by the acceptance checks in TEST_RESULTS.md before treating it as a tested Windows release.

## If it does not start

- A missing-Python message means the source launcher cannot find a supported 64-bit Python installation.
- Dependency/setup errors remain in the launcher window. Try SETUP_DESKTOP.bat with internet access from a writable extracted folder.
- A native error dialog points to the data folder and log. Check WebView2/.NET, then inspect `logs\desktop.log`. Existing data is never intentionally reset to fix startup errors.
- “Already running” means another app window/process owns this data folder. Close that instance before launching again.
- A migration-port error means the old bridge/export helper still owns 8765. Stop it and retry.
- Export JSON from Settings before moving to another PC. Do not copy a live SQLite database without its journal files; use the supported export/restore flow instead.

## Windows build test fix

This source package includes a Windows-only test cleanup correction (see `WINDOWS_TEST_FIX.md`). The initial build reported 35 passing tests and two temporary SQLite file-lock errors. The app and stored shooting data were not affected. Run `BUILD_WINDOWS.bat` again to compile the portable executable.
