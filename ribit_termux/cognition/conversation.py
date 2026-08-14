"""Text-only conversation-mode guard adapted from Ribit 2.0.

The classifier replaces the upstream automation/conversation switch with a
single safe outcome: ordinary conversational text or a transparent refusal of
requests that would need process, GUI, web, or device authority.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass


@dataclass(frozen=True, slots=True)
class ConversationDecision:
    mode: str
    allow_provider: bool
    reason: str


class TextOnlyConversationGuard:
    """Classify incoming text without invoking or queuing automation."""

    _AUTOMATION_PATTERNS = (
        r"\bopen\s+(?:app|application|browser|terminal|settings)\b",
        r"\bclick\b",
        r"\btype\s+(?:into|in|on)\b",
        r"\bpress\s+(?:key|enter|button)\b",
        r"\bmove\s+(?:the\s+)?mouse\b",
        r"\btake\s+(?:a\s+)?screenshot\b",
        r"\brun\s+(?:this\s+)?command\b",
        r"\bexecute\s+(?:this\s+)?(?:code|script|command)\b",
        r"\bcontrol\s+(?:the\s+)?robot\b",
    )

    def classify(self, prompt: str) -> ConversationDecision:
        lowered = prompt.casefold()
        for pattern in self._AUTOMATION_PATTERNS:
            if re.search(pattern, lowered):
                return ConversationDecision(
                    mode="capability_refusal",
                    allow_provider=False,
                    reason="This Termux prototype is text-only and does not execute processes, GUI actions, web requests, or robot controls.",
                )
        return ConversationDecision(mode="conversational", allow_provider=True, reason="Text-only conversational request.")

    def context(self, prompt: str) -> dict[str, str | bool]:
        return asdict(self.classify(prompt))
