#!/usr/bin/env python3
"""Compatibility launcher for Ribit Termux 0.2.

Use ``python ribit_termux.py --self-test`` for an offline smoke test, or run it
with Matrix settings supplied through an untracked ``.env`` file.
"""

from ribit_termux.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
