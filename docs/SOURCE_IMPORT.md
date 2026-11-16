# Importing the application sources

The repository setup is in place. Application code has not yet been imported from the existing source ZIPs.

## Packages identified

| Destination | Source package | Version |
| --- | --- | --- |
| `desktop/` | `freETarget-Minimalist-0.3.11-beta.1-Windows-x64-x86-Clean-Source.zip` | 0.3.11-beta.1 |
| `android/` | `freETarget-Minimalist-Android-0.2.0-beta.1-Source.zip` | 0.2.0-beta.1 |
| Reconcile with `desktop/` | `freETarget_Minimalist_0.3.10-beta.1_macOS_Universal_BuildFix_Source.zip` | 0.3.10-beta.1 |

These are source archives. They are not finished Windows installers, a macOS application download, or an Android APK.

## Import procedure

1. Create a branch from the current `main`.
2. Extract each package locally and inspect its top-level application folder.
3. Copy the desktop project contents into `desktop/` and Android project contents into `android/`. Avoid adding an extra archive-name folder around each project. Retain existing package documentation alongside these setup notes.
4. Preserve internal paths, icons, assets, tests, dependency files, and build scripts. Include Gradle wrapper files when supplied.
5. Exclude virtual environments, generated builds, installers, APKs, local SDK configuration, signing keys, credentials, logs, and personal shooter data. Inspect the staged changes: `.gitignore` cannot detect every personal file or credential.
6. Compare the macOS source with the desktop source before importing its build scripts. Resolve version differences explicitly.
7. Build and test each imported platform using its package instructions. Record actual requirements, script paths, output filenames, and validation results.
8. Update the root and platform READMEs to replace pending notices with verified build instructions, then merge the import.

## Before the next release

- [ ] Desktop source and both Windows installer configurations committed.
- [ ] Android project committed.
- [ ] macOS source differences reconciled, or its existing release clearly listed as unchanged.
- [ ] Windows x64 installer built and tested.
- [ ] Windows x86 installer tested on Windows 10 32-bit.
- [ ] Signed Android release APK tested on a device over Wi-Fi.
- [ ] Real platform versions and filenames recorded in release notes.
- [ ] Release tag points to the source commit used for the new builds.

Until import is complete, GitHub's automatic source archives contain only the repository setup files and cannot build the application.
