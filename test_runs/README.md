# Test-Run Records

Run `./scripts/run_tests.sh` from the repository root to perform the standard local quality gates and save a timestamped Markdown report in this directory. The script runs Python compilation, the unit-test suite, the offline self-test, and the whitespace check.

| Artifact | Version-control treatment | Purpose |
| --- | --- | --- |
| `YYYYMMDDTHHMMSSZ.md` | Tracked when intentionally committed | Reproducible human-readable test result. |
| `latest.md` | Tracked | Copy of the most recently committed test report. |
| `YYYYMMDDTHHMMSSZ.log` | Ignored | Full local command output, which may be noisy and machine-specific. |

> Test runs are local-only. They do not start Matrix, call a non-loopback model, or execute output from the Ribit MockLLM.
