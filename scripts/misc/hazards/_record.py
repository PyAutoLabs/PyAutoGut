"""Finding schema, semantic IDs, persistence, and regression comparison."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from ._anchor import CodeAnchor
from ._measure import Measurement

SCHEMA_VERSION = 1
_FINDING_ID_RE = re.compile(r"^[a-z0-9]+(?:[._-][a-z0-9]+)+$")
_SUBJECTS = {"component", "matrix", "likelihood"}


@dataclass(frozen=True)
class Finding:
    finding_id: str
    title: str
    summary: str
    hazard_class: str
    tier: int
    subject: str
    subject_name: str
    backends: tuple[str, ...]
    measurements: tuple[Measurement, ...]
    anchors: tuple[CodeAnchor, ...]
    code_exists: bool
    reachable_via: tuple[str, ...]
    blocked_by: tuple[CodeAnchor, ...]
    affects_science: bool | None
    backend_reachability: dict[str, dict] = field(default_factory=dict)
    reproducer: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not _FINDING_ID_RE.fullmatch(self.finding_id):
            raise ValueError(f"finding_id is not stable semantic syntax: {self.finding_id!r}")
        if self.subject not in _SUBJECTS:
            raise ValueError(f"unknown subject: {self.subject}")
        if self.tier not in (1, 2):
            raise ValueError("tier must be 1 or 2")

    def to_dict(self) -> dict:
        return {
            "schema_version": SCHEMA_VERSION,
            "finding_id": self.finding_id,
            "title": self.title,
            "summary": self.summary,
            "hazard_class": self.hazard_class,
            "tier": self.tier,
            "subject": self.subject,
            "subject_name": self.subject_name,
            "backends": list(self.backends),
            "measurements": [measurement.to_dict() for measurement in self.measurements],
            "anchors": [anchor.to_dict() for anchor in self.anchors],
            "code_exists": self.code_exists,
            "reachable_via": list(self.reachable_via),
            "blocked_by": [anchor.to_dict() for anchor in self.blocked_by],
            "affects_science": self.affects_science,
            "backend_reachability": self.backend_reachability,
            "reproducer": self.reproducer,
        }

    @property
    def record_relative_path(self) -> Path:
        return Path(self.subject) / self.subject_name / f"{self.hazard_class}.json"


@dataclass(frozen=True)
class FindingDiff:
    new: tuple[str, ...]
    persistent: tuple[str, ...]
    resolved: tuple[str, ...]

    @property
    def has_new(self) -> bool:
        return bool(self.new)


def compare_finding_ids(current: set[str], baseline: set[str]) -> FindingDiff:
    return FindingDiff(
        new=tuple(sorted(current - baseline)),
        persistent=tuple(sorted(current & baseline)),
        resolved=tuple(sorted(baseline - current)),
    )


def write_grouped_findings(findings: list[Finding], output_root: Path) -> list[Path]:
    groups: dict[Path, list[Finding]] = {}
    for finding in findings:
        groups.setdefault(finding.record_relative_path, []).append(finding)

    written: list[Path] = []
    for relative_path, group in sorted(groups.items(), key=lambda item: str(item[0])):
        path = output_root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": SCHEMA_VERSION,
            "findings": [
                finding.to_dict() for finding in sorted(group, key=lambda f: f.finding_id)
            ],
        }
        path.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n")
        written.append(path)
    return written


def findings_from_record(path: Path) -> list[dict]:
    try:
        payload = json.loads(path.read_text())
    except (OSError, ValueError):
        return []
    findings = payload.get("findings", []) if isinstance(payload, dict) else []
    return [finding for finding in findings if isinstance(finding, dict)]


def load_index(path: Path) -> dict[str, dict]:
    try:
        payload = json.loads(path.read_text())
    except (OSError, ValueError):
        return {}
    findings = payload.get("findings", {}) if isinstance(payload, dict) else {}
    return findings if isinstance(findings, dict) else {}
