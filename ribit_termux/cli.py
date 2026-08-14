"""Command-line entry point for the Ribit Termux 0.2 prototype."""

from __future__ import annotations

import argparse
import asyncio
import logging
import tempfile
from pathlib import Path

from .config import ConfigurationError, Settings, load_dotenv
from .engine import RibitEngine
from .matrix_bot import MatrixBot
from .memory import MemoryStore
from .providers import ProviderRouter


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ribit Termux 0.2 Matrix bot with text-only Ribit and GhostOS LLM providers.")
    parser.add_argument("--env-file", default=".env", help="Optional local configuration file (default: .env).")
    parser.add_argument("--self-test", action="store_true", help="Run the offline text-only provider and memory smoke test.")
    parser.add_argument("--version", action="version", version="ribit-termux 0.2")
    return parser


def make_engine(settings: Settings) -> RibitEngine:
    return RibitEngine(MemoryStore(settings.db_path), ProviderRouter(settings))


async def self_test() -> int:
    """Exercise the mock path in an isolated temporary runtime directory."""

    with tempfile.TemporaryDirectory(prefix="ribit-termux-self-test-") as directory:
        runtime = Path(directory)
        # The explicit settings avoid reading or modifying a user's Matrix configuration.
        settings = Settings(
            runtime_dir=runtime,
            db_path=runtime / "memory.db",
            knowledge_file=runtime / "mock_knowledge.txt",
            provider="mock",
            local_llm_url="http://127.0.0.1:8080/v1",
            local_llm_model="local-model",
            local_llm_timeout_seconds=2.0,
            matrix_homeserver="",
            matrix_user_id="",
            matrix_password="",
            matrix_device_id="RIBIT_TERMUX_SELF_TEST",
            authorized_users=(),
            auto_join_invites=False,
        )
        engine = make_engine(settings)
        try:
            engine.teach(room_id="local", sender="@tester:local", text="Ribit stores approved local notes in SQLite memory.")
            result = await engine.answer(
                room_id="local",
                sender="@tester:local",
                prompt="Explain the safe local memory workflow.",
            )
            print(f"MODEL: {result.used_model}")
            print(f"REPLY: {result.text}")
            print(f"STATUS: {engine.status()}")
            if result.raw_decision is not None:
                print("RAW_ACTION_PLAN: recorded as data only; not executed")
        finally:
            engine.close()
    return 0


async def run_matrix(settings: Settings) -> int:
    engine = make_engine(settings)
    bot = MatrixBot(settings, engine)
    try:
        await bot.run()
    finally:
        await bot.close()
    return 0


def main() -> int:
    args = build_parser().parse_args()
    load_dotenv(args.env_file)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    if args.self_test:
        return asyncio.run(self_test())
    try:
        settings = Settings.from_environment(require_matrix=True)
    except ConfigurationError as exc:
        raise SystemExit(f"Configuration error: {exc}") from exc
    return asyncio.run(run_matrix(settings))


if __name__ == "__main__":
    raise SystemExit(main())
