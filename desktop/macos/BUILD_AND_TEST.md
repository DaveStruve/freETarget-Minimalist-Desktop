# Apple build and acceptance

## Mac first

On a Mac with Python 3.12–3.15 installed, launch `START_MAC.command`. The launcher auto-detects a compatible interpreter and creates a separate virtual environment per Python version. It creates its own virtual environment and installs the Cocoa/WebKit dependencies. Configure your target's address/USB port, then test one live result and a saved/reopened session. The script keeps Terminal available on errors. Do not change the working Windows installation for this test.

Run `BUILD_MAC.command` to run Python tests and build a **universal2** `release/mac/freETarget Minimalist.app` (arm64 + x86_64) and `freETarget-Minimalist-0.3.5-beta.1-universal2.zip`. This requires a python.org universal2 Python installation, preferably Python 3.13. The build script selects a compatible Python, uses a separate universal2 virtual environment, checks the architecture of every bundled Mach-O file, and creates the ZIP with `ditto` to retain bundle metadata. See `BUILD_UNIVERSAL_MAC.md`.

`BUILD_MAC_NATIVE.command` retains the old single-architecture build option. macOS 13+ is the intended preview target. Check the universal app in its final moved location and test both an Apple Silicon and an Intel Mac without the development environment; architecture validation alone does not establish run-time compatibility.

For distribution, use your own Developer ID and the Apple signing/notarization process. `FREETARGET_MAC_SIGN_IDENTITY` can specify a signing identity for PyInstaller; no certificate is supplied. The included entitlements support the Python runtime/WebKit host and are not an App Store sandbox declaration. Signing, notarization and Gatekeeper acceptance have not run here. Do not ask testers to disable security controls.

Official references: https://pywebview.flowrl.com/guide/installation.html , https://pyinstaller.org/en/stable/feature-notes.html , https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution .

## iOS build

Refresh assets with `bash PREPARE_IOS.command` (or `python3 tools/prepare_ios.py`), open `ios/freETargetIOS.xcodeproj`, and select a simulator to check compilation/layout first. For a physical device, select your development team in Signing & Capabilities, select the device and Run. The target is iOS/iPadOS 16+, both phone and tablet. Use your own bundle identifier/team for a distributed build.

Optional unsigned simulator build from Terminal:

```
xcodebuild -project ios/freETargetIOS.xcodeproj -scheme freETargetIOS -sdk iphonesimulator -configuration Debug CODE_SIGNING_ALLOWED=NO build
```

Native core checks, on the Mac:

```
swift test
```

Those Swift tests cover packet fragmentation/legacy comma cleanup, malformed/nonfinite data, checksum round trips, database persistence/deletion/stale revisions and pre-restore backup. They have not been compiled or executed in this Linux workspace. Do not mark them passed based on the Python tests.

The app contains a Local Network usage description because it connects directly to the target. Allow access on the phone/tablet. If permission is denied, enable it in iOS Settings for the app and reconnect; the UI reports connection failures/timeouts. No discovery/multicast entitlement is requested: the address is entered manually.

The included privacy manifest is a draft for local app-container file metadata and files selected by the user. It must be reviewed against the final built app/SDK inventory and App Store Connect declarations. No App Store privacy or review approval is claimed.

## Hardware acceptance

Use the same known working Minimalist target first; close the other Windows/Mac client before connecting the next device. Record board, firmware, transport, OS/device, and app version with each result.

1. One real shot arrives once at the expected coordinates/score; explicit misses and out-of-target zeros remain distinct.
2. Named shooter/gun, logged session, saved target, statistics, settings and custom logo survive closing/reopening.
3. Export a disposable session/profile backup on Windows, import on Mac/iOS, export back and check coordinates, scores, rule snapshots and logo. Test cancel/stale-preview/replacement guards. Keep original data until all checks pass.
4. Test File picker cancel/error and native alert/confirmation behavior. On Mac check Finder Open Data Folder and quitting with an unlogged result.
5. On iPhone and iPad check portrait/landscape, safe areas, keyboard and display scaling. The phone layout is source-level work until visually checked on Apple devices.
6. Test Five-Shot Test Commands/volume and one short sequence. Confirm ordinary speech does not overlap range cues. Screen lock/app switch/audio interruption must stop the sequence, not silently continue it. Actual audio latency and shooting time are not certified.
7. Disconnect/reconnect and Wi-Fi loss must not silently duplicate/drop reports; stop and inspect incomplete strings. iOS currently requires a manual reconnect. Test USB port changes on Mac only.
8. On iOS test a renderer/app termination: committed records remain, while unlogged results may be lost. No background firing capture is implemented.

## Beta distribution later

Retain the current Windows installer as the working rollback version. Once the Apple builds pass native checks, package and version the Mac app separately. Use TestFlight for the invited iOS group after the required Apple Developer/App Store Connect setup and review; Xcode source is not directly installable by testers.

Apple's external-testing instructions: https://developer.apple.com/testflight/ and https://developer.apple.com/help/app-store-connect/test-a-beta-version/invite-external-testers/ . No TestFlight build was uploaded and no tester invitations were sent by this package.
