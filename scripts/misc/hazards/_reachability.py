"""Helpers that keep reachability separate from code existence and impact."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class PathProbe:
    path: str
    reachable: bool
    value: float | list[float] | None = None
    blocked_by: str | None = None
    error: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def probe_path(path: str, operation: Callable[[], object], *, blocked_by: str | None = None):
    """Evaluate one path without confusing a guard with a missing mechanism."""

    try:
        value = operation()
    except Exception as exc:  # detector boundary: the exception is evidence
        return PathProbe(
            path=path,
            reachable=False,
            blocked_by=blocked_by,
            error=f"{type(exc).__name__}: {exc}",
        )
    try:
        serializable = float(value)
    except (TypeError, ValueError):
        try:
            serializable = [float(item) for item in value]
        except (TypeError, ValueError):
            serializable = None
    return PathProbe(path=path, reachable=True, value=serializable)
