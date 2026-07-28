"""First-class af.MultiStartProdigy search profiling — imaging Delaunay pixelized source.

Promoted from the autolens_workspace_developer#117 campaign (2026-07,
``searches_minimal/pix_prodigy_findings.md``). Uses ``model_type=
"delaunay_matern"`` — same Delaunay mesh as the nautilus ``delaunay`` cell but
with **free MaternKernel regularization**, because on this mesh the choice of
regularization parametrization decides whether gradient search works at all:

- With the split-family ``AdaptSplit`` reg, broad-start descent hits a **NaN
  wall** at high coefficients (the #104 double-squared lambda^4 fragility):
  lanes die instead of learning, and the campaign's broad chain spent 1500
  steps flat at +8.5k logL before a ~2000-step resurrection lottery finally
  escaped. (It DID escape — the mesh is searchable, just heavily taxed.)
- With the reg **fixed/inherited** (SLaM ``source_pix[1]`` inherits it from
  the preceding fit), the same chain recovered the simulator truth exactly
  (r_E 1.600, shear to 2-3 d.p.) in ~150 steps.
- With **free Matérn** (this cell): same final fit ceiling (truth-point bars
  +29682 vs +30079), but the high-coefficient axis degrades *gracefully* — no
  NaNs anywhere — giving a smooth low-churn climb. Measured ordering:
  **Matérn >= fixed/inherited >> AdaptSplit.**

Two library fixes were prerequisites, both merged 2026-07-28: the PyAutoArray
Delaunay NaN-callback hardening (PR#411 — before it, one NaN lane killed the
whole vmapped batch AND poisoned the resume checkpoint) and the PyAutoFit
multi-start cadence fixes (#1423).

The Delaunay mesh's frozen-tables gradient is exact almost everywhere but
carries no information across triangulation-flip seams (C0), so global
progress leans on resurrection more than on the other meshes — for posterior
work route this mesh to tempered SMC or warm refits, not Hamiltonian kernels.
Budget/batching lessons as per the ``knn`` cell. Requires tfp-nightly.
"""

from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path


def _profiling_root() -> _Path:
    for _p in _Path(__file__).resolve().parents:
        if (_p / "ruff.toml").exists():
            return _p
    raise RuntimeError("autolens_profiling root (ruff.toml) not found")


_misc_dir = str(_profiling_root() / "scripts" / "misc")
if _misc_dir not in _sys.path:
    _sys.path.insert(0, _misc_dir)


import sys
from pathlib import Path

_REPO_ROOT = _profiling_root()
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from searches._runner import run_search  # noqa: E402

run_search(
    sampler="multi_start_prodigy",
    dataset_class="imaging",
    model_type="delaunay_matern",
    default_instrument="hst",
)
