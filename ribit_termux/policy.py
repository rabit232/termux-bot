"""Deny-by-default capability policy for the Termux 0.2 runtime.

Adapted from the supplied GhostOS--Ribit policy pattern. The policy is a guard
for application code, not a request to enable capabilities. The standard bot
creates it with every high-impact capability disabled.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class PermissionDenied(PermissionError):
    """Raised when an operation is outside the explicitly granted policy."""


@dataclass(frozen=True, slots=True)
class CapabilityPolicy:
    """Explicit capabilities for the local runtime.

    Workspace read/write are distinct from process execution, networking, and
    device authority. A message handler must never change this policy.
    """

    workspace: Path
    read_only_roots: tuple[Path, ...] = ()
    allow_read_workspace: bool = False
    allow_write_workspace: bool = False
    allow_process_execution: bool = False
    allow_web_access: bool = False
    allow_gui_control: bool = False
    allow_robot_actuation: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "workspace", Path(self.workspace).expanduser().resolve())
        object.__setattr__(
            self,
            "read_only_roots",
            tuple(Path(root).expanduser().resolve() for root in self.read_only_roots),
        )

    def resolve_read_path(self, requested_path: str | Path) -> Path:
        requested = Path(requested_path).expanduser()
        candidate = requested.resolve() if requested.is_absolute() else (self.workspace / requested).resolve()
        if any(candidate == root or root in candidate.parents for root in (self.workspace, *self.read_only_roots)):
            return candidate
        raise PermissionDenied(f"Path is outside approved read roots: {requested_path}")

    def resolve_workspace_path(self, relative_path: str | Path) -> Path:
        candidate = (self.workspace / relative_path).resolve()
        if candidate != self.workspace and self.workspace not in candidate.parents:
            raise PermissionDenied(f"Path escapes the approved workspace: {relative_path}")
        return candidate

    def require_read(self) -> None:
        if not self.allow_read_workspace:
            raise PermissionDenied("Workspace read access is disabled by policy.")

    def require_write(self) -> None:
        if not self.allow_write_workspace:
            raise PermissionDenied("Workspace write access is disabled by policy.")

    def require_process_execution(self) -> None:
        if not self.allow_process_execution:
            raise PermissionDenied("Process execution is disabled by policy.")

    def require_web_access(self) -> None:
        if not self.allow_web_access:
            raise PermissionDenied("Web access is disabled by policy.")

    def require_gui_control(self) -> None:
        if not self.allow_gui_control:
            raise PermissionDenied("GUI control is disabled by policy.")

    def require_robot_actuation(self) -> None:
        if not self.allow_robot_actuation:
            raise PermissionDenied("Robot actuation is disabled by policy.")

    def summary(self) -> dict[str, bool]:
        return {
            "read_workspace": self.allow_read_workspace,
            "write_workspace": self.allow_write_workspace,
            "process_execution": self.allow_process_execution,
            "web_access": self.allow_web_access,
            "gui_control": self.allow_gui_control,
            "robot_actuation": self.allow_robot_actuation,
        }
