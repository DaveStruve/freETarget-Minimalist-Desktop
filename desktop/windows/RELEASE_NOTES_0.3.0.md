# freETarget Minimalist — Desktop Beta 0.3.0-beta.1

Independent desktop scoring software, tested with the freETarget Minimalist hardware build. This source release includes Windows and macOS build packages; **compiled Windows/macOS binaries must be built on the corresponding platform**. iOS preview sources, where present, are unchanged and not part of this release.

## Changes

- New matching light/dark sidebar, 50%-width centered wordmark, upper-right collapse icon, actual program icon when collapsed, icon-only session shortcuts with tooltips, and bottom-anchored Live Scoring / Statistics / History / Settings navigation.
- Statistics and all existing progress filters/charts moved out of History into their own screen. History is now the full saved-session log with review/delete access, including records excluded from analytics filters.
- Settings: dedicated Backup tab, diagnostics switch moved to Connection and OFF by default, Ignore Misses OFF by default, Demo Shot OFF and hidden by default (still available when enabled).
- Connection: USB/Serial is the first-run default. Wi-Fi offers Station (user-supplied IP, 1090 default) and Access Point (192.168.10.9:1090 locked) modes. Existing saved connection preferences are retained.
- Total Score value displayed beneath its label. Navigation renamed to Live Scoring. Application renamed freETarget Minimalist.
- Draggable dashboard/target column divider was explicitly deferred and is not included.

## Data and upgrades

The existing per-user `freETarget/DesktopBeta` data folder, schema and database remain unchanged on both platforms so the user's saved shooters, guns, settings and session history continue to load. **Export a backup from the current app before upgrading.** A new install uses updated default preferences; an existing explicit setting is preserved.

Windows: the installer retains its previous AppId and install directory for in-place upgrade. The executable is now `freETargetMinimalist.exe`; the installer removes the obsolete executable. macOS: the application bundle remains `freETarget Minimalist.app`, with a newly named internal executable.

## Testing and limitations

Source/JS regressions and Python storage tests run on Linux. Browser UI screenshots and controls were inspected in headless Chromium. Native builds, live USB/TCP hardware, Windows WebView2, and macOS WKWebView still require acceptance tests on their actual operating systems before distribution. The app does not support arbitrary freETarget hardware builds without testing.
