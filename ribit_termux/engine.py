"""Local-first Ribit conversation engine."""

from __future__ import annotations

from typing import Any

from .cognition import CognitiveRuntime
from .memory import MemoryStore
from .policy import CapabilityPolicy
from .providers import GenerationResult, ProviderRouter


class RibitEngine:
    """Coordinates persistent memory, bounded cognition, and text-only providers."""

    def __init__(self, memory: MemoryStore, providers: ProviderRouter) -> None:
        self.memory = memory
        self.providers = providers
        self.policy = CapabilityPolicy(workspace=memory.path.parent)
        self.cognition = CognitiveRuntime(memory, self.policy)
        self.last_review: dict[str, Any] = {}

    async def answer(self, *, room_id: str | None, sender: str | None, prompt: str) -> GenerationResult:
        self.memory.learn(room_id=room_id, sender=sender, role="user", text=prompt)
        self.cognition.observe(prompt, source="user")
        context = self.cognition.prepare(prompt)
        result = await self.providers.generate(prompt, context.as_provider_context())
        self.memory.learn(room_id=room_id, sender="ribit", role=f"assistant:{result.used_model}", text=result.text)
        self.cognition.observe(result.text, source=f"assistant:{result.used_model}")
        self.last_review = self.cognition.review(query=prompt, response=result.text, context=context)
        return result

    def teach(self, *, room_id: str | None, sender: str | None, text: str) -> None:
        self.memory.learn(room_id=room_id, sender=sender, role="manual_teach", text=text)
        self.cognition.observe(text, source="manual_teach")

    def plan(self, goal: str) -> list[dict[str, Any]]:
        return self.cognition.plan_for(goal)

    def mind_status(self) -> dict[str, Any]:
        return {"runtime": self.cognition.mind_status(), "last_review": self.last_review}

    def status(self) -> str:
        stats = self.memory.status()
        return (
            f"messages={stats['messages']}; facts={stats['facts']}; words={stats['words']}; "
            f"cognitive_records={stats['cognitive_records']}; {self.providers.status()}"
        )

    def close(self) -> None:
        self.memory.close()
