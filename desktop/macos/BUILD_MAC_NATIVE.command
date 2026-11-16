#!/bin/bash
# Optional fallback: build only for this Mac's CPU architecture.
set -e
cd "$(dirname "$0")"
trap 'status=$?; if [ "$status" -ne 0 ]; then echo "Build failed. Read the error above and see START_HERE.txt."; read -r -p "Press Return to close..."; fi' EXIT
source "tools/select_python.sh"
ft_select_python
unset FREETARGET_MAC_ARCH
"$FT_PYTHON" tools/mac_tasks.py build
