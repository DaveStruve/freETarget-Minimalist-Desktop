# freETarget Minimalist

An independent scoring application for freETarget Minimalist electronic targets. This repository is the shared project home for Windows, macOS, and Android. The existing repository URL is retained so earlier links continue to work.

## Downloads

Get finished applications from [GitHub Releases](https://github.com/DaveStruve/freETarget-Minimalist-Desktop/releases). Open a release and expand **Assets** to choose a download. GitHub's automatic **Source code** ZIP and TAR files are repository snapshots, not installers.

| Platform | Download type | Availability |
| --- | --- | --- |
| Windows 64-bit (x64) | Setup EXE | The existing desktop v0.3.10-beta.1 release has a Windows installer. Separate x64/x86 packages for v0.3.11-beta.1 are pending. |
| Windows 32-bit (x86) | Setup EXE | Build configuration prepared separately; installer upload and Windows 10 x86 testing pending. |
| macOS Intel and Apple Silicon | Universal ZIP | Available in desktop v0.3.10-beta.1. |
| Android | Signed APK | Planned for direct download here; APK upload and device testing pending. Current source package is v0.2.0-beta.1 and focuses on Wi-Fi. |

An entry in this table does not mean a download has already been attached. Each release's asset list and notes are authoritative.

## Desktop features

- Redesigned live target display with recent shot scores and directions.
- Editable dashboard widgets and customizable appearance.
- Shooter profiles with multiple guns and session tracking by gun.
- Saved sessions, shooter statistics, and performance comparisons.
- Competition-style practice sessions using live target shots.
- Wi-Fi/TCP and USB target connections.

Android is developed separately. Check its release notes for available features and connection methods; desktop feature parity is not assumed.

## Repository layout

| Path | Purpose |
| --- | --- |
| [desktop/](desktop/) | Desktop source destination and import notes. |
| [android/](android/) | Android Studio project destination and import notes. |
| [docs/RELEASING.md](docs/RELEASING.md) | Build, test, and publish instructions for platform downloads. |
| [docs/SOURCE_IMPORT.md](docs/SOURCE_IMPORT.md) | Source packages to import and remaining setup work. |
| [docs/releases/](docs/releases/) | Release note templates. |
| [CHANGELOG.md](CHANGELOG.md) | Repository changes and release preparation status. |

**Source import is pending.** These platform folders currently contain setup notes. The complete application sources have not yet been committed, so cloning this repository does not yet provide a buildable project. Follow [source import instructions](docs/SOURCE_IMPORT.md).

## Reporting problems

[Open an issue](https://github.com/DaveStruve/freETarget-Minimalist-Desktop/issues/new/choose) with the application version, platform, connection method, steps to reproduce, and any relevant diagnostics. Remove personal information from attachments.

## Project credits

The [original freETarget project](https://github.com/ten-point-nine/freETarget) by ten-point-nine and its contributors provided the original firmware and PC application. The [freETarget Minimalist hardware and Arduino adaptation](https://free-e-target.com/freeetarget-minimalist/) was published by [stoeckli](https://github.com/stoeckli/freETarget). This application builds on that work.

The existing repository [LICENSE](LICENSE) is retained. Preserve applicable copyright notices and dependency licenses when importing source packages.
