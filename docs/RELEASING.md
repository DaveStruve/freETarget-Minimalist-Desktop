# Publishing releases

Use this repository for Windows x64, Windows x86, macOS Universal, and Android downloads. Keep the existing repository name and URL.

## Versions and tags

Keep an existing published tag attached to its original commit. Use a new version when application code changes.

The next proposed desktop version is `0.3.11-beta.1`; Android's identified source package is `0.2.0-beta.1`, and the existing macOS download is `0.3.10-beta.1`. These are separate current versions. Do not rename an older binary to imply it contains a newer application version.

A combined release can list multiple platform versions. State each actual version in the notes. Synchronize application version fields only as part of an intentional, tested source update. Android's internal version code must increase for subsequent updates distributed to existing users.

Do not create the next release tag until source import and the intended builds are complete.

## Build and validate

1. Import the actual source projects as described in [SOURCE_IMPORT.md](SOURCE_IMPORT.md).
2. Build Windows x64 and x86 with matching Python architectures and the package's Inno Setup configurations. Record the actual installer filenames.
3. Test startup, target connection, shooter profiles, saved sessions, statistics, and widget customization. Test x86 on a Windows 10 32-bit system before claiming verified compatibility.
4. Build and device-test a signed Android release APK, including Wi-Fi target connection and persistence across app restarts. Confirm the minimum Android version from the project.
5. Build and test macOS when publishing a new Mac version. If using the existing Mac build, link to its original release and identify it as unchanged.
6. Verify application versions shown by the built apps. Preserve Android signing material securely outside Git so future updates can use the intended signing identity.
7. Record what was actually tested and any known limitations.

Use the package instructions until source import provides verified commands. There is no build automation configured in this repository yet.

## Create a GitHub release

1. Open [New release](https://github.com/DaveStruve/freETarget-Minimalist-Desktop/releases/new).
2. Select the tested source commit and create a new tag, for example `v0.3.11-beta.1`.
3. Use a title such as **freETarget Minimalist — Desktop 0.3.11 Beta 1 / Android 0.2.0 Beta 1** when those are the actual included versions.
4. Start with the [release template](releases/next-beta.md), replace all pending text, and list the real asset filenames.
5. Attach the finished Windows x64 setup EXE, Windows x86 setup EXE, and signed Android APK. Attach a newly tested macOS Universal ZIP only if available.
6. Mark the release as a **pre-release** and save a draft.
7. Check the attached files, notes, versions, and testing statements, then publish.

Filename examples, to be replaced by actual build outputs:

| Platform | Suggested asset filename |
| --- | --- |
| Windows x64 | `freETarget-Minimalist-0.3.11-beta.1-Windows-x64-Setup.exe` |
| Windows x86 | `freETarget-Minimalist-0.3.11-beta.1-Windows-x86-Setup.exe` |
| Android | `freETarget-Minimalist-0.2.0-beta.1-Android.apk` |

Renaming an output file for clarity does not change the application's embedded version or architecture. Check both before upload.

Installers and APKs belong in release assets. Application source belongs in Git. GitHub's automatic source downloads contain only the tagged repository files; they become complete build sources only after the projects have actually been imported.
