# freETarget Minimalist 0.3.11-beta.1 — Windows x64 and x86 source

This is a clean **source** distribution, not precompiled installers. Build on Windows 11 x64.

## Prerequisites
- Python 3.12 64-bit and Python 3.12 32-bit (both registered with the Python launcher `py`)
- Inno Setup 6 for Setup.exe generation
- Internet access for Python package installation

## One-click builds
- `BUILD_AND_INSTALL_X64.bat`: builds x64 app and installer
- `BUILD_AND_INSTALL_X86.bat`: builds x86 app and installer
- `BUILD_AND_INSTALL_BOTH.bat`: builds both sequentially

## Outputs
- x64 portable: `release/freETargetMinimalist/` and `release/*-Windows-x64.zip`
- x64 installer: `release/installer/`
- x86 portable: `release-x86/freETargetMinimalist/` and `release-x86/*-Windows-x86.zip`
- x86 installer: `release-x86/installer/`

The two architectures are built separately. The x86 build checks that its EXE and WebView2 loader are 32-bit. If this check fails, the installer will not be generated. The x64 installer restricts installation to compatible 64-bit Windows; the x86 installer supports 32-bit Windows.

**Not yet compiled or tested on Windows.** Test on Windows 10 32-bit before publishing compatibility claims. Keep each installer in its own release asset.
