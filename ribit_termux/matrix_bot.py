"""Matrix transport for Ribit Termux 0.2.

This transport sends display text only. It intentionally does not dispatch
commands suggested by a model, open Android applications, browse the web, or
control hardware. Encrypted-room support is not part of this prototype.
"""

from __future__ import annotations

import logging
from typing import Any

from .config import Settings
from .engine import RibitEngine

logger = logging.getLogger(__name__)

try:
    from nio import AsyncClient, AsyncClientConfig, InviteMemberEvent, LoginResponse, MatrixRoom, RoomMessageText

    NIO_AVAILABLE = True
except ImportError:  # pragma: no cover - covered by the explicit availability guard
    AsyncClient = AsyncClientConfig = InviteMemberEvent = LoginResponse = MatrixRoom = RoomMessageText = Any  # type: ignore[misc,assignment]
    NIO_AVAILABLE = False


class MatrixBot:
    """Small Matrix bot that exposes only safe text and memory commands."""

    def __init__(self, settings: Settings, engine: RibitEngine) -> None:
        if not NIO_AVAILABLE:
            raise RuntimeError("matrix-nio is not installed. Run: python -m pip install -r requirements.txt")
        self.settings = settings
        self.engine = engine
        config = AsyncClientConfig(encryption_enabled=False)
        self.client = AsyncClient(
            settings.matrix_homeserver,
            settings.matrix_user_id,
            device_id=settings.matrix_device_id,
            store_path=str(settings.runtime_dir / "matrix_store"),
            config=config,
        )
        self.client.add_event_callback(self.message_callback, RoomMessageText)
        self.client.add_event_callback(self.invite_callback, InviteMemberEvent)

    def is_authorized(self, user_id: str) -> bool:
        return user_id in self.settings.authorized_users

    @staticmethod
    def _command_parts(message: str) -> tuple[str, str] | None:
        clean = " ".join(message.split())
        if not clean.startswith("?"):
            return None
        name, _, arguments = clean.partition(" ")
        return name.casefold(), arguments.strip()

    async def message_callback(self, room: MatrixRoom, event: RoomMessageText) -> None:
        if event.sender == self.settings.matrix_user_id:
            return
        message = " ".join(event.body.split())
        if not message:
            return
        parsed = self._command_parts(message)
        mentioned = self.settings.matrix_user_id.casefold() in message.casefold() or "ribit" in message.casefold()
        if parsed is None and not mentioned:
            return
        if not self.is_authorized(event.sender):
            await self.send_message(room.room_id, "This bot accepts requests only from configured authorized Matrix IDs.")
            return
        if parsed is not None:
            await self.handle_command(room.room_id, event.sender, parsed[0], parsed[1])
            return
        await self.reply(room.room_id, event.sender, message)

    async def handle_command(self, room_id: str, sender: str, command: str, arguments: str) -> None:
        if command == "?help":
            await self.send_message(
                room_id,
                "Commands: ?ask <question>, ?teach <text>, ?memory, ?mind, ?plan <goal>, ?status, ?sys, ?help. "
                "All replies and plans are text-only; model action plans are never executed.",
            )
        elif command == "?ask":
            if not arguments:
                await self.send_message(room_id, "Usage: ?ask <question>")
            else:
                await self.reply(room_id, sender, arguments)
        elif command == "?teach":
            if not arguments:
                await self.send_message(room_id, "Usage: ?teach <text>")
            else:
                self.engine.teach(room_id=room_id, sender=sender, text=arguments)
                await self.send_message(room_id, "Saved the text to local memory.")
        elif command == "?memory":
            await self.send_message(room_id, self.engine.memory.summary())
        elif command == "?mind":
            mind = self.engine.mind_status()
            runtime = mind["runtime"]
            semantic = runtime["semantic"]
            graph = runtime["knowledge_graph"]
            style = runtime["persona"]
            policy = runtime["policy"]
            await self.send_message(
                room_id,
                "Mind status: "
                f"semantic_records={semantic['records']}; graph_nodes={graph['nodes']}; graph_edges={graph['edges']}; "
                f"tone={style['emotion']}; cognition_records={runtime['persistent_cognitive_records']}; "
                f"process_execution={policy['process_execution']}; web_access={policy['web_access']}; "
                f"gui_control={policy['gui_control']}; robot_actuation={policy['robot_actuation']}.",
            )
        elif command == "?plan":
            if not arguments:
                await self.send_message(room_id, "Usage: ?plan <goal>")
            else:
                plan = self.engine.plan(arguments)
                text = "\n".join(f"{item['order']}. {item['title']}: {item['purpose']}" for item in plan)
                await self.send_message(room_id, "Text-only plan; no steps are executed:\n" + text)
        elif command in {"?status", "?sys"}:
            await self.send_message(room_id, self.engine.status())
        else:
            await self.send_message(room_id, "Unknown command. Use ?help.")

    async def reply(self, room_id: str, sender: str, prompt: str) -> None:
        await self.client.room_typing(room_id, typing_state=True)
        try:
            result = await self.engine.answer(room_id=room_id, sender=sender, prompt=prompt)
        finally:
            await self.client.room_typing(room_id, typing_state=False)
        await self.send_message(room_id, result.text)

    async def send_message(self, room_id: str, message: str) -> None:
        try:
            await self.client.room_send(
                room_id=room_id,
                message_type="m.room.message",
                content={"msgtype": "m.text", "body": message},
            )
        except Exception as exc:  # pragma: no cover - network-facing operational safeguard
            logger.error("Unable to send Matrix message: %s", exc)

    async def invite_callback(self, room: MatrixRoom, event: InviteMemberEvent) -> None:
        if not self.settings.auto_join_invites:
            logger.info("Invitation to %s ignored because RIBIT_AUTO_JOIN_INVITES is disabled.", room.room_id)
            return
        if not self.is_authorized(event.sender):
            logger.warning("Ignoring invitation from unauthorized Matrix ID: %s", event.sender)
            return
        try:
            await self.client.join(room.room_id)
        except Exception as exc:  # pragma: no cover - network-facing operational safeguard
            logger.error("Unable to join invited Matrix room: %s", exc)

    async def run(self) -> None:
        response = await self.client.login(self.settings.matrix_password)
        if not isinstance(response, LoginResponse):
            raise RuntimeError(f"Matrix login failed: {response}")
        logger.info("Logged in as %s", self.settings.matrix_user_id)
        await self.client.sync_forever(timeout=30000, full_state=False)

    async def close(self) -> None:
        try:
            await self.client.close()
        finally:
            self.engine.close()
