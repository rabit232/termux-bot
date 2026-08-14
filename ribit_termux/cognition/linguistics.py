"""Local linguistic analysis adapted from Ribit 2.0's LinguisticsEngine.

The analysis is heuristic and advisory. It provides context metadata for a text
provider; it does not profile users outside the current runtime or make actions.
"""

from __future__ import annotations

from collections import Counter, defaultdict
import re
from typing import Any


class LinguisticAnalyzer:
    """Bounded in-memory analysis of intent, tone, formality, and question depth."""

    def __init__(self, *, max_patterns_per_user: int = 50) -> None:
        self.max_patterns_per_user = max(1, max_patterns_per_user)
        self.user_patterns: dict[str, list[dict[str, str | int]]] = defaultdict(list)

    def analyze(self, text: str, *, user_id: str | None = None) -> dict[str, Any]:
        cleaned = " ".join(text.split())[:4000]
        words = re.findall(r"[\w'-]+", cleaned.casefold())
        analysis: dict[str, Any] = {
            "intent": self._intent(cleaned),
            "tone": self._tone(cleaned),
            "formality": self._formality(words, cleaned.casefold()),
            "complexity": self._complexity(words, cleaned.casefold()),
            "question_depth": self._question_depth(cleaned.casefold()),
            "key_phrases": self._key_phrases(cleaned),
            "technologies": [item for item in ("python", "javascript", "rust", "go", "docker", "api", "matrix", "termux") if item in words],
            "word_count": len(words),
        }
        if user_id:
            self._learn(user_id, cleaned, analysis)
            analysis["user_style"] = self.profile(user_id)
        return analysis

    @staticmethod
    def _intent(text: str) -> str:
        lowered = text.casefold()
        if any(word in lowered for word in ("what", "how", "why", "when", "where", "who")) or (
            "?" in text and any(phrase in lowered for phrase in ("could you", "would you", "can you", "please explain"))
        ):
            if "what if" in lowered or "what would" in lowered:
                return "hypothetical_inquiry"
            return "information_seeking"
        if any(word in lowered for word in ("help", "stuck", "problem", "issue", "error", "fix")):
            return "assistance_seeking"
        if any(word in lowered for word in ("i think", "i believe", "i feel", "in my opinion")):
            return "opinion_sharing"
        if any(word in lowered for word in ("hello", "hi", "hey", "thanks", "bye")):
            return "social_interaction"
        if any(word in lowered for word in ("meaning", "purpose", "existence", "consciousness", "philosophy")):
            return "philosophical_inquiry"
        return "general_statement"

    @staticmethod
    def _tone(text: str) -> str:
        lowered = text.casefold()
        if "!" in text or any(word in lowered for word in ("awesome", "amazing", "wow", "great")):
            return "excited"
        if any(word in lowered for word in ("ugh", "argh", "frustrated", "annoying", "broken")):
            return "frustrated"
        if "?" in text and any(word in lowered for word in ("wonder", "curious", "interesting")):
            return "curious"
        if any(word in lowered for word in ("important", "serious", "critical", "urgent")):
            return "serious"
        if any(word in lowered for word in ("lol", "haha", "btw", "tbh", "ngl")):
            return "casual"
        if any(word in lowered for word in ("please", "thank you", "thanks", "appreciate", "kindly")):
            return "polite"
        return "neutral"

    @staticmethod
    def _formality(words: list[str], lowered: str) -> str:
        informal = sum(word in {"u", "ur", "gonna", "wanna", "kinda", "sorta", "yeah", "nah", "lol", "btw"} for word in words)
        formal = sum(phrase in lowered for phrase in ("would you", "could you", "may i", "i would like", "please", "kindly"))
        return "informal" if informal > formal else "formal" if formal > informal else "neutral"

    @staticmethod
    def _complexity(words: list[str], lowered: str) -> str:
        if not words:
            return "empty"
        average = sum(len(word) for word in words) / len(words)
        if average > 6 or any(word in lowered for word in ("although", "however", "whereas", "nevertheless")) or any(len(word) > 10 for word in words):
            return "complex"
        return "moderate" if average > 4 else "simple"

    @staticmethod
    def _question_depth(lowered: str) -> str:
        if "?" not in lowered:
            return "not_a_question"
        if any(phrase in lowered for phrase in ("what is", "who is", "when was", "where is")):
            return "surface_factual"
        if any(phrase in lowered for phrase in ("how to", "how do", "how can")):
            return "process_oriented"
        if "why" in lowered:
            return "analytical"
        if any(word in lowered for word in ("meaning", "purpose", "should", "ought")):
            return "philosophical"
        return "general"

    @staticmethod
    def _key_phrases(text: str) -> list[str]:
        quoted = re.findall(r'"([^"\n]{1,160})"', text)
        words = text.split()
        capitalized = [f"{left} {right}" for left, right in zip(words, words[1:]) if left[:1].isupper() and right[:1].isupper()]
        return (quoted + capitalized)[:8]

    def _learn(self, user_id: str, text: str, analysis: dict[str, Any]) -> None:
        patterns = self.user_patterns[user_id]
        patterns.append(
            {
                "length": len(text),
                "tone": str(analysis["tone"]),
                "formality": str(analysis["formality"]),
                "intent": str(analysis["intent"]),
                "question": int("?" in text),
            }
        )
        del patterns[:-self.max_patterns_per_user]

    def profile(self, user_id: str) -> dict[str, Any]:
        patterns = self.user_patterns.get(user_id, [])
        if not patterns:
            return {"available": False}
        tones = Counter(str(item["tone"]) for item in patterns)
        formalities = Counter(str(item["formality"]) for item in patterns)
        intents = Counter(str(item["intent"]) for item in patterns)
        return {
            "available": True,
            "messages_analyzed": len(patterns),
            "average_length": round(sum(int(item["length"]) for item in patterns) / len(patterns), 1),
            "preferred_tone": tones.most_common(1)[0][0],
            "preferred_formality": formalities.most_common(1)[0][0],
            "common_intent": intents.most_common(1)[0][0],
            "question_frequency": round(sum(int(item["question"]) for item in patterns) / len(patterns), 2),
        }
