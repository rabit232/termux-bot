"""Message-scoped local cognition orchestration for Termux 0.2."""

from __future__ import annotations

from typing import Any

from ..memory import MemoryStore
from ..policy import CapabilityPolicy
from .context import ContextBuilder, ContextPackage
from .knowledge import KnowledgeGraph
from .persona import PersonaEngine
from .reasoning import AttentionEngine, PlanningEngine, ReasoningEngine, ReflectionEngine
from .semantic import SemanticMemory


class CognitiveRuntime:
    """Harmonizes compatible archive components behind a text-only interface.

    The runtime has no scheduler, thread, process, web, plug-in, GUI, or device
    control surface. It is invoked synchronously around individual chat turns.
    """

    def __init__(self, memory: MemoryStore, policy: CapabilityPolicy) -> None:
        self.memory = memory
        self.policy = policy
        self.semantic = SemanticMemory()
        self.graph = KnowledgeGraph()
        self.persona = PersonaEngine()
        self.attention = AttentionEngine()
        self.reasoning = ReasoningEngine(self.semantic, self.graph, self.attention)
        self.reflection = ReflectionEngine()
        self.planning = PlanningEngine()
        self.context_builder = ContextBuilder(self.persona, policy)
        self._sequence = 0
        self._hydrate_from_persistent_memory()

    def _hydrate_from_persistent_memory(self) -> None:
        for item in self.memory.recent_messages(limit=400):
            text = str(item["text"])
            role = str(item["role"])
            self.observe(text, source=role, persist=False)

    def observe(self, text: str, *, source: str, persist: bool = True) -> None:
        clean = " ".join(text.split())[:2000]
        if not clean:
            return
        tags = (source.casefold(),)
        self._sequence += 1
        key = f"{source}:{self._sequence}"
        self.semantic.add(key, clean, tags=tags, importance=1.2 if source.startswith("manual") else 1.0)
        self.graph.learn_text(clean, tags=tags)
        if persist:
            self.memory.save_cognitive_record(key=key, text=clean, tags=tags, importance=1.0)

    def prepare(self, query: str) -> ContextPackage:
        reasoning = self.reasoning.analyze(query)
        return self.context_builder.build(query=query, memory=self.memory.context(query), reasoning=reasoning)

    def review(self, *, query: str, response: str, context: ContextPackage) -> dict[str, Any]:
        return self.reflection.review(query=query, response=response, reasoning=context.reasoning)

    def plan_for(self, goal: str) -> list[dict[str, Any]]:
        return [
            {"order": task.order, "title": task.title, "purpose": task.purpose}
            for task in self.planning.create_plan(goal)
        ]

    def mind_status(self) -> dict[str, Any]:
        return {
            "semantic": self.semantic.stats(),
            "knowledge_graph": self.graph.stats(),
            "persona": self.persona.style(),
            "policy": self.policy.summary(),
            "persistent_cognitive_records": self.memory.cognitive_record_count(),
        }
