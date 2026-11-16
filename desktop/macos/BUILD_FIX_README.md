# Universal Mac Build — Selector Test Fix 2

This package fixes two build-test issues in the earlier Universal source packages:

1. A macOS test could recursively start another build. This was fixed in BuildFix.
2. The `test_shell_python_selector_finds_two_slices_only` test used a fake Python 3.13 executable but the selector found a real universal2 Python 3.15 at an absolute system path first. This incorrectly failed the test despite the installed Python being valid. This package adds an explicit `FT_UNIVERSAL_PYTHON` override so the test can isolate its fake interpreter on any Mac. The normal production interpreter selection is unchanged.

## Build

Extract this ZIP, then run:

```bash
cd ~/Downloads/freETarget_Minimalist_0.3.5-beta.1_macOS_Universal_BuildFix2
bash BUILD_MAC.command
```

The build will install dependencies, run unit tests, package a universal2 `.app`, then verify both `arm64` and `x86_64` slices in collected Mach-O binaries. A successful build creates `release/mac/freETarget Minimalist.app` and `release/mac/freETarget-Minimalist-0.3.5-beta.1-universal2.zip`.

The existing Python 3.15.2 universal2 installation is acceptable for attempting this build; the reported failure was the test fixture, not a dependency installation failure. Actual macOS packaging and runtime still need validation on the user's Mac.

No application or scoring behavior has changed.
