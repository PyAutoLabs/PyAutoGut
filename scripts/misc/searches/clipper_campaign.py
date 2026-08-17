"""Clipper validation campaign — arm-by-arm driver for the prior-support fix.

Phase 2 of the prior-support work (PyAutoFit#1476 / #1477). Runs the same cell
under each clipper arm and records the lane-death accounting *and* the best-fit
log-likelihood, so the claim being tested is not "fewer lanes die" but **does the
clipped run land closer to the Nautilus reference maximum**.

Why this exists rather than the ordinary `searches/` runner:

- The lane counters (`n_value_nan_lane_steps`, `n_grad_nan_lane_steps`,
  `n_constrained_lane_steps`, and the new `n_clipped_lane_steps`) are written
  into `search_internal`, which the ordinary results JSON does not carry.
  **Partly superseded by PyAutoFit#1478**, which surfaces the clip count and the
  constrained count in `search.summary` — prefer reading them from there, and
  treat a `ClipperPriorBox` arm reporting zero clips as a broken arm rather than
  a null result.
- `search_internal` is **deleted on successful completion**, so the raw dict
  cannot be read back after the fit. It has to be captured as it is written.
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

import autofit as af  # noqa: E402
import numpy as np  # noqa: E402
from autofit.non_linear.paths.directory import DirectoryPaths  # noqa: E402
from autonerves import conf  # noqa: E402
from searches._setup import build_for_cell  # noqa: E402

# The structurally-immune reference: Nautilus samples in unit-cube coordinates,
# so it cannot suffer the prior-exit failure mode at all. Its maximum is the bar
# a clipped gradient run has to move toward for the fix to be worth shipping.
TRUTH_BAR = {
    ("imaging", "mge", "hst"): 31786.782462488976,
}

# arm -> (clipper factory, extra-search-kwargs factory).
#
# Both halves are FACTORIES, called per run rather than shared. The extras used
# to be literal dicts, which was safe only because every value in them was a
# bool; `prior_box_scaled` puts a strategy OBJECT in there, and a module-level
# instance silently shared by two arms of the same sweep is the kind of thing
# that only bites once a strategy becomes stateful.
#
# `prior_box_reset` is the third arm the campaign called for: projection alone
# leaves a clipped lane holding the velocity that took it out of the box, so it
# is re-projected onto the same bound every step. Measured at 16x3000 it does NOT
# pay off (deaths 2 -> 2523, one more lane pinned, +39% wall on seed 0) and the
# campaign recommends against it; it stays here so that row is reproducible.
#
# `prior_box_scaled` is the CAUSE-side arm (PyAutoFit#1483). The clipper stays ON
# in it deliberately: the two features are complementary, and with clipping on
# the clip RATE becomes the direct measure of whether steps are now commensurate
# with prior widths. An arm with the clipper off would confound the two.
ARMS = {
    "none": (af.ClipperNone, dict),
    "prior_box": (af.ClipperPriorBox, dict),
    "prior_box_reset": (af.ClipperPriorBox, lambda: {"reset_momentum_on_clip": True}),
    "prior_box_scaled": (af.ClipperPriorBox, lambda: {"scaler": af.ScalerPriorWidth()}),
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


def _summary_counters(search) -> dict:
    """Parse ``search.summary`` (PyAutoFit#1478 surfaces the clip counters there).

    The file is ``Key = Value`` per line — NOT colon-separated. A colon parser
    returns an EMPTY dict, so every counter reads as ``None``, which is
    indistinguishable from a clipper that never fired. That failure mode is
    silent and produces a plausible-looking "no clipping" result, so the parse
    is asserted below rather than trusted.
    """
    path = Path(search.paths.output_path) / "search.summary"
    if not path.exists():
        return {}
    out = {}
    for line in path.read_text().splitlines():
        if "=" in line:
            key, _, value = line.partition("=")
            out[key.strip()] = value.strip()
    return out


def run_arm(
    *,
    arm: str,
    seed: int,
    dataset_class: str,
    model_type: str,
    instrument: str,
    n_starts: int,
    n_steps: int,
    learning_rate: float,
    sampler_cls,
    out_root: Path,
    negative_control: bool = False,
) -> dict:
    """One (arm, seed) fit. Returns the recorded row."""
    # Unique per arm AND seed: the clipper is not in the identifier, so a shared
    # name would let a completed run short-circuit the next one. The control
    # runs a DIFFERENT model under the same arm names, so it needs its own
    # namespace too or it would collide with the main campaign's runs.
    prefix = "clipper_control" if negative_control else "clipper_campaign"
    name = f"{prefix}_{arm}_seed{seed}"
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

    if negative_control:
        # THE NEGATIVE CONTROL. Every prior becomes an unbounded Gaussian, so
        # `bounds_from_model` yields (-inf, +inf) everywhere and
        # `ClipperPriorBox` has nothing to project onto: it must be an exact
        # no-op. If this arm clips even once, or differs from the `none` arm,
        # the bounds extraction is wrong.
        #
        # Each Gaussian is centred on its uniform box with sigma = the box
        # width, so the search explores a comparable region rather than a
        # different problem — the control tests the clipper, not the model.
        model = model.replacing(
            {
                prior: af.GaussianPrior(
                    mean=0.5 * (prior.lower_limit + prior.upper_limit),
                    sigma=(prior.upper_limit - prior.lower_limit),
                )
                for prior in model.priors
                if isinstance(prior, af.UniformPrior)
            }
        )

    # Seeded on three levels, because they are three different generators:
    # `random`/`numpy` reach the initializer, and the search's own `seed` reaches
    # the broad-start draw and the resurrection redraw. Before `seed` existed the
    # start band was a hardcoded `default_rng(0)`, so every "seed" here drew the
    # SAME starting population and a multi-seed study was silently single-seed.
    random.seed(seed)
    np.random.seed(seed)

    kwargs = dict(
        name=name,
        n_starts=n_starts,
        n_steps=n_steps,
        seed=seed,
        number_of_cores=1,
        convergence=af.MultiStartGradientConvergence(check_for_convergence=False),
        clipper=ARMS[arm][0](),
        **ARMS[arm][1](),
    )
    # Prodigy is learning-rate-FREE: it estimates its own step scale and its
    # `_default_learning_rate` is None. Passing a rate would override that
    # estimate with a hand-picked constant, quietly turning the lr-free arm into
    # a badly-tuned fixed-rate one and invalidating the comparison.
    if sampler_cls is not af.MultiStartProdigy:
        kwargs["learning_rate"] = learning_rate

    search = sampler_cls(**kwargs)

    captured, restore = _capture_search_internal()
    t0 = time.time()
    try:
        result = search.fit(model=model, analysis=analysis)
    finally:
        restore()
    wall = time.time() - t0

    max_log_l = float(result.samples.max_log_likelihood_sample.log_likelihood)

    summary = _summary_counters(search)

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
        # The per-parameter step scale the search actually derived, so the arm's
        # numbers can be read against the vector that produced them rather than
        # against a rule re-derived by hand months later. `None` on the unscaled
        # arms, which is the honest record: they had no scale, as opposed to a
        # scale of all ones that was computed and applied.
        "scale": (
            [float(s) for s in np.asarray(captured["scale"])]
            if captured.get("scale") is not None
            else None
        ),
        "wall_s": round(wall, 2),
        # What the search itself reported, kept alongside the captured dict so a
        # disagreement between the two is visible in the artefact rather than
        # resolved silently in favour of whichever was read first.
        "summary_clipper": summary.get("Clipper"),
        "summary_clipped_lane_steps": summary.get("Clipped Lane-Steps"),
        "summary_value_nan_lane_steps": summary.get("Value-NaN Lane-Steps"),
    }

    # The alive-versus-step CURVE. This is the quantity to grade on: the lane
    # counters above are survival integrals, so a dead lane keeps adding to them
    # every later step and the same death curve reads ~60% at 150 steps and ~75%
    # at 300. Two arms at different budgets cannot be compared on the scalar.
    alive_history = captured.get("alive_history")
    if alive_history is not None:
        alive = np.asarray(alive_history).astype(int).tolist()
        row["alive_history"] = alive
        row["alive_final"] = alive[-1] if alive else None
        row["alive_min"] = min(alive) if alive else None
        # Area under the curve, normalised: 1.0 = every lane alive at every
        # step. Budget-independent, so it IS comparable across arms.
        row["alive_fraction"] = round(sum(alive) / (n_starts * len(alive)), 4) if alive else None

    # --- validity checks ---
    #
    # Recorded on the row rather than raised. A raise here would abandon every
    # arm already completed in this sweep, which on a multi-hour GPU run means
    # discarding good results because a later arm was broken. `main` exits
    # non-zero if any arm is invalid, so this is not silent.
    problems = []

    # A short-circuited run reports the PREVIOUS run's counters rather than
    # zeros, so a zero-check alone would not catch it.
    if total_steps != n_steps:
        problems.append(
            f"recorded total_steps={total_steps} but asked for n_steps={n_steps}: "
            f"the run did not complete, or returned a cached result, so its "
            f"counters describe a different run"
        )

    # A ClipperPriorBox arm that never clipped has not exercised the clipper.
    # That is a broken arm, not a null result, and its "no change" means
    # nothing. It is also the signature of the arm-collision trap.
    #
    # It is equally the signature of a box that simply contains the optimum, or
    # of a budget too short for any lane to reach a bound — phase 1's first
    # efficacy attempt measured 0 clips for exactly that reason. Either way the
    # arm cannot speak to the question, which is why it is flagged rather than
    # interpreted.
    if negative_control:
        # The expectation INVERTS here. With every prior unbounded the clipper
        # has nothing to project onto, so zero clips is the PASS condition and
        # any clip at all means the bounds extraction invented a bound.
        row["control_pass"] = row["n_clipped_lane_steps"] == 0
        if row["n_clipped_lane_steps"]:
            problems.append(
                f"NEGATIVE CONTROL FAILED: n_clipped_lane_steps="
                f"{row['n_clipped_lane_steps']!r} on an all-Gaussian-prior model. "
                f"ClipperPriorBox must be a no-op where no prior is bounded — the "
                f"bounds extraction is wrong"
            )
    elif arm == "prior_box_scaled":
        # The expectation inverts again, and for a THIRD reason. On a scaled arm
        # zero clips is the hoped-for RESULT — the whole point is that steps
        # become commensurate with prior widths so lanes stop reaching walls — so
        # the clip count cannot double as the proof that the arm ran. It has to
        # be proved from the scale vector instead: the arm is exercised iff a
        # non-trivial scale was actually derived and applied.
        #
        # Without this the campaign would report its own success as a broken arm,
        # which is precisely the way a null result gets manufactured.
        scale = row.get("scale")
        if not scale:
            problems.append(
                "no scale vector recorded: the scaler never ran, so this arm "
                "tests nothing (check that `autofit.__file__` resolves to the "
                "task checkout — ScalerPriorWidth is unreleased)"
            )
        elif max(scale) / min(scale) < 1.5:
            problems.append(
                f"scale spread is only {max(scale) / min(scale):.3f}x: the "
                f"derived scale is effectively uniform, so this arm is not "
                f"testing per-parameter scaling on this model"
            )
    elif arm != "none" and not row["n_clipped_lane_steps"]:
        problems.append(
            f"n_clipped_lane_steps={row['n_clipped_lane_steps']!r}: the clipper "
            f"never fired, so this arm tests nothing. Either the arms collided, "
            f"the priors are unbounded, or no lane reached a bound at this budget"
        )

    row["valid"] = not problems
    row["invalid_reasons"] = problems
    if problems:
        print(f"  !! INVALID ARM {arm!r} seed {seed}:", flush=True)
        for p in problems:
            print(f"     - {p}", flush=True)

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
        pinned = np.isclose(p, lower, atol=atol) | np.isclose(p, upper, atol=atol)
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
    ap.add_argument("--learning-rate", type=float, default=0.1)
    ap.add_argument("--sampler", default="multi_start_adam")
    ap.add_argument("--out", default=None)
    # Calibration / sanity runs point this at a scratch dir so their rows are
    # not merged into the campaign's real artefact.
    ap.add_argument("--results-dir", default=None)
    ap.add_argument(
        "--negative-control",
        action="store_true",
        help="Replace every UniformPrior with an unbounded GaussianPrior. "
        "ClipperPriorBox must then be an exact no-op.",
    )
    args = ap.parse_args()

    sampler_cls = {
        "multi_start_adam": af.MultiStartAdam,
        "multi_start_prodigy": af.MultiStartProdigy,
    }[args.sampler]

    out_root = Path(args.out) if args.out else _ROOT / "output" / "clipper_campaign"
    out_root.mkdir(parents=True, exist_ok=True)

    # The search must actually write UNDER `out_root`, or `--out` is a lie and
    # the per-arm directory clearing silently targets a directory the search
    # never used. That bit once already: with `--out` pointing outside the repo
    # the run wrote to the default output path, kept a stale `.completed`
    # there, and the next arm short-circuited to a CACHED result in 2.9s while
    # every counter came back `None`. Setting the output root here is what makes
    # the clearing in `run_arm` meaningful.
    conf.instance.output_path = str(out_root)

    cell = f"{args.sampler}_{args.dataset_class}_{args.model_type}_{args.instrument}"
    if args.negative_control:
        cell += "_negative_control"
    dest = (
        Path(args.results_dir)
        if args.results_dir
        else _ROOT / "results" / "notes" / "clipper_campaign"
    )
    dest.mkdir(parents=True, exist_ok=True)
    dest_file = dest / f"{cell}.json"

    # Arms are hours apart on a GPU. Results are merged into whatever is already
    # on disk and rewritten after EVERY arm, so a killed or crashed sweep keeps
    # the arms it finished and a later invocation can add one arm without
    # re-running the rest. Keyed by (arm, seed) so a re-run replaces its own row
    # rather than accumulating duplicates.
    rows: dict[tuple[str, int], dict] = {}
    if dest_file.exists():
        for row in json.loads(dest_file.read_text()).get("rows", []):
            rows[(row["arm"], row["seed"])] = row

    def flush_rows():
        ordered = sorted(rows.values(), key=lambda r: (r["arm"], r["seed"]))
        dest_file.write_text(json.dumps({"cell": cell, "rows": ordered}, indent=2))

    for arm in [a.strip() for a in args.arms.split(",") if a.strip()]:
        for seed in [int(s) for s in args.seeds.split(",") if s.strip()]:
            print(f"\n=== ARM {arm} seed {seed} ===", flush=True)
            try:
                row = run_arm(
                    arm=arm,
                    seed=seed,
                    dataset_class=args.dataset_class,
                    model_type=args.model_type,
                    instrument=args.instrument,
                    n_starts=args.n_starts,
                    n_steps=args.n_steps,
                    learning_rate=args.learning_rate,
                    sampler_cls=sampler_cls,
                    out_root=out_root,
                    negative_control=args.negative_control,
                )
            except Exception as exc:  # noqa: BLE001 — one arm must not sink the sweep
                import traceback

                traceback.print_exc()
                row = {
                    "arm": arm,
                    "seed": seed,
                    "valid": False,
                    "invalid_reasons": [f"arm raised {type(exc).__name__}: {exc}"],
                }
            rows[(arm, seed)] = row
            flush_rows()
            print(json.dumps(row, indent=2), flush=True)

    rows_list = sorted(rows.values(), key=lambda r: (r["arm"], r["seed"]))
    flush_rows()

    print("\n" + "=" * 78)
    print(f"CLIPPER CAMPAIGN — {cell}")
    print("=" * 78)
    # `alive` is the area under the alive-versus-step curve (1.0 = every lane
    # alive at every step). It is the budget-independent survival measure; the
    # `deaths` column beside it is an integral and is NOT comparable between
    # runs of different length.
    hdr = (
        f"{'arm':12s} {'seed':>4s} {'steps':>6s} {'maxlogL':>14s} {'gap':>11s} "
        f"{'deaths':>7s} {'clips':>7s} {'alive':>6s} {'pinned':>6s}  ok"
    )
    print(hdr)
    for r in rows_list:
        if not r.get("valid", True) and "total_steps" not in r:
            print(f"{r['arm']:12s} {r['seed']:4d}  -- arm failed, see invalid_reasons --")
            continue
        print(
            f"{r['arm']:12s} {r['seed']:4d} {str(r['total_steps']):>6s} "
            f"{r['max_log_likelihood']:14.3f} "
            f"{r.get('gap_to_truth', float('nan')):11.3f} "
            f"{str(r['n_value_nan_lane_steps']):>7s} "
            f"{str(r['n_clipped_lane_steps']):>7s} "
            f"{str(r.get('alive_fraction', '-')):>6s} "
            f"{str(r.get('lanes_pinned', '-')):>6s}  "
            f"{'y' if r.get('valid', True) else 'NO'}"
        )
    print(f"\nwritten: {dest_file}")

    invalid = [r for r in rows_list if not r.get("valid", True)]
    if invalid:
        print(f"\n{len(invalid)} INVALID arm(s) — these cannot be interpreted:")
        for r in invalid:
            for reason in r.get("invalid_reasons", []):
                print(f"  {r['arm']} seed {r['seed']}: {reason}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
