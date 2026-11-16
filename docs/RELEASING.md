# Publishing builds

## Current status

Source import is complete.

| Platform | Committed source version | Published download |
| --- | --- | --- |
| Windows x64 / x86 | 0.3.11-beta.1 | [Existing Windows v0.3.10-beta.1 installer](https://github.com/DaveStruve/freETarget-Minimalist-Desktop/releases/download/v0.3.10-beta.1/freETarget-Minimalist-Desktop-0.3.10-beta.1-Windows-Setup.exe); no separate x86 asset yet |
| macOS Universal | 0.3.11-beta.1 | [Existing Mac v0.3.10-beta.1 ZIP](https://github.com/DaveStruve/freETarget-Minimalist-Desktop/releases/download/v0.3.10-beta.1/freETarget-Minimalist-Desktop-0.3.10-beta.1-macOS-Universal.zip) |
| Android | 0.2.2-beta.1 — versionCode 4 | No signed release APK published |

The [Releases page](https://github.com/DaveStruve/freETarget-Minimalist-Desktop/releases) is the download directory to use in the repository's About website field. Link to actual assets only after upload.

## Build and test

Build from each platform directory and follow its documentation:

- [Windows x64 and x86](../desktop/windows/README_WINDOWS_BUILDS.md): separate Python architectures, PyInstaller, and Inno Setup configurations.
- [macOS Universal](../desktop/macos/BUILD_UNIVERSAL_MAC.md): a Mac and universal2 Python; check Intel and Apple Silicon binaries.
- [Android](../android/README.md): Android Studio project and APK build. Confirm the Gradle configuration before building: the README specifies Gradle 8.9, while the committed wrapper requests 9.9.0. Resolve that discrepancy as a separate build configuration change.

Test startup, live target scoring, connection/reconnection, shooter profiles, session history, and saved settings on actual devices. Test Windows x86 on Windows 10 32-bit. Test Android Wi-Fi and USB serial separately. Record Mac Intel and Apple Silicon runtime checks and any signing/notarization status. Source import alone does not establish compatibility.

Create a signed Android release APK using signing material stored outside the repository. Retain the signing material for future updates.

## Prepare the release

1. Build and test each intended platform from the source commit to be tagged.
2. Record embedded application versions and exact output filenames. Desktop source is 0.3.11-beta.1; Android source is 0.2.2-beta.1. Keep those distinct unless intentionally changing and testing the version fields.
3. Open [New release](https://github.com/DaveStruve/freETarget-Minimalist-Desktop/releases/new), create a new tag from that commit, and mark it as a **pre-release**.
4. Start with the [release notes template](releases/next-beta.md). Record changes, actual asset links, validation results, and known limitations.
5. Attach Windows x64 and x86 Setup EXEs, the macOS Universal ZIP, and the signed Android APK when each is ready.
6. Save a draft, verify its attached files and notes, then publish.
7. Update the root README's download table to the newly published assets. Keep previous release tags and assets intact.

Do not relabel an old binary with a newer application version. If a platform is unchanged or not ready, link its original release and state its actual version.

Finished applications belong in release assets. Source belongs in Git. GitHub's automatic source archives contain the files at the selected tag; the old v0.3.10-beta.1 tag predates the application source import and does not contain these newly committed projects.
