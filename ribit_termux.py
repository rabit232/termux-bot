#!/usr/bin/env python3
"""
Ribit Termux Bot - Matrix + Mock Model + Memory + Gemma Fallback
Enhanced version with fixed Termux paths and app control.
"""

import argparse
import asyncio
import json
import logging
import os
import random
import re
import sqlite3
import subprocess
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import aiohttp

try:
    from nio import (
        AsyncClient,
        AsyncClientConfig,
        InviteMemberEvent,
        LoginResponse,
        MatrixRoom,
        MegolmEvent,
        RoomMessageText,
    )
    NIO_AVAILABLE = True
except Exception:
    AsyncClient = None  # type: ignore
    AsyncClientConfig = None  # type: ignore
    InviteMemberEvent = object  # type: ignore
    LoginResponse = object  # type: ignore
    MatrixRoom = object  # type: ignore
    MegolmEvent = object  # type: ignore
    RoomMessageText = object  # type: ignore
    NIO_AVAILABLE = False

try:
    import psutil  # optional
except Exception:
    psutil = None

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ribit-termux")

WORD_RE = re.compile(r"\b[\w'-]+\b", re.UNICODE)
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
JOIN_RE = re.compile(r"\s+")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def normalize_text(text: str) -> str:
    return JOIN_RE.sub(" ", text.strip())


def tokenize(text: str) -> List[str]:
    words = WORD_RE.findall(text.lower())
    stop = {
        "the", "a", "an", "and", "or", "but", "if", "then", "so", "to", "of", "in", "on", "at",
        "for", "with", "is", "are", "was", "were", "be", "been", "am", "it", "this", "that", "these",
        "those", "i", "you", "he", "she", "we", "they", "me", "my", "your", "our", "their", "as",
        "by", "from", "not", "do", "does", "did", "can", "could", "would", "should", "have", "has",
        "had", "will", "just", "too", "very", "more", "most", "less", "least", "about", "into", "over",
        "under", "again", "new", "old"
    }
    return [w for w in words if w not in stop and len(w) > 1]


@dataclass
class GenerationResult:
    text: str
    used_model: str
    confidence: float = 0.5
    fallback_used: bool = False


class RibitMemoryDB:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self) -> None:
        cur = self.conn.cursor()
        cur.executescript(
            """
            PRAGMA journal_mode=WAL;
            PRAGMA synchronous=NORMAL;

            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                room_id TEXT,
                sender TEXT,
                role TEXT NOT NULL,
                text TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS words (
                word TEXT PRIMARY KEY,
                count INTEGER NOT NULL DEFAULT 0,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS samples (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                source TEXT NOT NULL,
                text TEXT NOT NULL,
                words TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS facts (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                source TEXT NOT NULL,
                ts TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_samples_ts ON samples(ts);
            CREATE INDEX IF NOT EXISTS idx_messages_ts ON messages(ts);
            """
        )
        self.conn.commit()

    def close(self) -> None:
        try:
            self.conn.close()
        except Exception:
            pass

    def save_message(self, room_id: Optional[str], sender: Optional[str], role: str, text: str) -> None:
        self.conn.execute(
            "INSERT INTO messages(ts, room_id, sender, role, text) VALUES(?,?,?,?,?)",
            (now_iso(), room_id, sender, role, text),
        )
        self.conn.commit()

    def learn_text(self, text: str, source: str = "chat", save_sample: bool = True) -> None:
        clean = normalize_text(text)
        if not clean:
            return

        words = tokenize(clean)
        ts = now_iso()
        cur = self.conn.cursor()

        for word in words:
            cur.execute(
                """
                INSERT INTO words(word, count, first_seen, last_seen)
                VALUES(?,?,?,?)
                ON CONFLICT(word) DO UPDATE SET
                    count = count + 1,
                    last_seen = excluded.last_seen
                """,
                (word, 1, ts, ts),
            )

        if save_sample:
            cur.execute(
                "INSERT INTO samples(ts, source, text, words) VALUES(?,?,?,?)",
                (ts, source, clean, json.dumps(words, ensure_ascii=False)),
            )

        for key, value in self._extract_facts(clean):
            cur.execute(
                """
                INSERT INTO facts(key, value, source, ts)
                VALUES(?,?,?,?)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    source = excluded.source,
                    ts = excluded.ts
                """,
                (key, value, source, ts),
            )

        self.conn.commit()

    def forget_word(self, word: str) -> None:
        self.conn.execute("DELETE FROM words WHERE word = ?", (word.lower(),))
        self.conn.commit()

    def _extract_facts(self, text: str) -> List[Tuple[str, str]]:
        facts: List[Tuple[str, str]] = []
        lowered = text.lower()
        patterns = [
            (r"^\s*my name is ([^.!?]+)", "user_name"),
            (r"^\s*i am ([^.!?]+)", "user_identity"),
            (r"^\s*i like ([^.!?]+)", "user_like"),
            (r"^\s*i love ([^.!?]+)", "user_love"),
            (r"^\s*(.+?)\s+is\s+(.+)$", None),
        ]
        for pattern, fixed_key in patterns:
            m = re.match(pattern, lowered, re.IGNORECASE)
            if not m:
                continue
            if fixed_key:
                facts.append((fixed_key, normalize_text(m.group(1))))
            else:
                left = normalize_text(m.group(1))
                right = normalize_text(m.group(2))
                if 1 <= len(left.split()) <= 6 and 1 <= len(right.split()) <= 16:
                    facts.append((f"fact:{left}", right))
            break
        return facts

    def stats(self) -> Dict[str, Any]:
        cur = self.conn.cursor()
        words = cur.execute("SELECT COUNT(*) AS c FROM words").fetchone()["c"]
        samples = cur.execute("SELECT COUNT(*) AS c FROM samples").fetchone()["c"]
        messages = cur.execute("SELECT COUNT(*) AS c FROM messages").fetchone()["c"]
        facts = cur.execute("SELECT COUNT(*) AS c FROM facts").fetchone()["c"]
        return {"words": words, "samples": samples, "messages": messages, "facts": facts}

    def latest_words(self, limit: int = 12) -> List[Tuple[str, int]]:
        cur = self.conn.cursor()
        rows = cur.execute(
            "SELECT word, count FROM words ORDER BY last_seen DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [(r["word"], int(r["count"])) for r in rows]

    def get_facts(self, limit: int = 12) -> List[Tuple[str, str]]:
        cur = self.conn.cursor()
        rows = cur.execute(
            "SELECT key, value FROM facts ORDER BY ts DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [(r["key"], r["value"]) for r in rows]

    def get_relevant_samples(self, query: str, limit: int = 5) -> List[str]:
        qwords = set(tokenize(query))
        if not qwords:
            cur = self.conn.cursor()
            rows = cur.execute(
                "SELECT text FROM samples ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
            return [r["text"] for r in rows]

        cur = self.conn.cursor()
        rows = cur.execute(
            "SELECT text, words FROM samples ORDER BY id DESC LIMIT 500"
        ).fetchall()

        scored: List[Tuple[float, str]] = []
        for row in rows:
            sample_words = set(json.loads(row["words"]))
            if not sample_words:
                continue
            overlap = len(qwords & sample_words)
            if overlap == 0:
                continue
            score = overlap / max(1, len(qwords | sample_words))
            scored.append((score, row["text"]))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [text for _, text in scored[:limit]]

    def build_context(self, query: str, max_items: int = 5) -> Dict[str, Any]:
        facts = self.get_facts(limit=max_items)
        samples = self.get_relevant_samples(query, limit=max_items)
        words = self.latest_words(limit=max_items * 2)
        return {"facts": facts, "samples": samples, "words": words}

    def phrase_from_history(self, min_words: int = 4, max_words: int = 12) -> Optional[str]:
        cur = self.conn.cursor()
        rows = cur.execute(
            "SELECT text FROM messages WHERE role='user' ORDER BY id DESC LIMIT 120"
        ).fetchall()
        candidates: List[str] = []
        for row in rows:
            text = row["text"]
            for sent in SENTENCE_SPLIT_RE.split(text):
                s = normalize_text(sent)
                if not s:
                    continue
                count = len(tokenize(s))
                if min_words <= count <= max_words:
                    candidates.append(s)
        if not candidates:
            return None
        return random.choice(candidates[: min(20, len(candidates))])


class MockRibitModel:
    def __init__(self, memory: RibitMemoryDB):
        self.memory = memory
        self.failure_rate = float(os.getenv("RIBIT_MOCK_FAILURE_RATE", "0.08"))

    def _style(self, prompt: str) -> str:
        prompt_l = prompt.lower()
        if any(k in prompt_l for k in ("how", "why", "what", "when", "where")):
            return "explainer"
        if any(k in prompt_l for k in ("code", "bug", "fix", "error", "traceback", "matrix", "sqlite")):
            return "technical"
        if any(k in prompt_l for k in ("joke", "funny", "laugh")):
            return "playful"
        return "balanced"

    def generate(self, prompt: str) -> GenerationResult:
        if random.random() < self.failure_rate:
            raise RuntimeError("Mock model confidence too low")

        prompt = normalize_text(prompt)
        context = self.memory.build_context(prompt, max_items=4)
        facts = context["facts"]
        samples = context["samples"]
        words = context["words"]

        style = self._style(prompt)
        prompt_words = tokenize(prompt)

        if samples:
            source_line = random.choice(samples)
        else:
            source_line = self.memory.phrase_from_history() or "I am still building memory."

        learned_hint = ""
        if facts:
            k, v = random.choice(facts)
            learned_hint = f" I remember {k.replace(':', ' ')} = {v}."
        elif words:
            top_word = words[0][0]
            learned_hint = f" I have been seeing the word '{top_word}' often."

        if style == "technical":
            text = f"Ribit response: I found related memory and I think the best path is to keep it simple. Relevant sample: {source_line}.{learned_hint}"
        elif style == "explainer":
            text = f"From the memory I have, the strongest clue is: {source_line}.{learned_hint} I can answer more precisely if you give me one target."
        elif style == "playful":
            text = f"That gave me a grin. I pulled this from memory: {source_line}.{learned_hint} Ribit is trying to stay clever without pretending to know everything."
        else:
            text = f"I connected this to memory: {source_line}.{learned_hint} My response is still built from learned history, words, and stored samples."

        if prompt_words and random.random() < 0.4:
            text += f" I noticed: {random.choice(prompt_words)}."
        return GenerationResult(text=text, used_model="mock", confidence=0.74)


class GemmaFallbackClient:
    def __init__(self, url: str, model: str, timeout: int = 60):
        self.url = url
        self.model = model
        self.timeout = timeout

    async def generate(self, prompt: str, context: Dict[str, Any]) -> GenerationResult:
        # Note: 'system' role is removed here to avoid Gemma/Jinja template issues in Termux llama-server.
        memory_blob = json.dumps(context, ensure_ascii=False)
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": f"You are Ribit, a concise but helpful Matrix bot. Memory context:\n{memory_blob}\n\nUser message:\n{prompt}"},
            ],
            "temperature": 0.6,
            "top_p": 0.9,
            "max_tokens": 250,
        }

        timeout = aiohttp.ClientTimeout(total=self.timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(self.url, json=payload) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"Gemma server returned HTTP {resp.status}: {await resp.text()}")
                data = await resp.json()
                try:
                    text = data["choices"][0]["message"]["content"]
                except Exception as exc:
                    raise RuntimeError(f"Unexpected Gemma response shape: {data}") from exc
                return GenerationResult(text=text, used_model="gemma", fallback_used=True, confidence=0.88)


class RibitBrain:
    def __init__(self, db_path: str):
        self.memory = RibitMemoryDB(db_path)
        self.mock = MockRibitModel(self.memory)
        self.gemma = GemmaFallbackClient(
            url=os.getenv("RIBIT_GEMMA_URL", "http://127.0.0.1:8080/v1/chat/completions"),
            model=os.getenv("RIBIT_GEMMA_MODEL", "gemma-2-2b-it-abliterated-Q4_K_M.gguf"),
        )
        self.trigger_words = self._load_trigger_words()

    def _load_trigger_words(self) -> List[str]:
        raw = os.getenv("RIBIT_TRIGGER_WORDS", "ribit,megabite,crystal,matrix,termux,knowledge,learn")
        return [x.strip().lower() for x in raw.split(",") if x.strip()]

    def learn_turn(self, room_id: Optional[str], sender: Optional[str], text: str, role: str) -> None:
        self.memory.save_message(room_id, sender, role, text)
        self.memory.learn_text(text, source=role, save_sample=True)

    async def generate(self, prompt: str) -> GenerationResult:
        context = self.memory.build_context(prompt, max_items=5)
        try:
            result = self.mock.generate(prompt)
            if result.confidence < 0.55 or len(result.text.split()) < 4:
                raise RuntimeError("Mock output too weak")
            return result
        except Exception as mock_exc:
            logger.info("Mock model failed or underperformed: %s", mock_exc)
            try:
                return await self.gemma.generate(prompt, context)
            except Exception as gemma_exc:
                logger.error("Gemma fallback failed: %s", gemma_exc)
                fallback = self._last_resort_reply(prompt, context)
                return GenerationResult(text=fallback, used_model="fallback", fallback_used=True, confidence=0.35)

    def _last_resort_reply(self, prompt: str, context: Dict[str, Any]) -> str:
        samples = context.get("samples") or []
        facts = context.get("facts") or []
        if samples:
            return f"I could not use the main model, but memory suggests: {samples[0]}"
        if facts:
            k, v = facts[0]
            return f"I could not use the main model, but I still remember {k} = {v}."
        return "I could not use the main model, but I am still here and learning from the conversation."

    def stats_line(self) -> str:
        st = self.memory.stats()
        return f"words={st['words']} samples={st['samples']} messages={st['messages']} facts={st['facts']}"

    def recent_summary(self) -> str:
        words = self.memory.latest_words(8)
        facts = self.memory.get_facts(5)
        pieces = []
        if words:
            pieces.append("top words: " + ", ".join(f"{w}({c})" for w, c in words[:5]))
        if facts:
            pieces.append("facts: " + "; ".join(f"{k}={v}" for k, v in facts[:3]))
        return " | ".join(pieces) if pieces else "no memory yet"


class RibitTermuxBot:
    def __init__(self, homeserver: str, user_id: str, password: str, device_id: str, db_path: str):
        if not NIO_AVAILABLE:
            raise RuntimeError("matrix-nio is not installed.")
        config = AsyncClientConfig(encryption_enabled=False)
        self.client = AsyncClient(homeserver, user_id, device_id=device_id, store_path="ribit_store", config=config)
        self.password = password
        self.user_id = user_id
        self.brain = RibitBrain(db_path)

        self.authorized_users = {
            uid.strip() for uid in os.getenv(
                "RIBIT_AUTHORIZED_USERS",
                f"{user_id},@merkaba:stargazypie.xyz,@ribit:envs.net,@rabit232:envs.net"
            ).split(",") if uid.strip()
        }

        self.failed_auth_attempts: Dict[str, int] = {}
        self.last_autonomous_response: Optional[datetime] = None
        self.autonomous_triggers = [x.strip().lower() for x in os.getenv(
            "RIBIT_AUTONOMOUS_TRIGGERS",
            "matrix,termux,ai,knowledge,learn,remember,robot,bot"
        ).split(",") if x.strip()]

        self.client.add_event_callback(self.message_callback, RoomMessageText)
        self.client.add_event_callback(self.encrypted_callback, MegolmEvent)
        self.client.add_event_callback(self.invite_callback, InviteMemberEvent)

    async def encrypted_callback(self, room: MatrixRoom, event: MegolmEvent):
        await self.send_message(room.room_id, "⚠️ I cannot read encrypted messages in this mode.")

    def should_respond_autonomously(self, message: str) -> bool:
        if self.last_autonomous_response and (datetime.now(timezone.utc) - self.last_autonomous_response).total_seconds() < 30:
            return False
        if any(trigger in message.lower() for trigger in self.autonomous_triggers):
            if random.random() < 0.70:
                self.last_autonomous_response = datetime.now(timezone.utc)
                return True
        return False

    async def message_callback(self, room: MatrixRoom, event: RoomMessageText):
        if event.sender == self.user_id:
            return

        message = normalize_text(event.body)
        sender = event.sender

        self.brain.learn_turn(room.room_id, sender, message, role="user")
        logger.info("Heard from %s: %s", sender, message)

        lower = message.lower()
        if lower.startswith("?") or lower.startswith("!ribit"):
            await self.handle_command(room, event, lower)
            return

        should_respond = (
            self.user_id.lower() in lower
            or "ribit" in lower
            or self.should_respond_autonomously(lower)
        )
        if should_respond:
            await self.reply_with_model(room.room_id, message)

    async def reply_with_model(self, room_id: str, prompt: str) -> None:
        await self.client.room_typing(room_id, typing_state=True)
        try:
            result = await self.brain.generate(prompt)
            reply = result.text
            self.brain.learn_turn(room_id, self.user_id, reply, role=f"bot:{result.used_model}")
        finally:
            await self.client.room_typing(room_id, typing_state=False)

        await self.send_message(room_id, reply)

    async def handle_command(self, room: MatrixRoom, event: RoomMessageText, command: str):
        sender = event.sender
        if sender not in self.authorized_users:
            await self.handle_unauthorized(room, sender)
            return

        if command.startswith("?help"):
            await self.send_message(
                room.room_id,
                "🤖 Ribit commands: ?ask [question], ?teach [text], ?memory, ?status, ?sys, ?open [app], ?play_youtube [url]"
            )
        elif command.startswith("?status"):
            await self.send_message(room.room_id, f"Memory status: {self.brain.stats_line()} | {self.brain.recent_summary()}")
        elif command.startswith("?memory"):
            await self.send_message(room.room_id, self.brain.recent_summary())
        elif command.startswith("?sys"):
            await self.get_sys_status(room)
        elif command.startswith("?teach "):
            teach_text = command[len("?teach "):].strip()
            if teach_text:
                self.brain.learn_turn(room.room_id, sender, teach_text, role="manual_teach")
                await self.send_message(room.room_id, "✅ Learned that sample and saved it.")
            else:
                await self.send_message(room.room_id, "Give me text after ?teach.")
        elif command.startswith("?ask "):
            query = command[5:].strip()
            await self.reply_with_model(room.room_id, query)
        elif command.startswith("?open "):
            app = command.split(" ", 1)[1].strip()
            await self.open_app(room, app)
        elif command.startswith("?play_youtube "):
            video_url = command[len("?play_youtube "):].strip()
            await self.send_message(room.room_id, f"▶️ Opening: {video_url}")
            subprocess.Popen(["termux-open", video_url], shell=False)
        else:
            await self.send_message(room.room_id, "Unknown command. Try ?help")

    async def open_app(self, room: MatrixRoom, app: str):
        try:
            await self.send_message(room.room_id, f"🚀 Attempting to open {app}")
            if app.lower() == "youtube":
                subprocess.Popen(["termux-open", "--app", "com.google.android.youtube"], shell=False)
            elif app.lower() == "notes":
                subprocess.Popen(["termux-open", "--app", "com.termux.app.TermuxActivity"], shell=False)
            else:
                subprocess.Popen(["termux-open", "--app", app], shell=False)
        except Exception as exc:
            await self.send_message(room.room_id, f"Could not open {app}: {exc}")

    async def handle_unauthorized(self, room: MatrixRoom, sender: str):
        attempts = self.failed_auth_attempts.get(sender, 0) + 1
        self.failed_auth_attempts[sender] = attempts
        if attempts == 1:
            msg = "🔒 You are not authorized for system commands."
        elif attempts >= 3:
            msg = "🚫 Access denied."
        else:
            msg = "🚨 Repeated unauthorized access detected!"
        await self.send_message(room.room_id, msg)

    async def get_sys_status(self, room: MatrixRoom):
        try:
            cpu = psutil.cpu_percent(interval=0.2) if psutil else "n/a"
            mem = psutil.virtual_memory().percent if psutil else "n/a"
            status = f"🛡️ Termux System Status\nCPU: {cpu}%\nRAM: {mem}%\nMemory DB: {self.brain.stats_line()}"
        except Exception as exc:
            status = f"System monitor not available: {exc}"
        await self.send_message(room.room_id, status)

    async def send_message(self, room_id: str, message: str):
        try:
            await self.client.room_send(
                room_id=room_id,
                message_type="m.room.message",
                content={"msgtype": "m.text", "body": message},
            )
        except Exception as e:
            logger.error("Send error: %s", e)

    async def invite_callback(self, room: MatrixRoom, event: InviteMemberEvent):
        try:
            await self.client.join(room.room_id)
            await self.send_message(room.room_id, "Hello. I am Ribit, learning in memory mode.")
        except Exception as exc:
            logger.error("Failed to join invite: %s", exc)

    async def run(self):
        response = await self.client.login(self.password)
        if isinstance(response, LoginResponse):
            logger.info("Logged in as %s", self.user_id)
            await self.client.sync_forever(timeout=30000, full_state=False)
        else:
            logger.error("Login failed: %s", response)

    async def close(self):
        try:
            await self.client.close()
        except Exception:
            pass
        self.brain.memory.close()


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ribit Termux Matrix bot with memory and Gemma fallback.")
    parser.add_argument("--self-test", action="store_true", help="Run a local non-Matrix smoke test and exit.")
    parser.add_argument("--db", default=os.getenv("RIBIT_DB_PATH", "ribit_memory.db"), help="SQLite database path.")
    parser.add_argument("--homeserver", default=os.getenv("MATRIX_HOMESERVER", "https://matrix.stargazypie.xyz"))
    parser.add_argument("--user-id", default=os.getenv("MATRIX_USER_ID", "@merkaba:stargazypie.xyz"))
    parser.add_argument("--password", default=os.getenv("MATRIX_PASSWORD", "d3rLl2UrTAmeGb"))
    parser.add_argument("--device-id", default=os.getenv("MATRIX_DEVICE_ID", "RIBIT_TERMUX"))
    return parser


async def local_self_test(db_path: str) -> None:
    brain = RibitBrain(db_path)
    try:
        brain.learn_turn("local", "@tester:local", "Crystal is a memory bot that learns words and history.", "user")
        brain.learn_turn("local", "@tester:local", "Ribit can save knowledge, recall facts, and answer Matrix messages.", "user")
        brain.learn_turn("local", "@tester:local", "I like systems that remember technical details.", "user")

        for prompt in [
            "Tell me about Crystal",
            "How does Ribit learn?",
            "Explain the memory system",
            "Tell me a joke",
        ]:
            result = await brain.generate(prompt)
            print(f"\nPROMPT: {prompt}\nMODEL: {result.used_model}\nREPLY: {result.text}")
        print("\nSTATS:", brain.stats_line())
        print("SUMMARY:", brain.recent_summary())
    finally:
        brain.memory.close()


async def async_main():
    args = build_arg_parser().parse_args()

    if args.self_test:
        await local_self_test(args.db)
        return

    if not NIO_AVAILABLE:
        raise SystemExit(
            "matrix-nio is not installed. For local testing use --self-test, or install requirements.txt."
        )

    if not args.user_id or not args.password:
        raise SystemExit(
            "MATRIX_USER_ID and MATRIX_PASSWORD are required. "
            "Set environment variables or pass --user-id/--password."
        )

    bot = RibitTermuxBot(
        homeserver=args.homeserver,
        user_id=args.user_id,
        password=args.password,
        device_id=args.device_id,
        db_path=args.db,
    )
    try:
        await bot.run()
    finally:
        await bot.close()


def main():
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
