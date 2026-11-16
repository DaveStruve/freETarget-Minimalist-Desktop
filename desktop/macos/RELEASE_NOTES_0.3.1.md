# freETarget Minimalist — 0.3.1-beta.1

This incremental desktop beta builds on 0.3.0-beta.1. **Windows and macOS source packages** are provided; these are not precompiled installers or notarized apps.

## Changes in this release

1. **Approved sidebar layout (light and dark).** The expanded header uses a centered freETarget wordmark approximately 50% of the sidebar width; the collapse icon remains on the upper-right. When collapsed, the app icon and wordmark are hidden and the expand icon is centered. The collapsed sidebar retains icon-only live session controls and tooltips.
2. **Session Controls redesigned to match the approved mockup.** Shooter & Gun is now a full-row selection control with a profile summary. Discipline and Session each have an icon label and full-width dropdown. Session Rules remains accessible. Start / Resume, Next Stage, and Log Score & End now have their own full-width rows and distinct icons; button state and existing shooting logic remain intact. Demo Shot remains hidden unless enabled in General settings.
3. **Bottom navigation unchanged in behavior.** Live Scoring, Statistics, History and Settings stay anchored at the bottom, separated by a horizontal rule and using the same horizontal button padding as Session Controls.
4. **Appearance → Sidebar.** New **Auto-collapse sidebar when session starts** option, **off by default**. When enabled, starting/resuming a session collapses the sidebar; pausing or ending a session does not reopen it. The preference is saved in the existing local desktop database.
5. **Appearance → Custom Logo.** Moved from General to Appearance without changing stored logos or upload/reset functionality.
6. **Live Scoring adjustable Dashboard / Target columns.** Drag the vertical handle between panels to change the ratio. The default remains the existing 0.3.0 layout: the target fills its square panel and fits the available viewport. The new ratio is saved and restored. Double-click the handle, or focus it and press **Home**, to reset. Left/Right arrow keys also resize the columns. On narrow screens, the existing stacked layout remains in use and the handle is hidden.

## Unchanged

- Target communication and scoring code; Minimalist-specific compatibility.
- Profiles, saved guns, scoring records, session formats, voice announcements, diagnostics, connection settings, backup/restore and statistics/history.
- Existing local data folder, backup format, and schema version (1). Installing the new app does **not** intentionally delete stored data.
- iOS/iPadOS preview sources in the macOS archive (not updated for these desktop-only changes).

## Building

**Windows:** Extract the Windows ZIP and run `BUILD_WINDOWS.bat`. To create an installer, run `BUILD_INSTALLER.bat` after building (requires Inno Setup). The output is a local Windows binary/installer; none is included in the ZIP.

**macOS:** Extract the macOS ZIP and run `BUILD_MAC.command` on the Mac. The build helper supports the prior Python 3.12–3.15 selection mechanism. The output is a local `.app` and has not been signed or notarized here.

**Before upgrading:** Export a backup in the installed beta and finish/log any active session. Install/build on the relevant operating system, then test with the real freETarget Minimalist hardware before distributing to beta users.

## Validation

- Windows source: 41 Python unit tests passed on Linux.
- macOS source: 51 Python unit tests passed on Linux, including unchanged iOS preview checks.
- Windows Node.js suites passed: UI/scoring, five-shot, statistics, desktop bootstrap, browser exporter.
- macOS Node.js suites passed: UI/scoring, five-shot, statistics, desktop bootstrap, browser exporter.
- Both platforms passed headless Chromium acceptance tests for light/dark sidebar behavior, 50%-width centered logo, collapsed centered expand control, bottom navigation, Appearance settings, live start auto-collapse, manual pause behavior, target-column drag/persistence/reset, and square target fit.

**Not yet validated:** Native Windows or macOS builds, Windows WebView2/macOS WKWebView rendering, installer upgrade behavior, code signing/notarization, real USB or Wi-Fi hardware, and actual shooting sessions. The above browser tests used a simulated connected target.
