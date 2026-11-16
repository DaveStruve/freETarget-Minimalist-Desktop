# Source import and provenance

The Windows, macOS, and Android application sources were committed to this repository on 2026-11-16. The source import is complete. The imported package was prepared from the three source ZIPs supplied by the project owner.

| Destination | Supplied ZIP | Version |
| --- | --- | --- |
| `desktop/windows/` | `freETarget-Minimalist-0.3.11-beta.1-Windows-x64-x86-Clean-Source (2).zip` | 0.3.11-beta.1 |
| `desktop/macos/` | `freETarget-Minimalist-0.3.11-beta.1-macOS-Universal-BuildFix-Source 2.zip` | 0.3.11-beta.1 |
| `android/` | `freETarget-Minimalist-Android-0.2.2-beta.1-BuildFix-Source 2.zip` | 0.2.2-beta.1 |

The supplied Windows ZIP included virtual environments, build caches and release artifacts. Its **source files are byte-for-byte identical** to the separate, smaller `freETarget-Minimalist-0.3.11-beta.1-Windows-x64-x86-Clean-Source.zip` that was already available in this session; that compact copy was used to assemble `desktop/windows/` without generated files.

Excluded: `.venv*`, `.build*`, Gradle caches, IDE caches, `build/`, `release/`, `release-x86/`, `local.properties`, generated binaries/APKs/installers, Python caches, OS metadata and signing material. Mac firmware reference ZIP is retained as project reference source. No credentials were found by the basic known-token-pattern scan; this does not replace manual review.

The Mac source includes experimental iOS preview files in its `ios/` subdirectory; they have been preserved but do not represent a validated or published iOS release.

## Repository status

The source projects are available under [desktop/windows/](../desktop/windows/), [desktop/macos/](../desktop/macos/), and [android/](../android/). Windows and Mac snapshots are kept separate to preserve their platform-specific differences.

Build output, installers, APKs, caches, and local configuration are excluded from the source tree. The Mac firmware reference ZIP is not committed; the existing release contains the optional firmware source.

The existing published release remains [v0.3.10-beta.1](https://github.com/DaveStruve/freETarget-Minimalist-Desktop/releases/tag/v0.3.10-beta.1). The committed source versions are newer than the published desktop downloads. No new release or device-test result is implied by the import.

## Release readiness

- [x] Commit the source to GitHub and verify the expected platform directories, application files, assets, and build configurations.
- [ ] Run Windows x64 and x86 build scripts; test both installers, including on 32-bit Windows 10.
- [ ] Run macOS universal2 build; test Intel and Apple Silicon, signing/notarization if required.
- [ ] Build and sign Android APK; test Wi-Fi and USB on actual Android hardware.
- [ ] Confirm actual embedded version names and output filenames.
- [ ] Publish a new prerelease with verified binary assets; keep previous tags/assets unchanged.
