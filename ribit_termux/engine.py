"""Local-first Ribit conversation engine."""

from __future__ import annotations

from .memory import MemoryStore
from .providers import GenerationResult, ProviderRouter


class RibitEngine:
    """Coordinates local memory and the configured text-only model providers."""

    def __init__(self, memory: MemoryStore, providers: ProviderRouter) -> None:
        self.memory = memory
        self.providers = providers

    async def answer(self, *, room_id: str | None, sender: str | None, prompt: str) -> GenerationResult:
        self.memory.learn(room_id=room_id, sender=sender, role="user", text=prompt)
        result = await self.providers.generate(prompt, self.memory.context(prompt))
        self.memory.learn(room_id=room_id, sender="ribit", role=f"assistant:{result.used_model}", text=result.text)
        return result

    def teach(self, *, room_id: str | None, sender: str | None, text: str) -> None:
        self.memory.learn(room_id=room_id, sender=sender, role="manual_teach", text=text)

    def status(self) -> str:
        stats = self.memory.status()
        return (
            f"messages={stats['messages']}; facts={stats['facts']}; words={stats['words']}; "
            f"{self.providers.status()}"
        )

    def close(self) -> None:
        self.memory.close()
