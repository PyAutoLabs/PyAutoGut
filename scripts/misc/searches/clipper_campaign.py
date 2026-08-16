"""Clipper validation campaign — arm-by-arm driver for the prior-support fix.

Phase 2 of the prior-support work (PyAutoFit#1476 / #1477). Runs the same cell
under each clipper arm and records the lane-death accounting *and* the best-fit
log-likelihood, so the claim being tested is not "fewer lanes die" but **does the
clipped run land closer to the Nautilus reference maximum**.

Why this exists rather than the ordinary `searches/` runner:

- The lane counters (`n_value_nan_lane_steps`, `n_grad_nan_lane_steps`,
  `n_constrained_lane_steps`, and the new `n_clipped_lane_steps`) are written
  into `search_internal`, which the ordinary results JSON does not carry.
- `search_internal` is **deleted on successful completion**, so it cannot be read
  back after the fit. It has to be captured as it is written.
- `save_search_internal` must be patched at **class** level: `fit()` rebuilds
  `search.paths`, so an instance-level hook is silently discarded.
- The `clipper` does **not** enter the search identifier, so two arms differing
  only in clipper resolve to the same output directory. Combined with the
  `.completed` short-circuit — which makes `fit()` return a cached result without
  entering `_fit` — arm 2 can silently return arm 1's numbers. Every arm here
  therefore gets a unique `name`, and the run asserts the recorded step count.

Usage::

    python scripts/misc/searches/clipper_campaign.py \
        --arms none,prior_box --n-starts 16 --n-steps 150

Results are written to ``results/notes/clipper_campaign/<cell>.json``.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import shutil
import sys
import time
from pathlib import Path


def _profiling_root() -> Path:
    for p in Path(__file__).resolve().parents:
        if (p / "ruff.toml").exists():
            return p
    raise RuntimeError("autolens_profiling root (ruff.toml) not found")


_ROOT = _profiling_root()
for _p in (str(_ROOT), str(_ROOT / "scripts" / "misc")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import numpy as np  # noqa: E402

import autofit as af  # noqa: E402
from autofit.non_linear.paths.directory import DirectoryPaths  # noqa: E402
from searches._setup import build_for_cell  # noqa: E402

# The structurally-immune reference: Nautilus samples in unit-cube coordinates,
# so it cannot suffer the prior-exit failure mode at all. Its maximum is the bar
# a clipped gradient run has to move toward for the fix to be worth shipping.
TRUTH_BAR = {
    ("imaging", "mge", "hst"): 31786.782462488976,
}

ARMS = {
    "none": lambda: af.ClipperNone(),
    "prior_box": lambda: af.ClipperPriorBox(),
}


def _capture_search_internal():
    """Patch `save_search_internal` at CLASS level and return (dict, restore).

    Class level is required: `fit()` rebuilds `search.paths`, so a hook attached
    to the instance that exists before the fit is thrown away mid-run.
    """
    captured: dict = {}
    real = DirectoryPaths.save_search_internal

    def spy(self, obj):
        captured.update(obj)
        return real(self, obj)

    DirectoryPaths.save_search_internal = spy

    def restore():
        DirectoryPaths.save_search_internal = real

    return captured, restore


def run_arm(
    *,
    arm: str,
    seed: int,
    dataset_class: str,
    model_type: str,
    instrument: str,
    n_starts: int,
    n_steps: int,
    sampler_cls,
    out_root: Path,
) -> dict:
    """One (arm, seed) fit. Returns the recorded row."""
    # Unique per arm AND seed: the clipper is not in the identifier, so a shared
    # name would let a completed run short-circuit the next one.
    name = f"clipper_campaign_{arm}_seed{seed}"
    run_dir = out_root / name
    # A stale `.completed` from a previous execution would make `fit()` return a
    # cached result without running. Clear it rather than trusting it is absent.
    shutil.rmtree(run_dir, ignore_errors=True)

    dataset, model, analysis = build_for_cell(
        dataset_class=dataset_class,
        model_type=model_type,
        instrument=instrument,
        use_jax=True,
    )

    # The broad-start draw is seeded with a hardcoded `default_rng(0)` inside
    # `_broad_starts`, so this only varies the initializer, not the start band.
    # See the campaign note: true multi-seed needs a `seed` arg on the search.
    random.seed(seed)
    np.random.seed(seed)

    search = sampler_cls(
        name=name,
        path_prefix=str(out_root.relative_to(_ROOT / "output"))
        if (_ROOT / "output") in out_root.parents
        else None,
        n_starts=n_starts,
        n_steps=n_steps,
        learning_rate=0.1,
        number_of_cores=1,
        convergence=af.MultiStartGradientConvergence(check_for_convergence=False),
        clipper=ARMS[arm](),
    )

    captured, restore = _capture_search_internal()
    t0 = time.time()
    try:
        result = search.fit(model=model, analysis=analysis)
    finally:
        restore()
    wall = time.time() - t0

    max_log_l = float(result.samples.max_log_likelihood_sample.log_likelihood)

    total_steps = captured.get("total_steps")
    # `0` and `null` are different findings: a missing key means the search never
    # wrote it (broken plumbing), not a clean cell.
    row = {
        "arm": arm,
        "seed": seed,
        "n_starts": n_starts,
        "n_steps": n_steps,
        "total_steps": total_steps,
        "steps_complete": total_steps == n_steps,
        "max_log_likelihood": max_log_l,
        "best_fom": captured.get("best_fom"),
        "stop_reason": captured.get("stop_reason"),
        "n_value_nan_lane_steps": captured.get("n_value_nan_lane_steps"),
        "n_grad_nan_lane_steps": captured.get("n_grad_nan_lane_steps"),
        "n_constrained_lane_steps": captured.get("n_constrained_lane_steps"),
        "n_clipped_lane_steps": captured.get("n_clipped_lane_steps"),
        "n_resurrections": captured.get("n_resurrections"),
        "wall_s": round(wall, 2),
    }

    bar = TRUTH_BAR.get((dataset_class, model_type, instrument))
    if bar is not None:
        row["truth_bar"] = bar
        row["gap_to_truth"] = bar - max_log_l

    # Count lanes ending pinned to a bound: the input to the momentum-reset
    # decision, and the "pinning is a result, not a failure" science finding.
    params = captured.get("params")
    if params is not None and arm != "none":
        lower, upper = af.ClipperPriorBox().bounds_from_model(model=model)
        p = np.asarray(params)
        atol = 1e-9 + 1e-6 * np.abs(np.where(np.isfinite(upper), upper, 0.0))
        pinned = (np.isclose(p, lower, atol=atol) | np.isclose(p, upper, atol=atol))
        row["lanes_pinned"] = int(np.count_nonzero(pinned.any(axis=-1)))
        row["pinned_coords"] = int(np.count_nonzero(pinned))

    return row


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="none,prior_box")
    ap.add_argument("--seeds", default="0")
    ap.add_argument("--dataset-class", default="imaging")
    ap.add_argument("--model-type", default="mge")
    ap.add_argument("--instrument", default="hst")
    ap.add_argument("--n-starts", type=int, default=16)
    ap.add_argument("--n-steps", type=int, default=150)
    ap.add_argument("--sampler", default="multi_start_adam")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    sampler_cls = {
        "multi_start_adam": af.MultiStartAdam,
        "multi_start_prodigy": af.MultiStartProdigy,
    }[args.sampler]

    out_root = Path(args.out) if args.out else _ROOT / "output" / "clipper_campaign"
    out_root.mkdir(parents=True, exist_ok=True)

    rows = []
    for arm in [a.strip() for a in args.arms.split(",") if a.strip()]:
        for seed in [int(s) for s in args.seeds.split(",") if s.strip()]:
            print(f"\n=== ARM {arm} seed {seed} ===", flush=True)
            row = run_arm(
                arm=arm,
                seed=seed,
                dataset_class=args.dataset_class,
                model_type=args.model_type,
                instrument=args.instrument,
                n_starts=args.n_starts,
                n_steps=args.n_steps,
                sampler_cls=sampler_cls,
                out_root=out_root,
            )
            rows.append(row)
            print(json.dumps(row, indent=2), flush=True)

    cell = f"{args.sampler}_{args.dataset_class}_{args.model_type}_{args.instrument}"
    dest = _ROOT / "results" / "notes" / "clipper_campaign"
    dest.mkdir(parents=True, exist_ok=True)
    (dest / f"{cell}.json").write_text(json.dumps({"cell": cell, "rows": rows}, indent=2))

    print("\n" + "=" * 78)
    print(f"CLIPPER CAMPAIGN — {cell}")
    print("=" * 78)
    hdr = f"{'arm':10s} {'seed':>4s} {'steps':>6s} {'maxlogL':>14s} {'gap':>10s} {'deaths':>7s} {'clips':>7s} {'pinned':>7s}"
    print(hdr)
    for r in rows:
        print(
            f"{r['arm']:10s} {r['seed']:4d} {str(r['total_steps']):>6s} "
            f"{r['max_log_likelihood']:14.3f} "
            f"{r.get('gap_to_truth', float('nan')):10.3f} "
            f"{str(r['n_value_nan_lane_steps']):>7s} "
            f"{str(r['n_clipped_lane_steps']):>7s} "
            f"{str(r.get('lanes_pinned', '-')):>7s}"
        )
    print(f"\nwritten: {dest / f'{cell}.json'}")


if __name__ == "__main__":
    main()
