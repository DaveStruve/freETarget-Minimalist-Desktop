# freETarget Minimalist — Desktop

Windows and macOS source version **0.3.11-beta.1** is committed in this repository. Each platform retains its own source snapshot and build configuration.

## Published downloads

| Platform | Version | Download |
| --- | --- | --- |
| Windows | 0.3.10-beta.1 | [Windows installer](https://github.com/DaveStruve/freETarget-Minimalist-Desktop/releases/download/v0.3.10-beta.1/freETarget-Minimalist-Desktop-0.3.10-beta.1-Windows-Setup.exe) |
| macOS Universal | 0.3.10-beta.1 | [Mac ZIP — Intel and Apple Silicon](https://github.com/DaveStruve/freETarget-Minimalist-Desktop/releases/download/v0.3.10-beta.1/freETarget-Minimalist-Desktop-0.3.10-beta.1-macOS-Universal.zip) |

New v0.3.11-beta.1 installers and a separate Windows x86 download have not yet been published.

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
