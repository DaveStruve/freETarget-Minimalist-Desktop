# Changelog

## Unreleased — source imported, 2026-11-16

- Imported the published Arduino Mega Wi-Fi/LED Pin 13 firmware source into [`firmware/arduino-mega/`](firmware/arduino-mega/), including all original `.ino` and `.h` files and the original package notes. The firmware remains optional; no new HEX or hardware-test result was produced.

- Committed Windows x64/x86 and macOS Universal source v0.3.11-beta.1, with build scripts, installer configurations, tests, and assets.
- Committed Android source v0.2.2-beta.1 (versionCode 4), including Wi-Fi/TCP and USB serial connection code.
- Updated the project and platform documentation to reflect completed source import.
- Added direct links to the published Windows installer and macOS Universal ZIP.
- Documented the newer desktop source changes: Small/Large widget sizes, the idle-shot session prompt, and Mac target zoom/pan.

Published desktop downloads remain v0.3.10-beta.1. No new installer, APK, release tag, or device-testing result is implied by this documentation update.

## Unreleased — repository setup

- Expanded the project README to cover Windows x64, Windows x86, macOS, and Android.
- Added desktop and Android source destinations with explicit import status.
- Added source import instructions, release guidance, and a beta release note template.
- Added ignore rules for generated output, local configuration, signing material, and common data files.
- Added bug report and pull request templates.

The repository setup was followed by the application source import recorded above. New builds, hardware testing, and release assets remain pending.

## Desktop 0.3.10-beta.1

Existing published beta: [release and downloads](https://github.com/DaveStruve/freETarget-Minimalist-Desktop/releases/tag/v0.3.10-beta.1).

The original release contains the Windows installer, macOS Universal ZIP, and optional firmware source and wiring diagram. Its tag and assets are retained.
