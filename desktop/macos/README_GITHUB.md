# macOS Universal 0.3.11-beta.1

Build from this folder on a Mac. See `BUILD_UNIVERSAL_MAC.md` and `BUILD_FIX_README.md` for the universal2 Python requirements and run `bash BUILD_MAC.command`.

`app/version.py` and `RELEASE_NOTES_0.3.11.md` identify this snapshot as **0.3.11-beta.1**. The bundled original `README.md` and some older example output paths mention prior betas and are retained as historical package documentation. Confirm the actual output filename from the build before publishing.

The `ios/` directory is an **experimental iOS/iPadOS preview**, not a published iOS application. Its original layout is retained so its build scripts and Xcode project paths remain intact.

Build artifacts and local Python environments are excluded. Real Intel and Apple Silicon device tests and Apple signing/notarization are still required before claiming a validated public release.
