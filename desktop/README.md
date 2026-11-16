# freETarget Minimalist — Desktop source

Both desktop source snapshots are **0.3.11-beta.1**, retained separately to avoid overwriting platform-specific application and UI differences.

- `windows/`: Windows x64 and x86 Python/WebView source, tests, PyInstaller and Inno Setup scripts. Start with `README_WINDOWS_BUILDS.md` and `BUILD_AND_INSTALL_BOTH.bat`.
- `macos/`: macOS Intel + Apple Silicon universal2 source, tests, build scripts, and bundled iOS preview source. Start with `BUILD_UNIVERSAL_MAC.md` and `BUILD_MAC.command`.

**Build from the platform folder**: scripts assume `app/`, `tools/`, and other folders are next to them. These are source files, not compiled installers. Hardware testing, Apple signing/notarization, and release builds remain pending.

Some upstream READMEs retain historical version text; `app/version.py`, the 0.3.11 release notes, and current build scripts are the more recent version references. Keep both desktop copies until a separately tested shared-code merge is done.
