# Ribit Termux Bot 0.2

**Ribit Termux Bot 0.2** is a compact, local-first Matrix bot prototype for Android Termux. It consolidates the existing Termux bot with a vendored **Ribit 2.0 `MockRibit20LLM`** fallback and a **GhostOS–Ribit-inspired loopback-only local LLM client**.

> **Security boundary:** The canonical Ribit mock can return action-plan strings such as `type_text(...)` or `run_command(...)`. Version 0.2 treats every returned plan as **untrusted data**. It extracts only text from one recognized `type_text` envelope and never evaluates, runs, opens, browses, types, or dispatches any returned action.

| Layer | Component | Role in 0.2 | External authority |
| --- | --- | --- | --- |
| Matrix transport | `ribit_termux.matrix_bot` | Authorized text commands and replies | Sends/receives Matrix text only when configured |
| Conversation engine | `ribit_termux.engine` | Connects local memory to providers | No process, web, GUI, or device controls |
| Local memory | `ribit_termux.memory` | SQLite messages, small facts, and word counts | Device-local runtime data only |
| GhostOS-style LLM client | `ribit_termux.providers.LocalOpenAICompatibleClient` | OpenAI-compatible `llama-server` loopback endpoint | `localhost` / loopback only |
| Ribit fallback | Vendored `MockRibit20LLM` | Offline text-generation fallback | Returned actions are filtered and never executed |

## What changed from the original bot

The original credential-bearing defaults were removed. **No Matrix server URL, Matrix ID, password, authorized-user list, or runtime database is committed by 0.2.** Runtime state is kept under `./runtime/` by default and is ignored by Git.

The bot deliberately removes the earlier application-opening and YouTube-opening commands. Supported commands are text and local-memory only.

| Command | Authorized behavior |
| --- | --- |
| `?ask <question>` | Stores the question locally and returns a text-only answer |
| `?teach <text>` | Stores the supplied text in local SQLite memory |
| `?memory` | Shows a compact local memory summary |
| `?status` / `?sys` | Shows memory and provider status; does not run shell commands |
| `?help` | Shows the command list |

All Matrix requests must originate from a full Matrix ID listed in `RIBIT_AUTHORIZED_USERS`. Invitations are ignored by default. Set `RIBIT_AUTO_JOIN_INVITES=true` only if the inviter is an authorized user and you intend the bot to join that room.

## Quick start on Termux

Install the Termux app from a maintained source, then clone this repository and switch to the `0.2` branch:

```bash
git clone https://github.com/rabit232/termux-bot.git
cd termux-bot
git switch 0.2
chmod +x setup_termux.sh scripts/setup_termux.sh
./setup_termux.sh
```

The installer installs Python and the Matrix transport dependency, compiles the prototype, creates a private `.env`, and instructs you to fill it in. First run the offline self-test:

```bash
python ribit_termux.py --self-test
```

The self-test uses the real vendored `MockRibit20LLM` with a temporary runtime directory. It writes no Matrix credentials, does not log in, and does not execute any returned action plan.

## Configure Matrix mode

Copy the example and edit the untracked local file:

```bash
cp example.env .env
chmod 600 .env
nano .env
```

Set `MATRIX_HOMESERVER`, `MATRIX_USER_ID`, `MATRIX_PASSWORD`, and `RIBIT_AUTHORIZED_USERS` to your own private values. The 0.2 Matrix login flow uses the configured account password. Then run:

```bash
python ribit_termux.py
```

**This prototype supports unencrypted Matrix rooms only.** It does not claim Matrix E2EE compatibility. Configure a separate, maintained Matrix E2EE client before using an encrypted room.

## Use a local model server

By default `RIBIT_PROVIDER=auto` first attempts a local OpenAI-compatible endpoint, then falls back to Ribit 2.0’s mock model if the endpoint is unavailable. The endpoint is restricted to `localhost` or a loopback IP address. A typical local configuration is:

```dotenv
RIBIT_PROVIDER=auto
RIBIT_LOCAL_LLM_URL=http://127.0.0.1:8080/v1
RIBIT_LOCAL_LLM_MODEL=your-local-model-id
```

Run your local server separately in Termux, then start the bot. If you want to exercise only the offline fallback, set:

```dotenv
RIBIT_PROVIDER=mock
```

If `RIBIT_PROVIDER=local`, the bot reports a short availability message rather than silently switching providers when the local server is unavailable.

## Existing memory migration

A supplied `neural_memory.db` is treated as private runtime data and is **not included in this branch**. Make a backup before migration. If it uses the same SQLite schema as this prototype, place a copy at `runtime/ribit_memory.db` while the bot is stopped. Otherwise, preserve it separately and use `?teach` or a reviewed export/migration script to add selected information. Never commit a personal memory database.

## Project layout

```text
ribit_termux.py                 Compatibility launcher
ribit_termux/
  cli.py                        CLI and offline smoke test
  config.py                     Environment-only configuration
  engine.py                     Memory/provider orchestration
  matrix_bot.py                 Authorized text-only Matrix transport
  memory.py                     Local SQLite memory
  providers.py                  GhostOS local LLM + safe MockLLM adapter
vendor/ribit_2_0/               Minimal canonical MockRibit20LLM sources
scripts/setup_termux.sh         Termux installation and compilation
example.env                     Safe configuration template
tests/test_core.py              Text-only and local-first tests
```

## Supplied project compatibility

See [COMPATIBILITY.md](COMPATIBILITY.md) for a project-by-project record of what was integrated, what was kept separate, and why the supplied private memory database is not committed. The complete non-executing audit of all 629 analyzed Python files is in [docs/MODULE_INVENTORY.md](docs/MODULE_INVENTORY.md), the integration decision for each major module group is in [docs/MODULE_HARMONY.md](docs/MODULE_HARMONY.md), and the active Termux runtime design is in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Provenance

The vendor subset was copied from [`rabit232/ribit.2.0`](https://github.com/rabit232/ribit.2.0) revision `88f60d941a9b6a3aae57618025f04609f6faa69e`: `mock_llm_wrapper.py`, `knowledge_base.py`, and `response_samples.py`. The package layout and loopback policy were adapted from the supplied `ghostOS-ribit.2.0-0.1` archive’s `libs/ribit_ghostos` integration package. The 0.2 work started from Termux bot revision `3d3c253af21b658e557d166e04d0f61502af572d`.

The vendored subset is intentionally incomplete: optional web-search, Matrix enhancement, robot-control, GUI, and other advanced modules are not included. This keeps the 0.2 prototype local-first and avoids making those capabilities available through the bot.

## Validation

Run the repository checks from the project root:

```bash
python -m compileall -q ribit_termux vendor ribit_termux.py
python -m unittest discover -s tests -v
python ribit_termux.py --self-test
```

The test suite verifies that non-text action plans are not executed, non-loopback LLM URLs are rejected, mock fallback works, and local memory is persisted only in the runtime location.
