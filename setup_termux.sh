#!/data/data/com.termux/files/usr/bin/bash
# Backward-compatible launcher for the Ribit Termux 0.2 installer.
set -euo pipefail
exec "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)/scripts/setup_termux.sh" "$@"
