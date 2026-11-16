#!/bin/bash
# Shared macOS Python selection. Sourced by the three .command launchers.
# Python 3.12-3.15 are allowed; native app compatibility must be verified on macOS.
ft_select_python() {
    local candidate version
    local candidates=(
        python3.15 python3.14 python3.13 python3.12 python3
        /opt/homebrew/bin/python3.15 /opt/homebrew/bin/python3.14
        /opt/homebrew/bin/python3.13 /opt/homebrew/bin/python3.12
        /usr/local/bin/python3.15 /usr/local/bin/python3.14
        /usr/local/bin/python3.13 /usr/local/bin/python3.12
        /Library/Frameworks/Python.framework/Versions/3.15/bin/python3.15
        /Library/Frameworks/Python.framework/Versions/3.14/bin/python3.14
        /Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13
        /Library/Frameworks/Python.framework/Versions/3.12/bin/python3.12
    )
    for candidate in "${candidates[@]}"; do
        if command -v "$candidate" >/dev/null 2>&1; then
            version=$("$candidate" -c 'import sys; print("{}.{}".format(*sys.version_info[:2]))' 2>/dev/null) || continue
            case "$version" in
                3.12|3.13|3.14|3.15)
                    FT_PYTHON="$candidate"
                    FT_PYTHON_VERSION="$version"
                    echo "Using Python $version: $(command -v "$candidate")"
                    return 0
                    ;;
            esac
        fi
    done
    echo 'No compatible Python interpreter found (need Python 3.12, 3.13, 3.14 or 3.15).'
    echo 'Try: python3 --version; python3.15 --version'
    echo 'If Python is missing, install it from https://www.python.org/downloads/macos/'
    return 1
}

# Universal2 builds need a Python executable that actually contains both CPU
# slices. Homebrew's Apple Silicon Python is usually arm64-only; a python.org
# macOS universal2 framework installer is the recommended starting point.
ft_select_universal_python() {
    local candidate version executable arches
    local candidates=(
        /Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13
        /Library/Frameworks/Python.framework/Versions/3.12/bin/python3.12
        /Library/Frameworks/Python.framework/Versions/3.14/bin/python3.14
        /Library/Frameworks/Python.framework/Versions/3.15/bin/python3.15
        /usr/local/bin/python3.13 /usr/local/bin/python3.12
        /usr/local/bin/python3.14 /usr/local/bin/python3.15
        python3.13 python3.12 python3.14 python3.15 python3
        /opt/homebrew/bin/python3.13 /opt/homebrew/bin/python3.12
        /opt/homebrew/bin/python3.14 /opt/homebrew/bin/python3.15
    )
    # Optional explicit interpreter. Used by reproducible tests and by users
    # who need to choose one installed universal2 Python over another.
    # When specified, do not silently fall back to a different interpreter.
    if [[ -n "${FT_UNIVERSAL_PYTHON:-}" ]]; then
        candidates=("$FT_UNIVERSAL_PYTHON")
    fi
    if ! command -v lipo >/dev/null 2>&1; then
        echo 'The Apple lipo tool is missing. Install Xcode Command Line Tools: xcode-select --install'
        return 1
    fi
    for candidate in "${candidates[@]}"; do
        if command -v "$candidate" >/dev/null 2>&1; then
            version=$("$candidate" -c 'import sys; print("{}.{}".format(*sys.version_info[:2]))' 2>/dev/null) || continue
            case "$version" in 3.12|3.13|3.14|3.15) ;; *) continue ;; esac
            executable=$("$candidate" -c 'import sys; print(sys.executable)' 2>/dev/null) || continue
            arches=$(lipo -archs "$executable" 2>/dev/null) || continue
            if [[ " $arches " == *" arm64 "* && " $arches " == *" x86_64 "* ]]; then
                FT_PYTHON="$candidate"
                FT_PYTHON_VERSION="$version"
                echo "Using universal2 Python $version: $executable ($arches)"
                return 0
            fi
        fi
    done
    echo 'No universal2 Python found (both arm64 and x86_64 slices are required).'
    echo 'Install Python 3.13 for macOS from https://www.python.org/downloads/macos/'
    echo 'Choose the macOS 64-bit universal2 installer, then rerun BUILD_MAC.command.'
    echo 'For an Apple Silicon-only build instead, use BUILD_MAC_NATIVE.command.'
    return 1
}
