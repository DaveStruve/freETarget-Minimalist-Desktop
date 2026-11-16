# Source import and provenance

This import package was prepared from the three source ZIPs provided by the project owner on 2026-11-16.

| Destination | Supplied ZIP | Version |
| --- | --- | --- |
| `desktop/windows/` | `freETarget-Minimalist-0.3.11-beta.1-Windows-x64-x86-Clean-Source (2).zip` | 0.3.11-beta.1 |
| `desktop/macos/` | `freETarget-Minimalist-0.3.11-beta.1-macOS-Universal-BuildFix-Source 2.zip` | 0.3.11-beta.1 |
| `android/` | `freETarget-Minimalist-Android-0.2.2-beta.1-BuildFix-Source 2.zip` | 0.2.2-beta.1 |

The supplied Windows ZIP included virtual environments, build caches and release artifacts. Its **source files are byte-for-byte identical** to the separate, smaller `freETarget-Minimalist-0.3.11-beta.1-Windows-x64-x86-Clean-Source.zip` that was already available in this session; that compact copy was used to assemble `desktop/windows/` without generated files.

Excluded: `.venv*`, `.build*`, Gradle caches, IDE caches, `build/`, `release/`, `release-x86/`, `local.properties`, generated binaries/APKs/installers, Python caches, OS metadata and signing material. Mac firmware reference ZIP is retained as project reference source. No credentials were found by the basic known-token-pattern scan; this does not replace manual review.

The Mac source includes experimental iOS preview files in its `ios/` subdirectory; they have been preserved but do not represent a validated or published iOS release.

## Import into GitHub

1. Clone the repository in GitHub Desktop: `DaveStruve/freETarget-Minimalist-Desktop`.
2. Extract the import ZIP. Copy its `desktop/`, `android/`, `docs/`, and root `README.md` into the cloned repository folder. Merge the folders; keep the existing `LICENSE`, `.github/`, and `CHANGELOG.md`.
3. In GitHub Desktop, review the changes. The source folders should contain application code and assets, not `.venv`, `.gradle`, APKs or installers.
4. Commit with a message such as `Import Windows, macOS and Android source projects` and click **Push origin**.
5. Verify the source directories on GitHub. The old published release remains unchanged. Build and test before creating the next release.

If GitHub Desktop omits the Mac firmware reference ZIP because of the root `*.zip` ignore rule, either leave it out (the existing firmware release already carries the reference) or force-add it explicitly; do not accidentally include unrelated ZIP archives.

## Release readiness

- [ ] Import the source to GitHub and verify source file counts.
- [ ] Run Windows x64 and x86 build scripts; test both installers, including on 32-bit Windows 10.
- [ ] Run macOS universal2 build; test Intel and Apple Silicon, signing/notarization if required.
- [ ] Build and sign Android APK; test Wi-Fi and USB on actual Android hardware.
- [ ] Confirm actual embedded version names and output filenames.
- [ ] Publish a new prerelease with verified binary assets; keep previous tags/assets unchanged.
