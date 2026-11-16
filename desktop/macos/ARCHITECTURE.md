# Implementation boundaries

The shared source is `app/assets/index.html`, including the v1.7.9 scoring engine, History/statistics and embedded voice WAVs. A platform data/service adapter is installed before that UI initializes. iOS adds its own stylesheet; the Windows application is not modified by this package.

## macOS

The existing token-protected loopback service and Python TCP/serial bridge run in-process. The native window selects Cocoa instead of EdgeChromium. Data uses SQLite in Application Support. The existing storage format, migrations and native file dialogs are retained; Finder is opened with an argument list. The Mac PyInstaller spec supplies an app bundle, icon, network usage text and optional signing identity. The default `BUILD_MAC.command` explicitly targets universal2 (arm64 and x86_64) using a compatible Python.org framework and validates every collected Mach-O file. `BUILD_MAC_NATIVE.command` retains a native single-architecture build option. Both modes use the same app code and saved-data schema.

## iOS

SwiftUI owns a WKWebView showing only its generated local app file. Navigation to other local files is cancelled; external HTTP(S) links require an actual link action and open outside the app. Main-frame/path checks gate native operations. The app does not serve a network HTTP endpoint and cannot execute Python.

`ios_bootstrap.js` maps the existing asynchronous fetch API to WKScriptMessageHandlerWithReply. A private JavaScript prompt sentinel maps the synchronous Storage interface to a native SQLite transaction; cache/revision changes occur only after an acknowledged commit. Ordinary user alerts/confirmations use native dialogs. Initial scripts are loaded once the view is attached to a native window so storage acknowledgements do not depend on an offscreen web view.

`TargetConnection` owns one NWConnection on the main queue. PacketFramer reconstructs objects across arbitrary TCP chunks and ignores trace text outside objects, while preserving quoted braces and cleaning legacy empty-comma members. Events keep increasing IDs; polling discards only acknowledged events. Connection generations reject old callbacks. Reported shots use the existing coordinate/scoring path. Connection timeout, closure and buffer overflow are surfaced. No automatic command replay or reconnect is implemented.

The Swift SQLite store intentionally uses the same `meta`/`kv` schema and raw JSON value shapes as the desktop store. The backup codec produces schema-1 JSON and SHA-256 over the same canonical storage map. This is implemented source-level compatibility; Apple round-trip execution remains pending. Native store calls are serialized by their main-thread owner. Restore requires an idle session/disconnected target, a staged ten-minute preview and a matching revision, and writes a previous-data backup before replacement. Reload regenerates the injected snapshot. The iOS connection-method preference is normalized from USB to TCP when needed.

Saved data is local to each installation. Cross-device transfer is manual; there is no cloud sync, merge engine or automatic feedback upload. A copied backup contains personal records and is not encrypted by this app. Document picker operations use security-scoped access and do not read arbitrary user files.

Leaving the foreground stops/pauses the session and disconnects. The native app does not request background execution for shot collection. A terminated WebKit renderer disconnects and prompts for reload; an unlogged result may be lost. These lifecycle paths are implemented but must be checked on a device.

USB, firmware upload, target settings/terminal commands and the desktop browser exporter are not available on iOS. New native code is isolated from the working Windows branch; the entire iOS native host and Swift core require Apple compilation/testing before use as a beta release.
