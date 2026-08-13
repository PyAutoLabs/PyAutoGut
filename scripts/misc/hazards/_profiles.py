"""Public profile-registry discovery and lightweight applicability metadata."""

from __future__ import annotations

import inspect
import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProfileSpec:
    registry: str
    class_name: str
    import_path: str
    family: str
    geometry: str


def _geometry(class_name: str) -> str:
    lowered = class_name.lower()
    return "spherical" if lowered.endswith("sph") or "spherical" in lowered else "elliptical"


def discover_profile_registry(autolens_module) -> tuple[ProfileSpec, ...]:
    """Discover public light/mass profile classes, de-duplicated across aliases."""

    specs: list[ProfileSpec] = []
    seen: set[tuple[str, str]] = set()
    for registry in ("lp", "lp_linear", "lmp", "mp"):
        namespace = getattr(autolens_module, registry, None)
        if namespace is None:
            continue
        for class_name, cls in inspect.getmembers(namespace, inspect.isclass):
            if class_name.startswith("_"):
                continue
            identity = (cls.__module__, cls.__qualname__)
            if identity in seen:
                continue
            seen.add(identity)
            specs.append(
                ProfileSpec(
                    registry=registry,
                    class_name=class_name,
                    import_path=f"{cls.__module__}.{cls.__qualname__}",
                    family={"mp": "mass", "lmp": "light_mass"}.get(registry, "light"),
                    geometry=_geometry(class_name),
                )
            )
    return tuple(sorted(specs, key=lambda spec: (spec.family, spec.registry, spec.class_name)))


def coverage_payload(specs: tuple[ProfileSpec, ...]) -> dict:
    families = {family: 0 for family in ("light", "light_mass", "mass")}
    geometries = {geometry: 0 for geometry in ("elliptical", "spherical")}
    for spec in specs:
        families[spec.family] += 1
        geometries[spec.geometry] += 1
    return {
        "schema_version": 1,
        "scope": "public_profile_registry",
        "matrix_policy": "discovery_only; representative detectors are not multiplied by backend",
        "counts": {"total": len(specs), "families": families, "geometries": geometries},
        "profiles": [asdict(spec) for spec in specs],
    }


def write_coverage(specs: tuple[ProfileSpec, ...], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(coverage_payload(specs), indent=2, sort_keys=True) + "\n")
