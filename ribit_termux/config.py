"""Configuration for the Ribit Termux 0.2 prototype.

Configuration is read from environment variables.  Secrets are deliberately not
stored in the repository; use a private ``.env`` file or Termux environment.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


class ConfigurationError(ValueError):
    """Raised when a required runtime setting is missing or malformed."""


def _csv(value: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in value.split(",") if item.strip())


def _bool(value: str, *, default: bool = False) -> bool:
    if not value.strip():
        return default
    return value.strip().casefold() in {"1", "true", "yes", "on"}


@dataclass(frozen=True, slots=True)
class Settings:
    """Runtime settings with conservative defaults for a local-first bot."""

    runtime_dir: Path
    db_path: Path
    knowledge_file: Path
    provider: str
    local_llm_url: str
    local_llm_model: str
    local_llm_timeout_seconds: float
    matrix_homeserver: str
    matrix_user_id: str
    matrix_password: str
    matrix_device_id: str
    authorized_users: tuple[str, ...]
    auto_join_invites: bool

    @classmethod
    def from_environment(cls, *, require_matrix: bool) -> "Settings":
        runtime_dir = Path(os.getenv("RIBIT_RUNTIME_DIR", "./runtime")).expanduser()
        runtime_dir.mkdir(parents=True, exist_ok=True)

        provider = os.getenv("RIBIT_PROVIDER", "auto").strip().casefold()
        if provider not in {"auto", "local", "mock"}:
            raise ConfigurationError("RIBIT_PROVIDER must be one of: auto, local, mock.")

        homeserver = os.getenv("MATRIX_HOMESERVER", "").strip()
        user_id = os.getenv("MATRIX_USER_ID", "").strip()
        password = os.getenv("MATRIX_PASSWORD", "").strip()
        if require_matrix and not all((homeserver, user_id, password)):
            raise ConfigurationError(
                "MATRIX_HOMESERVER, MATRIX_USER_ID, and MATRIX_PASSWORD are required for Matrix mode."
            )

        authorized_users = _csv(os.getenv("RIBIT_AUTHORIZED_USERS", user_id))
        if require_matrix and not authorized_users:
            raise ConfigurationError(
                "RIBIT_AUTHORIZED_USERS must contain at least the controlling Matrix user ID."
            )

        return cls(
            runtime_dir=runtime_dir,
            db_path=Path(os.getenv("RIBIT_DB_PATH", str(runtime_dir / "ribit_memory.db"))).expanduser(),
            knowledge_file=Path(
                os.getenv("RIBIT_KNOWLEDGE_FILE", str(runtime_dir / "ribit_mock_knowledge.txt"))
            ).expanduser(),
            provider=provider,
            local_llm_url=os.getenv("RIBIT_LOCAL_LLM_URL", "http://127.0.0.1:8080/v1").strip(),
            local_llm_model=os.getenv("RIBIT_LOCAL_LLM_MODEL", "local-model").strip(),
            local_llm_timeout_seconds=float(os.getenv("RIBIT_LOCAL_LLM_TIMEOUT", "30")),
            matrix_homeserver=homeserver,
            matrix_user_id=user_id,
            matrix_password=password,
            matrix_device_id=os.getenv("MATRIX_DEVICE_ID", "RIBIT_TERMUX_02").strip(),
            authorized_users=authorized_users,
            auto_join_invites=_bool(os.getenv("RIBIT_AUTO_JOIN_INVITES", ""), default=False),
        )


def load_dotenv(path: str | Path = ".env") -> None:
    """Load simple KEY=VALUE pairs without replacing already-set environment values.

    The loader intentionally supports only uncomplicated local configuration. It
    is not a shell parser and never evaluates values as code.
    """

    env_file = Path(path)
    if not env_file.is_file():
        return
    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value
