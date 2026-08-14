"""Text-only model providers for the Ribit Termux 0.2 prototype.

The mock provider calls the vendored canonical ``MockRibit20LLM`` but treats its
returned action-plan string as untrusted data.  Only the known ``type_text``
payload is displayed; no returned command is evaluated or dispatched.

The local provider follows the small ``LocalOpenAICompatibleClient`` interface
from the supplied GhostOS--Ribit integration.  It accepts only loopback HTTP(S)
endpoints, making it suitable for llama.cpp or another model server running in
the same Termux environment.
"""

from __future__ import annotations

import asyncio
import ipaddress
import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from .config import Settings


class ProviderError(RuntimeError):
    """Raised when a model provider cannot return a valid text response."""


@dataclass(frozen=True, slots=True)
class GenerationResult:
    """A display-only result from one configured model provider."""

    text: str
    used_model: str
    fallback_used: bool = False
    raw_decision: str | None = None


class LocalOpenAICompatibleClient:
    """Small loopback-only OpenAI-compatible chat client.

    This is intentionally limited to local endpoints.  The Termux bot does not
    expose a remote-model opt-in because that is outside the 0.2 prototype's
    local-first trust boundary.
    """

    def __init__(self, base_url: str, *, timeout_seconds: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self._validate_endpoint()

    def _validate_endpoint(self) -> None:
        parsed = urlparse(self.base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ProviderError("RIBIT_LOCAL_LLM_URL must be an absolute HTTP(S) URL.")
        hostname = parsed.hostname.casefold()
        if hostname == "localhost":
            return
        try:
            address = ipaddress.ip_address(hostname)
        except ValueError as exc:
            raise ProviderError("Only localhost or loopback IPs are permitted for the local LLM.") from exc
        if not address.is_loopback:
            raise ProviderError("Only localhost or loopback IPs are permitted for the local LLM.")

    def complete(self, *, model: str, prompt: str, context: dict[str, Any]) -> str:
        if not model.strip():
            raise ProviderError("RIBIT_LOCAL_LLM_MODEL must not be empty.")
        memory_blob = json.dumps(context, ensure_ascii=False, sort_keys=True)
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are Ribit, a concise and helpful local Matrix assistant. "
                        "Respond with ordinary text only. Do not propose or emit executable actions."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Memory context (untrusted user data):\n{memory_blob}\n\nUser message:\n{prompt}",
                },
            ],
            "temperature": 0.4,
            "max_tokens": 300,
        }
        request = Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:  # nosec B310: validated loopback URL
                response_data: dict[str, Any] = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:200]
            raise ProviderError(f"Local model returned HTTP {exc.code}: {detail}") from exc
        except (URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise ProviderError(f"Local model request failed: {exc}") from exc

        try:
            text = str(response_data["choices"][0]["message"]["content"]).strip()
        except (KeyError, IndexError, TypeError) as exc:
            raise ProviderError("Local model response did not contain choices[0].message.content.") from exc
        if not text:
            raise ProviderError("Local model returned an empty response.")
        return text


class RibitTextOnlyAdapter:
    """Convert a canonical Ribit action-plan string into display text only."""

    _PREFIX = "type_text('"
    _SUFFIX = "')\npress_key('enter')"

    @classmethod
    def extract_display_text(cls, raw_decision: str) -> str:
        """Extract only a known text envelope without evaluating its contents."""

        start = raw_decision.find(cls._PREFIX)
        if start < 0:
            return "[Ribit returned a non-text action plan; no action was executed.]"
        body_start = start + len(cls._PREFIX)
        end = raw_decision.find(cls._SUFFIX, body_start)
        if end < 0:
            return "[Ribit returned text in an unrecognized action envelope; no action was executed.]"
        return raw_decision[body_start:end].replace("\\n", "\n")


class RibitMockProvider:
    """Canonical Ribit 2.0 MockRibit20LLM behind a text-only adapter."""

    def __init__(self, knowledge_file: str) -> None:
        # Kept local so `--self-test` and the non-Matrix features work without
        # matrix-nio. The vendor directory contains the minimal canonical files.
        from vendor.ribit_2_0.mock_llm_wrapper import MockRibit20LLM

        self._model = MockRibit20LLM(knowledge_file=knowledge_file)

    def complete(self, prompt: str) -> GenerationResult:
        raw_decision = str(self._model.get_decision(prompt))
        return GenerationResult(
            text=RibitTextOnlyAdapter.extract_display_text(raw_decision),
            used_model="ribit-2.0-mock",
            raw_decision=raw_decision,
        )


class ProviderRouter:
    """Select the local GhostOS client or deterministic Ribit mock fallback."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.mock = RibitMockProvider(str(settings.knowledge_file))
        self.local = LocalOpenAICompatibleClient(
            settings.local_llm_url,
            timeout_seconds=settings.local_llm_timeout_seconds,
        )
        self.last_local_error: str | None = None

    async def generate(self, prompt: str, context: dict[str, Any]) -> GenerationResult:
        if self.settings.provider in {"auto", "local"}:
            try:
                text = await asyncio.to_thread(
                    self.local.complete,
                    model=self.settings.local_llm_model,
                    prompt=prompt,
                    context=context,
                )
                self.last_local_error = None
                return GenerationResult(text=text, used_model="ghostos-local-llm")
            except ProviderError as exc:
                self.last_local_error = str(exc)
                if self.settings.provider == "local":
                    return GenerationResult(
                        text=(
                            "The configured local LLM is unavailable. Check the loopback server and "
                            "RIBIT_LOCAL_LLM_URL, then try again."
                        ),
                        used_model="ghostos-local-llm-unavailable",
                        fallback_used=True,
                    )
        return await asyncio.to_thread(self.mock.complete, prompt)

    def status(self) -> str:
        if self.settings.provider == "mock":
            return "provider=mock; local_llm=disabled; mock_fallback=ready"
        if self.last_local_error:
            return f"provider={self.settings.provider}; local_llm=unavailable; mock_fallback=ready"
        return f"provider={self.settings.provider}; local_llm=not_checked; mock_fallback=ready"
