# Desktop application

This folder is reserved for the complete desktop application source, assets, tests, build scripts, and installer configurations.

**Status: source import pending. This folder is not yet buildable.**

Import the contents of the clean Windows x64/x86 source package into this folder, preserving its internal paths. Do not reorganize scripts, assets, or installer files until their relative path assumptions have been checked.

The prepared package is:
`freETarget-Minimalist-0.3.11-beta.1-Windows-x64-x86-Clean-Source.zip`

The package's existing instructions are the starting point for local compilation. Build scripts described in the prior package handoff include `BUILD_AND_INSTALL_X64.bat`, `BUILD_AND_INSTALL_X86.bat`, and `BUILD_AND_INSTALL_BOTH.bat`; these are not present here until import and must be checked against the actual archive.

Reconcile the macOS v0.3.10-beta.1 source package with the imported desktop tree separately. Preserve its platform-specific build configuration, and review application code differences before combining versions.

See [source import](../docs/SOURCE_IMPORT.md) and [releasing](../docs/RELEASING.md).
