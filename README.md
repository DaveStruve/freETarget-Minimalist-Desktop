# freETarget Minimalist

Independent live scoring application for freETarget Minimalist electronic targets, with source projects for Windows, macOS and Android.

## Downloads

Finished applications are published under [GitHub Releases](https://github.com/DaveStruve/freETarget-Minimalist-Desktop/releases). GitHub's automatic source ZIP is **not** an installer.

| Platform | Source version | Download status |
| --- | --- | --- |
| Windows x64 | 0.3.11-beta.1 | Source prepared; new installer build/test/upload pending. Existing 0.3.10-beta.1 Windows installer remains available. |
| Windows x86 (32-bit) | 0.3.11-beta.1 | Source and installer scripts prepared; Windows 10 32-bit hardware validation and upload pending. |
| macOS Universal (Intel / Apple Silicon) | 0.3.11-beta.1 | Source prepared; new universal build/test/upload pending. Existing 0.3.10-beta.1 Mac ZIP remains available. |
| Android | 0.2.2-beta.1 (versionCode 4) | Source prepared for Android Studio; signed release APK and device testing pending. |

The existing published release is [v0.3.10-beta.1](https://github.com/DaveStruve/freETarget-Minimalist-Desktop/releases/tag/v0.3.10-beta.1). No new release is implied by this source import.

## Features

- Live shot scoring and recent-shot direction indicators.
- Customizable dashboard widgets, appearance and statistics.
- Shooter profiles with multiple firearms, logged sessions and performance comparisons.
- Competition-style sessions using live target data.
- Wi-Fi/TCP and USB connections on desktop. Android 0.2.2 source includes Wi-Fi/TCP and USB serial code; actual device testing remains necessary.

## Source layout

| Path | Contents |
| --- | --- |
| [`desktop/windows/`](desktop/windows/) | Windows 64-bit and 32-bit source, build and installer scripts. |
| [`desktop/macos/`](desktop/macos/) | macOS universal2 source and build scripts; includes experimental iOS preview files. |
| [`android/`](android/) | Android Studio project, Gradle wrapper, assets, Java bridge and source documentation. |
| [`docs/SOURCE_IMPORT.md`](docs/SOURCE_IMPORT.md) | Source provenance, exclusions and validation checklist. |
| [`docs/RELEASING.md`](docs/RELEASING.md) | Release workflow and platform testing guidance. |

Each platform source is retained in its own directory, preserving its relative paths. Windows and macOS 0.3.11 application snapshots have platform-specific differences and have **not** been blindly merged.

## Reporting issues

[Open a GitHub issue](https://github.com/DaveStruve/freETarget-Minimalist-Desktop/issues/new/choose) with the app version, operating system, connection method, reproduction steps and diagnostics (with personal information removed).

## Credits

The [original freETarget project](https://github.com/ten-point-nine/freETarget) by ten-point-nine and its contributors provided the original firmware and PC application. The [freETarget Minimalist hardware and Arduino adaptation](https://free-e-target.com/freeetarget-minimalist/) was published by [stoeckli](https://github.com/stoeckli/freETarget). Preserve the existing repository LICENSE and all platform-specific third-party notices and licenses.
