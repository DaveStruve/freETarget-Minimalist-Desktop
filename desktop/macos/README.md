> Updated desktop release notes: `RELEASE_NOTES_0.3.5.md`. iOS preview remains unchanged.

# freETarget Minimalist Desktop Beta

**Designed for the freETarget Minimalist build.** Independent project, based on the corrected Windows beta and v1.7.9 scoring UI. Other builds and firmware combinations remain unverified.

Version **0.3.5-beta.1** is a source preview starting two ports:

| Platform | Implementation | First connection scope | Build on |
|---|---|---|---|
| macOS | Existing Python bridge/SQLite + native Cocoa/WebKit window | TCP/Wi-Fi and USB | Mac, universal2 Python 3.13 recommended/PyInstaller |
| iOS/iPadOS | SwiftUI/WKWebView, native TCP and SQLite, shared scoring UI | Wi-Fi/TCP; no USB or target editing | Mac, Xcode |

Open **START_HERE.txt** for the short launch/build instructions, and **BUILD_UNIVERSAL_MAC.md** to package for both Apple Silicon and Intel. The package includes a real `.xcodeproj` with bundled Web assets and icons, not just an architecture proposal. Native Apple compilation, signing and device acceptance are pending; no compiled Apple app is included.

The desktop scoring/session/statistics/voice implementation is shared rather than rewritten. iOS uses a native local service adapter, stream framer, durable key/value database and document pickers. It cannot run the Python USB/command bridge; unsupported controls/endpoints are hidden or rejected. `ios/mobile.css` changes the phone/tablet layout without changing the Windows distribution.

## Data

Mac records live in `~/Library/Application Support/freETarget/DesktopBeta`. iOS records live inside its app container. Backups use the desktop schema-1 JSON format, with manual import/export. There is no automatic sync and imports replace data rather than merging it. Finish/log a session before export and test round trips with disposable records first.

The iOS native store and backup codec are new implementations and need their included Swift tests plus actual-device acceptance. Passing desktop/JavaScript simulations does not establish native iOS correctness. Leaving iOS stops/pauses its current sequence and disconnects; unlogged shots remain in memory only.

## Reference firmware

`reference/freETarget_WiFi_LED_Pin13.zip` is copied unchanged from the confirmed Windows closed-beta package. Its source identifies 4.2.8 WiFi Test 1, Mega 2560, station-mode changes, LED PWM 13 and TCP 1090. Firmware notes retain the duplicate LED definition/wiring limits. No firmware changes or flashing actions are part of either Apple app build.

## Development

See BUILD_AND_TEST.md, ARCHITECTURE.md and TEST_RESULTS.md. The Python/Node checks run in this Linux workspace. Swift native core tests are included for `swift test` on a Mac; they were not executed here. The Xcode project generator is optional—the generated project is included. If shared Web assets change, rerun `tools/prepare_ios.py` before building iOS.

Original attribution/notices are in `licenses/` and THIRD_PARTY_NOTICES.md. This package does not assign a new license to upstream materials. No publication, invitations, signing credentials or automatic update service are configured.

The macOS launch scripts automatically select Python 3.12–3.15. Python 3.15 is enabled for first-run testing, not yet validated on Apple hardware.

**Universal Mac packaging:** `BUILD_MAC.command` now targets both Apple Silicon and Intel; use a Python.org universal2 Python interpreter. `BUILD_MAC_NATIVE.command` builds for the current architecture only. No compiled app is included in this source ZIP.
