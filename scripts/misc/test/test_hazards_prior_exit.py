"""The prior-exit hazard detector (autolens_profiling#128)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest


def _misc_dir() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "ruff.toml").exists():
            return parent / "scripts" / "misc"
    raise RuntimeError("autolens_profiling root (ruff.toml) not found")


sys.path.insert(0, str(_misc_dir()))

from hazards.checks import CHECKS  # noqa: E402
from hazards.checks._base import ScanContext  # noqa: E402
from hazards.checks.prior_exit import PriorExitCheck  # noqa: E402


@pytest.fixture
def context():
    return ScanContext(
        repo_root=Path("."),
        workspace_root=_misc_dir().parents[1].parent,
        output_root=Path("."),
        backends=("numpy", "jax"),
        sample_count=500,
        seed=0,
    )


def test__prior_exit_is_registered():
    assert any(isinstance(check, PriorExitCheck) for check in CHECKS)


def test__non_finite_exactly_where_the_value_left_the_box(context):
    # The decisive property: the -inf tracks the box EDGE, so this is a support
    # boundary rather than a numerical instability that happens to be nearby.
    finding = PriorExitCheck().run(context)[0]

    assert finding.reproducer["non_finite_iff_outside"] is True
    assert finding.reproducer["outside_box"] > 0
    assert finding.reproducer["non_finite_log_prior"] == finding.reproducer["outside_box"]


def test__numpy_path_does_not_evaluate_the_bound(context):
    # `log_prior_from_value` short-circuits to a scalar 0.0 under NumPy and only
    # returns -inf under JAX. The hazard therefore lives on the JAX path — which
    # is the one the gradient searches use. If this ever flips, the finding's
    # backend_reachability is stale and the reader would be misled about which
    # backend can actually lose lanes.
    finding = PriorExitCheck().run(context)[0]

    assert finding.reproducer["numpy_evaluates_bound"] is False
    assert finding.backend_reachability["numpy"]["log_prior_outside_box"].startswith("zero")
    assert finding.backend_reachability["jax"]["log_prior_outside_box"] == "non_finite"


def test__records_the_clipper_as_what_blocks_it(context):
    # The mitigation is opt-in, so the hazard must still report as existing
    # while naming what blocks it.
    finding = PriorExitCheck().run(context)[0]

    assert finding.code_exists is True
    assert finding.affects_science is True
    assert any("ClipperPriorBox" in anchor.symbol for anchor in finding.blocked_by)


def test__a_numpy_only_scan_does_not_claim_to_have_adjudicated_it():
    # Same discipline as the autodiff hazards: without the backend that exhibits
    # it, the scan must not report the hazard as resolved.
    numpy_only = ScanContext(
        repo_root=Path("."),
        workspace_root=_misc_dir().parents[1].parent,
        output_root=Path("."),
        backends=("numpy",),
        sample_count=200,
        seed=0,
    )
    finding = PriorExitCheck().run(numpy_only)[0]

    assert finding.reproducer["adjudicated"] is False
    assert finding.reproducer["hazard_persists"] is True
    assert "jax" not in finding.backend_reachability
