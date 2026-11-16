#!/bin/bash
set -e
cd "$(dirname "$0")"
trap 'status=$?; if [ "$status" -ne 0 ]; then echo "Build failed. Read the error above and see BUILD_UNIVERSAL_MAC.md."; read -r -p "Press Return to close..."; fi' EXIT
source "tools/select_python.sh"
ft_select_universal_python
export FREETARGET_MAC_ARCH=universal2
"$FT_PYTHON" tools/mac_tasks.py build
