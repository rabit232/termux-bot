"""Small local knowledge graph for the Termux cognitive runtime."""

from __future__ import annotations

from collections import Counter, defaultdict, deque
from dataclasses import dataclass

from .semantic import tokenize


@dataclass(frozen=True, slots=True)
class Edge:
    """A weighted, labeled relationship between two normalized concepts."""

    source: str
    target: str
    relation: str
    weight: float


class KnowledgeGraph:
    """Bounded graph associations derived only from locally supplied text."""

    def __init__(self, *, max_nodes: int = 2000) -> None:
        self.max_nodes = max(100, max_nodes)
        self.nodes: Counter[str] = Counter()
        self.edges: dict[str, Counter[tuple[str, str]]] = defaultdict(Counter)
        self.reverse_edges: dict[str, Counter[tuple[str, str]]] = defaultdict(Counter)

    def learn_text(self, text: str, *, tags: tuple[str, ...] = ()) -> None:
        terms = tokenize(text)[:120]
        for term in terms:
            self.nodes[term] += 1
        for left, right in zip(terms, terms[1:]):
            if left != right:
                self.link(left, right, relation="adjacent", weight=0.2)
        for tag in tags:
            normalized_tag = tag.casefold().strip()
            if normalized_tag:
                self.nodes[normalized_tag] += 1
                for term in terms[:20]:
                    self.link(normalized_tag, term, relation="tagged_with", weight=0.5)
        self._enforce_limit()

    def learn_fact(self, subject: str, relation: str, object_: str, *, weight: float = 1.0) -> None:
        subject = subject.casefold().strip()[:160]
        relation = relation.casefold().strip()[:80]
        object_ = object_.casefold().strip()[:160]
        if subject and relation and object_:
            self.link(subject, object_, relation=relation, weight=weight)
            self._enforce_limit()

    def link(self, source: str, target: str, *, relation: str, weight: float = 1.0) -> None:
        if not source or not target or source == target:
            return
        value = max(0.01, min(float(weight), 10.0))
        self.nodes[source] += 1
        self.nodes[target] += 1
        self.edges[source][(target, relation)] += value
        self.reverse_edges[target][(source, relation)] += value

    def related(self, query: str, *, limit: int = 8) -> list[dict[str, object]]:
        scores: Counter[tuple[str, str]] = Counter()
        for term in tokenize(query):
            scores.update(self.edges.get(term, {}))
            scores.update(self.reverse_edges.get(term, {}))
        return [
            {"concept": concept, "relation": relation, "weight": round(weight, 3)}
            for (concept, relation), weight in scores.most_common(max(1, limit))
        ]

    def shortest_path(self, start: str, end: str, *, max_depth: int = 3) -> list[str]:
        """Return a local graph path for diagnostics, not a factual proof."""

        start = start.casefold().strip()
        end = end.casefold().strip()
        if not start or not end or start not in self.nodes or end not in self.nodes:
            return []
        queue: deque[tuple[str, list[str]]] = deque([(start, [start])])
        seen = {start}
        while queue:
            current, path = queue.popleft()
            if current == end:
                return path
            if len(path) > max_depth:
                continue
            for target, _ in self.edges.get(current, {}):
                if target not in seen:
                    seen.add(target)
                    queue.append((target, [*path, target]))
        return []

    def explain(self, query: str, *, limit: int = 8) -> dict[str, object]:
        return {"query_terms": tokenize(query)[:20], "related": self.related(query, limit=limit), "nodes": len(self.nodes)}

    def stats(self) -> dict[str, int]:
        return {"nodes": len(self.nodes), "edges": sum(len(edges) for edges in self.edges.values())}

    def _enforce_limit(self) -> None:
        overflow = len(self.nodes) - self.max_nodes
        if overflow <= 0:
            return
        for node, _ in self.nodes.most_common()[:-overflow - 1:-1]:
            self.nodes.pop(node, None)
            self.edges.pop(node, None)
            self.reverse_edges.pop(node, None)
        for source in list(self.edges):
            self.edges[source] = Counter(
                {(target, relation): weight for (target, relation), weight in self.edges[source].items() if target in self.nodes}
            )
