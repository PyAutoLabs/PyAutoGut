"""Detector protocol and scan context."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from hazards._record import Finding


@dataclass(frozen=True)
class ScanContext:
    repo_root: Path
    workspace_root: Path
    output_root: Path
    backends: tuple[str, ...]
    sample_count: int
    seed: int


class HazardCheck(ABC):
    name: str
    subject: str

    @abstractmethod
    def run(self, context: ScanContext) -> list[Finding]:
        """Run the real reproducer and return semantic findings."""

    def applies_to(self, subject: str) -> bool:
        return subject in ("all", self.subject)
