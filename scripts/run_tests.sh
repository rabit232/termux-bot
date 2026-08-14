#!/usr/bin/env bash
# Run the reproducible local quality gates and save a Markdown report in test_runs/.
# This script does not start Matrix, contact a remote model, or execute LLM output.
set -u -o pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

mkdir -p test_runs
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
REPORT="test_runs/${STAMP}.md"
RAW_LOG="test_runs/${STAMP}.log"
LATEST="test_runs/latest.md"

status=0
{
  echo "# Ribit Termux Test Run"
  echo
  echo "| Field | Value |"
  echo "| --- | --- |"
  echo "| Started (UTC) | $(date -u +%Y-%m-%dT%H:%M:%SZ) |"
  echo "| Git revision | $(git rev-parse --short HEAD 2>/dev/null || echo unavailable) |"
  echo "| Python | $(python3 --version 2>&1) |"
  echo
  echo '```text'
  echo '$ python3 -m compileall -q ribit_termux vendor ribit_termux.py'
  python3 -m compileall -q ribit_termux vendor ribit_termux.py || status=1
  echo '$ python3 -m unittest discover -s tests -v'
  python3 -m unittest discover -s tests -v || status=1
  echo '$ python3 ribit_termux.py --self-test'
  python3 ribit_termux.py --self-test || status=1
  echo '$ git diff --check'
  git diff --check || status=1
  echo '```'
  echo
  if [ "$status" -eq 0 ]; then
    echo '**Result:** PASS'
  else
    echo '**Result:** FAIL'
  fi
  echo
  echo "| Field | Value |"
  echo "| --- | --- |"
  echo "| Finished (UTC) | $(date -u +%Y-%m-%dT%H:%M:%SZ) |"
  echo "| Exit status | $status |"
} > "$REPORT" 2>&1

cp "$REPORT" "$RAW_LOG"
cp "$REPORT" "$LATEST"
printf 'Raw test output: %s\nReport: %s\n' "$RAW_LOG" "$REPORT"
exit "$status"
