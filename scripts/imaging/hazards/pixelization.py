"""Small complete-likelihood fixture for tier-2 imaging hazard checks.

The cell intentionally uses a 7x7 image and 3x3 rectangular source mesh.  It is
large enough to exercise the real ``FitImaging`` inversion while remaining a
diagnostic, not a runtime benchmark.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict
from functools import lru_cache
from pathlib import Path

import autoarray as aa
import autolens as al
import numpy as np


def _profiling_root() -> Path:
    for path in Path(__file__).resolve().parents:
        if (path / "ruff.toml").is_file():
            return path
    raise RuntimeError("autolens_profiling root (ruff.toml) not found")


REPO_ROOT = _profiling_root()
MISC_ROOT = REPO_ROOT / "scripts" / "misc"
if str(MISC_ROOT) not in sys.path:
    sys.path.insert(0, str(MISC_ROOT))

from hazards._likelihood import (  # noqa: E402
    LikelihoodProbeRow,
    calibrated_scale_aware_floors,
)

if os.environ.get("AUTOLENS_PROFILING_SMOKE") == "1":
    print(f"[smoke] {__file__}: imports + module setup OK; exiting.")
    raise SystemExit(0)


@lru_cache(maxsize=3)
def _dataset(noise_scale: float = 1.0):
    data_native = np.zeros((7, 7))
    data_native[2:5, 2:5] = np.asarray(((0.1, 1.0, 0.0), (0.2, 3.0, 0.3), (0.0, 0.5, 0.1)))
    data = aa.Array2D.no_mask(values=data_native, pixel_scales=(1.0, 1.0))
    noise_map = aa.Array2D.full(
        fill_value=2.0 * noise_scale,
        shape_native=(7, 7),
        pixel_scales=(1.0, 1.0),
    )
    kernel = aa.Array2D.no_mask(
        values=np.asarray(((0.0, 0.5, 0.0), (0.5, 1.0, 0.5), (0.0, 0.5, 0.0))),
        pixel_scales=(1.0, 1.0),
    )
    mask = aa.Mask2D(
        mask=np.asarray(
            (
                (True, True, True, True, True, True, True),
                (True, True, True, True, True, True, True),
                (True, True, False, False, False, True, True),
                (True, True, False, False, False, True, True),
                (True, True, False, False, False, True, True),
                (True, True, True, True, True, True, True),
                (True, True, True, True, True, True, True),
            )
        ),
        pixel_scales=(1.0, 1.0),
    )
    return aa.Imaging(
        data=data,
        psf=aa.Convolver(kernel=kernel),
        noise_map=noise_map,
        over_sample_size_lp=1,
    ).apply_mask(mask=mask)


def _array_module(backend: str):
    if backend == "numpy":
        return np
    if backend == "jax":
        import jax
        import jax.numpy as jnp

        jax.config.update("jax_enable_x64", True)
        return jnp
    raise ValueError(f"unsupported backend: {backend}")


def _inversion_row(
    *,
    backend: str,
    einstein_radius: float,
    noise_scale: float,
    curvature_floor: float | None = None,
    curvature_floor_policy: str = "absolute",
) -> LikelihoodProbeRow:
    xp = _array_module(backend)
    pixelization = al.Pixelization(
        mesh=al.mesh.RectangularUniform(shape=(3, 3)),
        regularization=al.reg.Constant(coefficient=1.0),
    )
    tracer = al.Tracer(
        galaxies=(
            al.Galaxy(
                redshift=0.5,
                bulge=al.lp_linear.SersicSph(
                    effective_radius=0.6,
                    sersic_index=2.0,
                ),
                mass=al.mp.IsothermalSph(einstein_radius=einstein_radius),
            ),
            al.Galaxy(redshift=1.0, pixelization=pixelization),
        )
    )
    settings = al.Settings(
        use_positive_only_solver=True,
        use_edge_zeroed_pixels=False,
        no_regularization_add_to_curvature_diag_value=curvature_floor,
    )
    applied_floor = float(settings.no_regularization_add_to_curvature_diag_value)
    fit = al.FitImaging(
        dataset=_dataset(noise_scale=noise_scale),
        tracer=tracer,
        settings=settings,
        xp=xp,
    )
    inversion = fit.inversion
    curvature_diagonal = np.diag(np.asarray(inversion.curvature_matrix, dtype=float))
    conditioned_indices = tuple(int(index) for index in inversion.no_regularization_index_list)
    return LikelihoodProbeRow(
        parameter=float(einstein_radius),
        parameter_name="einstein_radius",
        backend=backend,
        figure_of_merit=float(np.asarray(fit.figure_of_merit)),
        reconstruction=tuple(np.asarray(inversion.reconstruction, dtype=float).tolist()),
        curvature_diagonal=tuple(curvature_diagonal.tolist()),
        conditioned_curvature_diagonal=tuple(
            curvature_diagonal[list(conditioned_indices)].tolist()
        ),
        regularization_diagonal=tuple(
            np.diag(np.asarray(inversion.regularization_matrix, dtype=float)).tolist()
        ),
        noise_scale=float(noise_scale),
        metadata={
            "curvature_floor_policy": curvature_floor_policy,
            "curvature_floor_value": applied_floor,
            "conditioned_indices": list(conditioned_indices),
        },
    )


def _structural_row(*, backend: str, axis_ratio: float, angle: float) -> LikelihoodProbeRow:
    xp = _array_module(backend)
    ell_comps = al.convert.ell_comps_from(axis_ratio=axis_ratio, angle=angle)
    tracer = al.Tracer(
        galaxies=(
            al.Galaxy(
                redshift=0.5,
                bulge=al.lp.Sersic(
                    ell_comps=ell_comps,
                    intensity=1.0,
                    effective_radius=1.0,
                    sersic_index=2.0,
                ),
            ),
        )
    )
    fit = al.FitImaging(dataset=_dataset(), tracer=tracer, xp=xp)
    return LikelihoodProbeRow(
        parameter=float(axis_ratio),
        parameter_name="axis_ratio",
        backend=backend,
        figure_of_merit=float(np.asarray(fit.figure_of_merit)),
        metadata={"axis_ratio": float(axis_ratio), "angle": float(angle)},
    )


def run_probe(backends: tuple[str, ...] = ("numpy", "jax")) -> dict[str, list]:
    """Evaluate the full likelihood over bounded diagnostic parameter grids."""

    einstein_radii = np.linspace(0.1, 1.6, 31)
    inversion = [
        _inversion_row(
            backend=backend,
            einstein_radius=float(einstein_radius),
            noise_scale=1.0,
        )
        for backend in backends
        for einstein_radius in einstein_radii
    ]
    inversion.extend(
        _inversion_row(backend=backend, einstein_radius=0.9, noise_scale=noise_scale)
        for backend in backends
        for noise_scale in (0.5, 2.0)
    )
    configured_floor = float(al.Settings().no_regularization_add_to_curvature_diag_value)
    control_rows = [
        _inversion_row(
            backend="numpy",
            einstein_radius=0.9,
            noise_scale=noise_scale,
            curvature_floor=0.0,
            curvature_floor_policy="none",
        )
        for noise_scale in (0.5, 1.0, 2.0)
    ]
    _, scale_aware_values = calibrated_scale_aware_floors(
        control_rows,
        configured_floor=configured_floor,
    )
    absolute_rows = [row for row in inversion if row.backend == "numpy" and row.parameter == 0.9]
    scale_aware_rows = [
        _inversion_row(
            backend="numpy",
            einstein_radius=0.9,
            noise_scale=noise_scale,
            curvature_floor=scale_aware_values[noise_scale],
            curvature_floor_policy="scale_aware",
        )
        for noise_scale in (0.5, 1.0, 2.0)
    ]
    conditioning = control_rows + absolute_rows + scale_aware_rows
    structural = [
        _structural_row(backend=backend, axis_ratio=axis_ratio, angle=angle)
        for backend in backends
        for axis_ratio in (0.7, 0.9, 0.99, 1.0)
        for angle in (0.0, 30.0, 60.0, 90.0)
    ]
    return {
        "inversion": inversion,
        "conditioning": conditioning,
        "structural": structural,
    }


def main() -> int:
    probe = run_probe()
    output = REPO_ROOT / "results" / "hazards" / "imaging" / "pixelization" / "probe.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(
            {name: [asdict(row) for row in rows] for name, rows in probe.items()},
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
        + "\n"
    )
    print(f"wrote {output.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
