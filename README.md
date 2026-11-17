# freETarget Minimalist

An independent live scoring application for freETarget Minimalist electronic targets, with a customizable scoring dashboard, shooter profiles, session history, and competition-style practice. **This repository now includes the Windows, macOS, and Android application source code, plus the Arduino Mega 2560 target firmware source.**

## Download and install

| Platform | Published version | Download |
| --- | --- | --- |
| Windows | 0.3.10-beta.1 | **[Download Windows installer](https://github.com/DaveStruve/freETarget-Minimalist-Desktop/releases/download/v0.3.10-beta.1/freETarget-Minimalist-Desktop-0.3.10-beta.1-Windows-Setup.exe)** |
| macOS — Intel and Apple Silicon | 0.3.10-beta.1 | **[Download macOS Universal ZIP](https://github.com/DaveStruve/freETarget-Minimalist-Desktop/releases/download/v0.3.10-beta.1/freETarget-Minimalist-Desktop-0.3.10-beta.1-macOS-Universal.zip)** |
| Windows 32-bit (x86) | Not yet published | Source and installer build scripts are available below. |
| Android | 0.2.2-beta.1 | **[Download Android APK](https://github.com/DaveStruve/freETarget-Minimalist-Desktop/releases/download/v0.3.10-beta.1/freETarget-Minimalist-Android-0.2.2-beta.1.apk)** |

[View all releases and downloads](https://github.com/DaveStruve/freETarget-Minimalist-Desktop/releases) · [Browse Arduino Mega firmware source](firmware/arduino-mega/) · [Download firmware source ZIP](https://github.com/DaveStruve/freETarget-Minimalist-Desktop/releases/download/v0.3.10-beta.1/freETarget-Minimalist-Arduino-Mega-WiFi-Fix-LED-Pin13-Source.zip)

Windows and macOS installers are published as v0.3.10-beta.1, and the Android v0.2.2-beta.1 APK is attached to that same GitHub release. Newer Windows and macOS source versions listed below are committed, but updated desktop installers have not yet been published. GitHub's automatic **Source code** ZIP and TAR files contain source files, not ready-to-run applications.

**Connecting Android over Wi-Fi?** See the [step-by-step Access Point and Station Mode setup guide](android/README.md#wi-fi-connection-setup-first-connection). Access Point connects your phone directly to the target at `192.168.10.9:1090`; Station Mode connects through your existing network using the target's assigned IP address on port `1090`. Selecting a mode in the app does not reconfigure the target firmware.

## Installer folders and build files

These links go directly to the **installer configuration or platform build folders in this repository**. They contain source and build scripts, **not ready-to-install programs**. Use the download links above for currently published installers.

| Platform | Installer / build folder | Build script or configuration | Installer output after a local build |
| --- | --- | --- | --- |
| Windows 64-bit (x64) | [Windows installer folder](desktop/windows/installer/) | [Build x64 installer](desktop/windows/BUILD_AND_INSTALL_X64.bat) · [x64 Inno Setup file](desktop/windows/installer/freETargetDesktop.iss) | `desktop/windows/release/installer/` |
| Windows 32-bit (x86) | [Windows installer folder](desktop/windows/installer/) | [Build x86 installer](desktop/windows/BUILD_AND_INSTALL_X86.bat) · [x86 Inno Setup file](desktop/windows/installer/freETargetDesktop-x86.iss) | `desktop/windows/release-x86/installer/` |
| macOS Universal | [Mac application/build folder](desktop/macos/) | [Build Mac application](desktop/macos/BUILD_MAC.command) | `desktop/macos/release/mac/` |
| Android | [Android Studio project folder](android/) | [Android app module](android/app/) · [Gradle build configuration](android/app/build.gradle) | `android/app/build/outputs/apk/` |

The output directories shown in the last column are created **on your computer after building**; they are not uploaded GitHub folders. For both Windows architectures in one run, use [BUILD_AND_INSTALL_BOTH.bat](desktop/windows/BUILD_AND_INSTALL_BOTH.bat). For installation-ready downloads, see [GitHub Releases](https://github.com/DaveStruve/freETarget-Minimalist-Desktop/releases).

## What's new in the committed source

**Windows and macOS — 0.3.11-beta.1**

- All six dashboard widgets offer **Small** and **Large** sizes. Large is the default, and existing layouts retain their saved sizes.
- An idle shot can prompt you to start a session. Accepting carries the shot into the session; the opening stage determines whether it is scored. The prompt can be disabled in **Settings → General**.
- macOS adds pinch-to-zoom and drag-to-pan on the live target, with a zoom percentage control to reset the view.
- Windows includes separate x64 and x86 application and Inno Setup installer build scripts.

**Android — 0.2.2-beta.1**

- Android source for phones and tablets, with layouts adapted to each screen.
- Wi-Fi/TCP and USB serial connection code.
- On-device profiles, guns, history, and settings.
- Live target zoom and pan, session controls, and connection diagnostics.

**Arduino Mega 2560 firmware — source now included**

- The complete published Wi-Fi-fix / LED Pin 13 firmware source is available in [`firmware/arduino-mega/`](firmware/arduino-mega/), including the Arduino sketch, headers, and original package notes.
- Includes ESP-01 Station Mode connectivity fixes, Access Point Mode support, and LED PWM set to **pin 13** rather than pin 5.
- This is an **optional firmware update**. No compiled firmware image or new hardware-test result is included.

The Android APK has been **tested successfully in an Android emulator** by the project maintainer. Testing on a physical Android phone or tablet—including real-target Wi-Fi and USB connectivity—is still pending. Desktop feature parity is not assumed. The newer desktop source changes still require platform builds and testing before updated desktop installers are published. Android features and limitations are documented in the [Android README](android/README.md).

## Application features

- Live target display, shot scores, and recent-shot direction indicators.
- Editable dashboard widgets, customizable appearance, and optional spoken scores.
- Shooter profiles with multiple guns and session tracking by gun.
- Saved sessions, statistics, and performance comparisons.
- Competition-style practice sessions using live target data.
- Desktop Wi-Fi/TCP and USB connectivity.

Feature availability varies by platform and version. Android is developed separately; desktop feature parity is not assumed.

## Source code and building

The application and Arduino Mega firmware source imports are complete.

| Project | Committed source version | Build documentation |
| --- | --- | --- |
| [Windows x64 and x86](desktop/windows/) | 0.3.11-beta.1 | [Windows build and installer instructions](desktop/windows/README_WINDOWS_BUILDS.md) |
| [macOS Universal](desktop/macos/) | 0.3.11-beta.1 | [Mac Universal build instructions](desktop/macos/BUILD_UNIVERSAL_MAC.md) |
| [Android](android/) | 0.2.2-beta.1 — versionCode 4 | [Android build and connection instructions](android/README.md) |
| [Arduino Mega firmware](firmware/arduino-mega/) | Wi-Fi fixes / LED PWM pin 13 | [Firmware build and flashing instructions](firmware/arduino-mega/README.md) |

Build from each platform's directory to preserve the relative paths expected by its scripts. Windows and macOS retain separate source snapshots with platform-specific changes. Experimental iOS preview files are preserved inside the Mac source; no iOS release is published here.

See [source provenance](docs/SOURCE_IMPORT.md), the [changelog](CHANGELOG.md), and [release instructions](docs/RELEASING.md). Committed source does not establish that a new installer has been compiled or tested.

## Arduino Mega 2560 firmware (optional)

The **firmware source is now part of this repository**, not just a ZIP attached to a release. Browse the [firmware project folder](firmware/arduino-mega/), open the [main Arduino sketch](firmware/arduino-mega/freETarget/freETarget.ino), or read the [firmware build and flashing guide](firmware/arduino-mega/README.md). The original [firmware source ZIP](https://github.com/DaveStruve/freETarget-Minimalist-Desktop/releases/download/v0.3.10-beta.1/freETarget-Minimalist-Arduino-Mega-WiFi-Fix-LED-Pin13-Source.zip) remains available for download.

This version addresses a Wi-Fi issue that **prevented Station Mode from connecting reliably** to an existing wireless network. It also includes related Wi-Fi communication and connection-handling fixes:

- Improved Station Mode initialization and DHCP/IP-address handling, including waiting for complete ESP responses and verifying that a valid, nonzero IP address is assigned before starting the TCP server.
- Corrected dropped incoming data during sends, receive-buffer overreads, incomplete ESP response/IP parsing, and Wi-Fi credential-buffer handling. The firmware retains its 16-character password limit and rejects longer passwords.
- Preserved Access Point Mode and TCP communication on port **1090**.

The package also configures **LED PWM on pin 13**, matching the hardware wiring used for this build (rather than the original pin 5). This LED pin change is separate from the Wi-Fi fixes. A [wiring diagram](https://github.com/DaveStruve/freETarget-Minimalist-Desktop/releases/download/v0.3.10-beta.1/freETarget-Minimalist-Arduino-Mega-WiFi-LED-Wiring-Diagram.jpeg) is included in the [published release](https://github.com/DaveStruve/freETarget-Minimalist-Desktop/releases/tag/v0.3.10-beta.1).

**Firmware installation is optional.** To compile it yourself, open `firmware/arduino-mega/freETarget/freETarget.ino` in Arduino IDE and select **Arduino Mega 2560**. Verify your target's wiring, especially LED PWM pin 13, before uploading. If your target already connects and operates reliably, you can continue using your existing firmware. No precompiled HEX file is provided.

## Reporting issues

[Open a GitHub issue](https://github.com/DaveStruve/freETarget-Minimalist-Desktop/issues/new/choose) with the application version, operating system, connection method, steps to reproduce, and relevant diagnostics. Remove personal information from attachments.

## Credits

The [original freETarget project](https://github.com/ten-point-nine/freETarget) by ten-point-nine and its contributors provided the original firmware and PC application. The [freETarget Minimalist hardware and Arduino adaptation](https://free-e-target.com/freeetarget-minimalist/) was published by [stoeckli](https://github.com/stoeckli/freETarget). Preserve the existing [LICENSE](LICENSE) and all platform-specific third-party notices and licenses.
