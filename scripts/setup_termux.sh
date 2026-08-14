#!/data/data/com.termux/files/usr/bin/bash
# Install and compile the Ribit Termux 0.2 prototype on Android Termux.
set -euo pipefail

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$ROOT_DIR"

pkg update -y
pkg install -y python git
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m compileall -q ribit_termux vendor ribit_termux.py

if [ ! -f .env ]; then
  cp example.env .env
  chmod 600 .env
  printf '%s\n' "Created .env with restrictive permissions. Fill in your Matrix settings before starting the bot."
fi

printf '%s\n' "Installation and compilation complete. Run: python ribit_termux.py --self-test"
