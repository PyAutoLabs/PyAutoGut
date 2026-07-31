"""af.MultiStartProdigy search profiling — point-source image-plane (free centre).

JAX multi-start Prodigy gradient MAP optimizer on the solver-chained
``FitPositionsImagePairAll`` likelihood with a free-centre ``al.ps.PointFlux``
source — the same model/dataset as the ``nautilus/point_source/image_plane.py``
reference anchor, so the two cells compare directly (Nautilus posterior vs
gradient MAP). Gradients through the ``PointSolver`` come from the
implicit-diff ``custom_jvp`` (``autolens.point.solver.implicit_diff``, #657
phase 5); the solved-centre sibling is ``image_plane_solved.py``. Prodigy
self-tunes its learning rate. See ``searches/README.md``.
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

_REPO_ROOT = _profiling_root()  # autolens_profiling/
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from searches._runner import run_search  # noqa: E402

run_search(
    sampler="multi_start_prodigy",
    dataset_class="point_source",
    model_type="image_plane",
    default_instrument="simple",
)
