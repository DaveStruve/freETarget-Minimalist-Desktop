# Publishing builds

Current source versions: **Windows 0.3.11-beta.1**, **macOS 0.3.11-beta.1**, **Android 0.2.2-beta.1 (versionCode 4)**. Source versions do not prove that installers or APKs were built or device-tested.

Build each platform from its own source directory and follow its bundled build documentation. Windows requires separate x64 and x86 Python environments and Inno Setup for installers; macOS requires a universal2 Python environment on a Mac; Android requires JDK 17, Android SDK Platform 35, Gradle 8.9 and Android Gradle Plugin 8.7.3.

Test startup, target connections, live scoring, shooter profiles, session history and saved settings on actual devices. Windows x86 must be tested on Windows 10 32-bit. Android Wi-Fi and USB serial must be tested separately. Verify Mac Intel and Apple Silicon slices and actual runtime behavior. For Android, create a properly signed APK using signing material stored outside the repository and retain the keystore for updates.

Once all intended binaries are verified, create a **new** prerelease at [GitHub Releases](https://github.com/DaveStruve/freETarget-Minimalist-Desktop/releases/new), using the tested source commit. Attach platform-specific Windows Setup EXEs, macOS Universal ZIP and signed Android APK. Record actual filenames and versions in the release notes. Do not modify the existing `v0.3.10-beta.1` release.

**Do not publish source ZIPs as if they are compiled installers.** GitHub's automatically generated source ZIP/TAR archives become complete only after the source has been committed to the repository.
