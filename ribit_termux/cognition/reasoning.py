"""Text-only attention, reasoning, reflection, and planning utilities.

The classes in this module combine the archive's attention, hypothesis,
reasoning, reflection, and planning patterns. They only prepare structured text
and diagnostics. They never choose or execute tools, processes, web actions, or
robot operations.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from typing import Any

from .knowledge import KnowledgeGraph
from .semantic import SemanticMemory, tokenize


@dataclass(frozen=True, slots=True)
class AttentionItem:
    text: str
    score: float
    source: str


@dataclass(frozen=True, slots=True)
class ReasoningStep:
    stage: str
    detail: str
    confidence: float


@dataclass(frozen=True, slots=True)
class PlanTask:
    order: int
    title: str
    purpose: str


class AttentionEngine:
    """Ranks local context items by transparent token-overlap and source score."""

    def rank(self, query: str, items: list[dict[str, Any]], *, limit: int = 5) -> list[AttentionItem]:
        query_terms = set(tokenize(query))
        ranked: list[AttentionItem] = []
        for item in items:
            text = str(item.get("text", "")).strip()
            if not text:
                continue
            overlap = len(query_terms & set(tokenize(text))) / max(1, len(query_terms))
            source_score = float(item.get("score", 0.0))
            score = min(1.0, max(0.0, overlap * 0.55 + source_score * 0.45))
            ranked.append(AttentionItem(text=text[:500], score=round(score, 4), source=str(item.get("source", "memory"))))
        return sorted(ranked, key=lambda item: item.score, reverse=True)[: max(1, limit)]


class PlanningEngine:
    """Creates a readable plan. Plan output is information, never an action queue."""

    def create_plan(self, goal: str) -> list[PlanTask]:
        compact_goal = " ".join(goal.split())[:300] or "Clarify the requested goal"
        return [
            PlanTask(1, "Clarify objective", f"Define the desired outcome for: {compact_goal}"),
            PlanTask(2, "Review local context", "Identify relevant local memory, graph relationships, and constraints."),
            PlanTask(3, "Propose approach", "Describe a bounded text-only approach and identify uncertainty."),
            PlanTask(4, "Review result", "Check the response for safety, relevance, and missing information."),
        ]


class ReasoningEngine:
    """Builds a bounded evidence trace from local semantic and graph memory."""

    def __init__(self, semantic: SemanticMemory, graph: KnowledgeGraph, attention: AttentionEngine | None = None) -> None:
        self.semantic = semantic
        self.graph = graph
        self.attention = attention or AttentionEngine()

    def analyze(self, query: str) -> dict[str, Any]:
        semantic_hits = self.semantic.search(query, limit=6)
        graph = self.graph.explain(query, limit=8)
        focused = self.attention.rank(query, [{**hit, "source": "semantic"} for hit in semantic_hits], limit=4)
        related = graph.get("related", [])
        confidence = min(0.95, 0.20 + min(len(semantic_hits), 5) * 0.10 + min(len(related), 5) * 0.07)
        terms = Counter(tokenize(query)).most_common(6)
        steps = [
            ReasoningStep("parse", f"Extracted query terms: {', '.join(term for term, _ in terms) or 'none'}.", 0.80),
            ReasoningStep("retrieve", f"Ranked {len(semantic_hits)} local semantic-memory candidates.", min(0.90, 0.30 + len(semantic_hits) * 0.10)),
            ReasoningStep("associate", f"Found {len(related)} graph associations derived from local text.", min(0.90, 0.25 + len(related) * 0.08)),
            ReasoningStep("estimate", "Confidence is a retrieval signal, not a factual guarantee.", confidence),
        ]
        return {
            "confidence": round(confidence, 3),
            "semantic_hits": semantic_hits,
            "focused_context": [asdict(item) for item in focused],
            "graph": graph,
            "steps": [asdict(step) for step in steps],
        }


class ReflectionEngine:
    """Checks a generated response for simple non-authoritative quality signals."""

    def review(self, *, query: str, response: str, reasoning: dict[str, Any]) -> dict[str, Any]:
        response_terms = set(tokenize(response))
        query_terms = set(tokenize(query))
        coverage = len(response_terms & query_terms) / max(1, len(query_terms))
        warnings: list[str] = []
        if len(response.strip()) < 8:
            warnings.append("response_is_very_short")
        if not response_terms:
            warnings.append("response_has_no_words")
        if reasoning.get("confidence", 0.0) < 0.35:
            warnings.append("limited_local_context")
        return {
            "query_coverage": round(coverage, 3),
            "warnings": warnings,
            "reviewed": True,
            "note": "This reflection does not execute or approve actions.",
        }
