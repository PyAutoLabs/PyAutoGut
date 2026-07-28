"""First-class af.MultiStartProdigy search profiling — imaging KNN pixelized source.

Promoted from the autolens_workspace_developer#117 campaign (2026-07,
``searches_minimal/pix_prodigy_findings.md``), which validated broad-start
multi-start gradient search on every pixelized mesh. The KNN (Wendland-C4)
mesh was the fastest converger, and **beat a matched-settings Nautilus
baseline by ~24k nats while landing in the truth basin the sampler missed**
(+29724 @ r_E 1.599 vs +5704 @ r_E 1.011, at ~1/5 the CPU wall).

Why this cell works (the #117 lessons, baked into the framework defaults):

- **Prodigy is learning-rate-free** — on pixelized cells it converges where
  hand-tuned adam-era runs sat 190k nats short (#100/#101).
- **resurrection-compatible landscape**: KNN's high-regularization region is
  an over-regularized floor (bad but *finite*), so dying starts redraw and
  eventually cross regularization modes. The exact-truth mode arrived at step
  ~1300 after a 1000-step plateau at a suboptimal reg mode — hence the
  3000-step budget (``_MULTI_START_N_STEPS_BY_CELL``): **a long plateau is a
  reg mode, not convergence.**
- **batch_size=4 is mandatory** on pixelized cells (the unbatched 16-start
  jvp fusion is the ~58 GB allocation; PyAutoFit#1374 tiling is numerically
  inert).

Model: MGE lens light (linear amplitudes) + free broad Isothermal/shear +
``KNearestNeighbor`` source with free ``AdaptSplit`` regularization — the
SLaM ``source_pix[1]`` shape. See ``searches/README.md`` and
``_setup._knn_model`` for the reg-parametrization caveats.
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
    model_type="knn",
    default_instrument="hst",
)
