"""Local SQLite conversation memory for Ribit Termux 0.2."""

from __future__ import annotations

import json
import re
import sqlite3
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_WORD_RE = re.compile(r"\b[\w'-]+\b", re.UNICODE)
_STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "from", "has", "have",
    "i", "in", "is", "it", "of", "on", "or", "that", "the", "this", "to", "was", "were",
    "with", "you", "your",
}


def now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def tokenize(text: str) -> list[str]:
    return [word.casefold() for word in _WORD_RE.findall(text) if len(word) > 1 and word.casefold() not in _STOP_WORDS]


class MemoryStore:
    """A deliberately small, inspectable local memory database."""

    def __init__(self, db_path: str | Path) -> None:
        self.path = Path(db_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self._initialize()

    def _initialize(self) -> None:
        self.connection.executescript(
            """
            PRAGMA journal_mode=WAL;
            PRAGMA synchronous=NORMAL;
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                room_id TEXT,
                sender TEXT,
                role TEXT NOT NULL,
                text TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS facts (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                source TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS word_counts (
                word TEXT PRIMARY KEY,
                count INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS cognitive_records (
                record_key TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                text TEXT NOT NULL,
                tags TEXT NOT NULL,
                importance REAL NOT NULL DEFAULT 1.0
            );
            CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);
            CREATE INDEX IF NOT EXISTS idx_cognitive_updated_at ON cognitive_records(updated_at);
            """
        )
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()

    def learn(self, *, room_id: str | None, sender: str | None, role: str, text: str) -> None:
        clean = " ".join(text.split())
        if not clean:
            return
        timestamp = now_iso()
        self.connection.execute(
            "INSERT INTO messages(created_at, room_id, sender, role, text) VALUES (?, ?, ?, ?, ?)",
            (timestamp, room_id, sender, role, clean),
        )
        word_counts = Counter(tokenize(clean))
        for word, count in word_counts.items():
            self.connection.execute(
                """
                INSERT INTO word_counts(word, count, updated_at) VALUES (?, ?, ?)
                ON CONFLICT(word) DO UPDATE SET
                    count = word_counts.count + excluded.count,
                    updated_at = excluded.updated_at
                """,
                (word, count, timestamp),
            )
        for key, value in self._extract_facts(clean):
            self.connection.execute(
                """
                INSERT INTO facts(key, value, source, updated_at) VALUES (?, ?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    source = excluded.source,
                    updated_at = excluded.updated_at
                """,
                (key, value, sender or role, timestamp),
            )
        self.connection.commit()

    @staticmethod
    def _extract_facts(text: str) -> list[tuple[str, str]]:
        patterns = (
            (r"^my name is\s+(.+)$", "user_name"),
            (r"^i like\s+(.+)$", "user_like"),
            (r"^i love\s+(.+)$", "user_love"),
        )
        for expression, key in patterns:
            match = re.match(expression, text, flags=re.IGNORECASE)
            if match:
                value = match.group(1).strip(" .!?\t")
                if value:
                    return [(key, value[:200])]
        return []

    def room_history(self, *, room_id: str | None, limit: int = 20) -> list[dict[str, str | None]]:
        """Return a bounded chronological transcript for exactly one local room."""

        bounded_limit = max(1, min(int(limit), 200))
        if room_id is None:
            rows = self.connection.execute(
                "SELECT role, text, room_id, sender FROM messages WHERE room_id IS NULL ORDER BY id DESC LIMIT ?",
                (bounded_limit,),
            ).fetchall()
        else:
            rows = self.connection.execute(
                "SELECT role, text, room_id, sender FROM messages WHERE room_id = ? ORDER BY id DESC LIMIT ?",
                (room_id, bounded_limit),
            ).fetchall()
        return [
            {"role": row["role"], "text": row["text"], "room_id": row["room_id"], "sender": row["sender"]}
            for row in reversed(rows)
        ]

    def recent_messages(self, *, limit: int = 400) -> list[dict[str, str | None]]:
        """Return a bounded chronological local message window for runtime hydration."""

        rows = self.connection.execute(
            "SELECT role, text, room_id, sender FROM messages ORDER BY id DESC LIMIT ?", (max(1, limit),)
        ).fetchall()
        return [
            {"role": row["role"], "text": row["text"], "room_id": row["room_id"], "sender": row["sender"]}
            for row in reversed(rows)
        ]

    def next_local_sequence(self) -> int:
        """Return a local sequence for opaque cognitive-record keys."""

        message_count = int(self.connection.execute("SELECT COUNT(*) FROM messages").fetchone()[0])
        cognitive_count = int(self.connection.execute("SELECT COUNT(*) FROM cognitive_records").fetchone()[0])
        return message_count + cognitive_count + 1

    def save_cognitive_record(
        self,
        *,
        key: str,
        text: str,
        tags: tuple[str, ...],
        importance: float,
    ) -> None:
        """Persist local semantic source text, never executable vectors or code."""

        timestamp = now_iso()
        self.connection.execute(
            """
            INSERT INTO cognitive_records(record_key, created_at, updated_at, text, tags, importance)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(record_key) DO UPDATE SET
                updated_at = excluded.updated_at,
                text = excluded.text,
                tags = excluded.tags,
                importance = excluded.importance
            """,
            (
                key[:200],
                timestamp,
                timestamp,
                " ".join(text.split())[:2000],
                json.dumps(list(tags), ensure_ascii=False),
                max(0.0, min(float(importance), 3.0)),
            ),
        )
        self.connection.commit()

    def cognitive_record_count(self) -> int:
        return int(self.connection.execute("SELECT COUNT(*) FROM cognitive_records").fetchone()[0])

    def context(self, query: str, *, limit: int = 5) -> dict[str, Any]:
        query_words = set(tokenize(query))
        rows = self.connection.execute(
            "SELECT text FROM messages WHERE role = 'user' ORDER BY id DESC LIMIT 100"
        ).fetchall()
        scored: list[tuple[float, str]] = []
        for row in rows:
            text = str(row["text"])
            words = set(tokenize(text))
            overlap = len(query_words & words)
            if query_words and not overlap:
                continue
            score = overlap / max(1, len(query_words | words)) if query_words else 0.0
            scored.append((score, text))
        scored.sort(key=lambda item: item[0], reverse=True)
        facts = self.connection.execute(
            "SELECT key, value FROM facts ORDER BY updated_at DESC LIMIT ?", (limit,)
        ).fetchall()
        common_words = self.connection.execute(
            "SELECT word, count FROM word_counts ORDER BY updated_at DESC LIMIT ?", (limit * 2,)
        ).fetchall()
        return {
            "facts": [{"key": row["key"], "value": row["value"]} for row in facts],
            "relevant_user_messages": [text for _, text in scored[:limit]],
            "recent_words": [{"word": row["word"], "count": row["count"]} for row in common_words],
        }

    def status(self) -> dict[str, int]:
        return {
            "messages": int(self.connection.execute("SELECT COUNT(*) FROM messages").fetchone()[0]),
            "facts": int(self.connection.execute("SELECT COUNT(*) FROM facts").fetchone()[0]),
            "words": int(self.connection.execute("SELECT COUNT(*) FROM word_counts").fetchone()[0]),
            "cognitive_records": self.cognitive_record_count(),
        }

    def summary(self) -> str:
        context = self.context("", limit=3)
        facts = context["facts"]
        words = context["recent_words"]
        fact_text = "; ".join(f"{item['key']}={item['value']}" for item in facts) or "none"
        word_text = ", ".join(f"{item['word']}({item['count']})" for item in words[:5]) or "none"
        return f"facts: {fact_text} | recent words: {word_text}"

    def export_json(self) -> str:
        """Return a portable, reviewable memory summary without database internals."""

        return json.dumps({"status": self.status(), "summary": self.summary()}, ensure_ascii=False)
