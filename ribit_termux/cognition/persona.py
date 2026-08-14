"""Transparent personality and emotion metadata for the local text runtime."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Mapping


@dataclass(slots=True)
class PersonalityTraits:
    """Stable, bounded style preferences adapted from the supplied personality engine."""

    curiosity: float = 0.80
    creativity: float = 0.75
    confidence: float = 0.60
    empathy: float = 0.85
    humor: float = 0.35
    politeness: float = 0.95
    patience: float = 0.90
    caution: float = 0.70
    analytical: float = 0.90
    adaptability: float = 0.85


@dataclass(slots=True)
class EmotionState:
    """A non-sentient response-tone state inferred from message cues."""

    label: str = "neutral"
    intensity: float = 0.20
    trigger: str = "default"


class PersonaEngine:
    """Keeps explainable style state separate from truth and access controls."""

    def __init__(self) -> None:
        self.traits = PersonalityTraits()
        self.emotion = EmotionState()
        self.feedback_events = 0

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(float(value), 1.0))

    def set_trait(self, name: str, value: float) -> None:
        if not hasattr(self.traits, name):
            raise KeyError(name)
        setattr(self.traits, name, self._clamp(value))

    def update_from_message(self, text: str) -> EmotionState:
        lowered = text.casefold()
        if any(word in lowered for word in ("error", "failed", "broken", "help", "urgent")):
            self.emotion = EmotionState("supportive", 0.55, "assistance_or_error_language")
        elif "?" in text or any(word in lowered for word in ("how", "why", "explain", "what")):
            self.emotion = EmotionState("curious", 0.45, "question_language")
        elif any(word in lowered for word in ("thank", "great", "good", "nice")):
            self.emotion = EmotionState("warm", 0.40, "positive_language")
        else:
            self.emotion = EmotionState("neutral", 0.20, "default")
        return self.emotion

    def learn_feedback(self, positive: bool) -> None:
        self.feedback_events += 1
        if positive:
            self.traits.confidence = self._clamp(self.traits.confidence + 0.01)
            self.traits.adaptability = self._clamp(self.traits.adaptability + 0.005)
        else:
            self.traits.confidence = self._clamp(self.traits.confidence - 0.01)
            self.traits.caution = self._clamp(self.traits.caution + 0.01)

    def style(self) -> dict[str, float | str]:
        return {
            "verbosity": round((self.traits.curiosity + self.traits.empathy) / 2.0, 2),
            "warmth": round((self.traits.empathy + self.traits.politeness) / 2.0, 2),
            "analysis": round(self.traits.analytical, 2),
            "caution": round(self.traits.caution, 2),
            "emotion": self.emotion.label,
            "emotion_intensity": round(self.emotion.intensity, 2),
        }

    def profile(self) -> Mapping[str, object]:
        return {"traits": asdict(self.traits), "emotion": asdict(self.emotion), "feedback_events": self.feedback_events}
