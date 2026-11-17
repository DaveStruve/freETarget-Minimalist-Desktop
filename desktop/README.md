# freETarget Minimalist — Desktop

Windows and macOS source version **0.3.11-beta.1** is committed in this repository. Each platform retains its own source snapshot and build configuration.

## Download the desktop app (no build tools required)

**Want to install freETarget? Click your operating system below to download the actual app.** Do not download GitHub's **Source code** ZIP.

- **[Download Windows 64-bit installer (.exe)](https://github.com/DaveStruve/freETarget-Minimalist-Desktop/releases/download/v0.3.10-beta.1/freETarget-Minimalist-Desktop-0.3.10-beta.1-Windows-Setup.exe)** — Windows 10/11, v0.3.10-beta.1. Open the downloaded installer.
- **[Download macOS Universal (.zip)](https://github.com/DaveStruve/freETarget-Minimalist-Desktop/releases/download/v0.3.10-beta.1/freETarget-Minimalist-Desktop-0.3.10-beta.1-macOS-Universal.zip)** — Intel and Apple Silicon, v0.3.10-beta.1. Extract the ZIP and open the app.

The Windows 32-bit (x86) installer and updated v0.3.11-beta.1 desktop installers have not yet been published. [View all releases](https://github.com/DaveStruve/freETarget-Minimalist-Desktop/releases).

## Connecting to a target over Wi-Fi

Both **Windows and macOS** support **Access Point Mode** (connect your computer directly to the target's `FET-` Wi-Fi network at `192.168.10.9:1090`) and **Station Mode** (connect through your existing Wi-Fi using the target's router-assigned IP on port `1090`). Select the mode under **Settings → Connection → Wi-Fi / TCP**. Selecting a mode in the app does **not** reconfigure the target's firmware.

See the **[cross-platform Wi-Fi setup guide](../docs/WIFI_SETUP.md)** for step-by-step setup, target-side configuration via Arduino Terminal, and troubleshooting. The same guide also covers Android.

## Building the current source

| Folder | Includes | Start here |
| --- | --- | --- |
| [windows/](windows/) | Python/WebView application, tests, PyInstaller build, x64/x86 Inno Setup configurations | [Windows builds](windows/README_WINDOWS_BUILDS.md); `BUILD_AND_INSTALL_BOTH.bat` builds both architectures |
| [macos/](macos/) | Universal2 application source, tests, build scripts, experimental iOS preview source | [Mac Universal build](macos/BUILD_UNIVERSAL_MAC.md); `BUILD_MAC.command` |

Run builds from the platform folder: scripts expect `app/`, `tools/`, and assets beside them.

## Changes in 0.3.11-beta.1

- Small and Large sizes for all six widgets, retaining saved layout sizes.
- An optional start-session prompt after an idle shot, with scoring determined by the opening stage.
- Mac live-target pinch zoom, drag pan, and view reset.
- Separate Windows x64/x86 application and installer build paths.

See the [Windows release notes](windows/RELEASE_NOTES_0.3.11.md) and [Mac release notes](macos/RELEASE_NOTES_0.3.11.md). Native packaging and physical-device testing remain to be completed for the next release.

Windows and Mac snapshots have platform-specific differences. Keep them separate until a shared-source merge is reviewed and tested. Historical release notes describe their original versions.
