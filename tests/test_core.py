from __future__ import annotations

import asyncio
import tempfile
import unittest
from pathlib import Path

from ribit_termux.config import Settings
from ribit_termux.engine import RibitEngine
from ribit_termux.matrix_bot import MatrixBot, NIO_AVAILABLE
from ribit_termux.memory import MemoryStore
from ribit_termux.policy import CapabilityPolicy, PermissionDenied
from ribit_termux.providers import (
    LocalOpenAICompatibleClient,
    ProviderError,
    ProviderRouter,
    RibitMockProvider,
    RibitTextOnlyAdapter,
)


class CapabilityPolicyTests(unittest.TestCase):
    def test_high_impact_capabilities_are_denied_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            policy = CapabilityPolicy(workspace=Path(directory))
            self.assertFalse(any(policy.summary().values()))
            with self.assertRaises(PermissionDenied):
                policy.require_process_execution()
            with self.assertRaises(PermissionDenied):
                policy.require_web_access()
            with self.assertRaises(PermissionDenied):
                policy.require_gui_control()
            with self.assertRaises(PermissionDenied):
                policy.require_robot_actuation()


class TextOnlyAdapterTests(unittest.TestCase):
    def test_extracts_known_text_without_executing_anything(self) -> None:
        raw = "type_text('Hello\\nlocal user')\npress_key('enter')\nrun_command('not executed')"
        self.assertEqual(RibitTextOnlyAdapter.extract_display_text(raw), "Hello\nlocal user")

    def test_refuses_non_text_action_plan(self) -> None:
        raw = "run_command('rm -rf /')\ngoal_achieved:unsafe"
        display = RibitTextOnlyAdapter.extract_display_text(raw)
        self.assertIn("no action was executed", display)

    def test_rejects_non_loopback_local_llm(self) -> None:
        with self.assertRaises(ProviderError):
            LocalOpenAICompatibleClient("https://example.com/v1")


class EngineTests(unittest.IsolatedAsyncioTestCase):
    async def test_mock_provider_and_memory_are_local(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            settings = Settings(
                runtime_dir=root,
                db_path=root / "memory.db",
                knowledge_file=root / "knowledge.txt",
                provider="mock",
                local_llm_url="http://127.0.0.1:8080/v1",
                local_llm_model="test-model",
                local_llm_timeout_seconds=1.0,
                matrix_homeserver="",
                matrix_user_id="",
                matrix_password="",
                matrix_device_id="test",
                authorized_users=(),
                auto_join_invites=False,
            )
            memory = MemoryStore(settings.db_path)
            engine = RibitEngine(memory, ProviderRouter(settings))
            try:
                engine.teach(room_id="local", sender="@tester:local", text="My name is Ada")
                result = await engine.answer(
                    room_id="local",
                    sender="@tester:local",
                    prompt="Introduce your local memory approach.",
                )
                self.assertEqual(result.used_model, "ribit-2.0-mock")
                self.assertTrue(result.text)
                self.assertGreaterEqual(memory.status()["messages"], 3)
                self.assertIn("user_name=Ada", memory.summary())
            finally:
                engine.close()

    async def test_cognitive_runtime_builds_local_semantic_context_and_text_plan(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            settings = Settings(
                runtime_dir=root,
                db_path=root / "memory.db",
                knowledge_file=root / "knowledge.txt",
                provider="mock",
                local_llm_url="http://127.0.0.1:8080/v1",
                local_llm_model="test-model",
                local_llm_timeout_seconds=1.0,
                matrix_homeserver="",
                matrix_user_id="",
                matrix_password="",
                matrix_device_id="test",
                authorized_users=(),
                auto_join_invites=False,
            )
            engine = RibitEngine(MemoryStore(settings.db_path), ProviderRouter(settings))
            try:
                engine.teach(room_id="local", sender="@tester:local", text="Termux stores local semantic knowledge in SQLite.")
                result = await engine.answer(
                    room_id="local", sender="@tester:local", prompt="How does Termux local knowledge work?"
                )
                self.assertTrue(result.text)
                mind = engine.mind_status()["runtime"]
                self.assertGreaterEqual(mind["semantic"]["records"], 3)
                self.assertGreaterEqual(mind["knowledge_graph"]["nodes"], 4)
                self.assertGreaterEqual(mind["persistent_cognitive_records"], 3)
                self.assertFalse(mind["policy"]["process_execution"])
                self.assertFalse(mind["policy"]["web_access"])
                plan = engine.plan("Document the local knowledge architecture")
                self.assertEqual([item["order"] for item in plan], [1, 2, 3, 4])
                self.assertIn("not execute", engine.last_review["note"])
            finally:
                engine.close()

    async def test_local_mode_returns_safe_availability_message(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            settings = Settings(
                runtime_dir=root,
                db_path=root / "memory.db",
                knowledge_file=root / "knowledge.txt",
                provider="local",
                local_llm_url="http://127.0.0.1:9/v1",
                local_llm_model="test-model",
                local_llm_timeout_seconds=0.1,
                matrix_homeserver="",
                matrix_user_id="",
                matrix_password="",
                matrix_device_id="test",
                authorized_users=(),
                auto_join_invites=False,
            )
            engine = RibitEngine(MemoryStore(settings.db_path), ProviderRouter(settings))
            try:
                result = await engine.answer(room_id="local", sender="@tester:local", prompt="Hello")
                self.assertEqual(result.used_model, "ghostos-local-llm-unavailable")
                self.assertIn("local LLM is unavailable", result.text)
            finally:
                engine.close()


class MatrixTransportTests(unittest.TestCase):
    def test_matrix_transport_dependency_is_available(self) -> None:
        self.assertTrue(NIO_AVAILABLE)

    def test_command_parser_only_accepts_question_mark_commands(self) -> None:
        self.assertEqual(MatrixBot._command_parts("?ask keep original case"), ("?ask", "keep original case"))
        self.assertIsNone(MatrixBot._command_parts("hello ribit"))


class MockProviderTests(unittest.TestCase):
    def test_mock_returns_text_and_retains_raw_decision_as_data(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = RibitMockProvider(str(Path(directory) / "knowledge.txt")).complete("Introduce yourself")
            self.assertIsNotNone(result.raw_decision)
            self.assertTrue(result.text)


if __name__ == "__main__":
    unittest.main()
