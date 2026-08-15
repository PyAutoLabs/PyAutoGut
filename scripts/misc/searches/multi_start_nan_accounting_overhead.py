"""
Does MultiStartGradient's per-step NaN accounting cost any run time?

``MultiStartGradient`` counts, per step, how many lanes are non-finite in VALUE
(likelihood undefined) and how many are non-finite in GRADIENT (likelihood
defined but not differentiable -- a lane that ``optax.apply_if_finite`` freezes
in place while it still counts as alive). See PyAutoFit#1472.

The value side was already computed. The gradient side is new, and it reads an
``(n_starts, ndim)`` array that until now never left the device. This script
answers whether that costs anything, against a REAL likelihood rather than a toy.

The feature ships unconditionally -- there is no flag to A/B inside one process,
and a standalone script cannot hold two library versions at once. So rather than
fake a toggle, this measures the two halves separately and divides:

    denominator   one step of jax.jit(jax.vmap(jax.value_and_grad(f))) on a real
                  lens likelihood at realistic (n_starts, ndim) shapes -- the
                  same code path and shapes the fit loop runs
    numerator     each accounting variant applied to that same gradient output

Variants:

    baseline  today's loop: alive = np.isfinite(np.asarray(foms))
    control   a SECOND, identical baseline. Not decorative -- it is the noise
              floor. Without it this script could only ever report "we measured
              no impact", which is unfalsifiable; with it, it reports "below a
              floor of X%", a claim that could have failed.
    host      + np.all(np.isfinite(np.asarray(grads)), axis=1)
              the literal reading: pull the whole gradient to host
    eager     + np.asarray(jnp.all(jnp.isfinite(grads), axis=1))
              reduce on device, but OUTSIDE the jit
    fused     finiteness returned as a third output of the jitted call
              (what PyAutoFit#1472 ships)

Note ``eager`` looks like the obvious optimization over ``host`` -- it shrinks
the transfer from (n_starts, ndim) floats to (n_starts,) bools -- and it is in
fact the WORST of the three, because an un-jitted reduction buys a kernel
dispatch plus a second host round-trip to save a few KB that were never the
cost. That inversion is the point of measuring.

**Backend matters.** On CPU a device->host copy is a memcpy in the same address
space, so ``host`` looks nearly free there and its cost only appears on GPU. Run
this on both before drawing conclusions; ``fused`` is the safe pick either way,
since it adds neither a launch nor a round-trip.

Usage (from the ``autolens_profiling/`` root)::

    python scripts/misc/searches/multi_start_nan_accounting_overhead.py
    python scripts/misc/searches/multi_start_nan_accounting_overhead.py --model-type pixelization
    python scripts/misc/searches/multi_start_nan_accounting_overhead.py --n-starts 8 --reps 9

Writes a JSON + PNG pair under
``results/searches/multi_start_nan_accounting/<hardware>.json``.
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


import argparse  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import platform  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402

_WORKSPACE_ROOT = _profiling_root()
if str(_WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(_WORKSPACE_ROOT))

if os.environ.get("AUTOLENS_PROFILING_SMOKE") == "1":
    print(f"[smoke] {__file__}: imports + module setup OK; exiting.")
    raise SystemExit(0)


N_STARTS_DEFAULT = 16
N_STEPS_DEFAULT = 50
WARMUP_STEPS = 5
REPS_DEFAULT = 7
ACCOUNTING_REPS = 2000
ACCOUNTING_CALL_REPS = 20

VARIANTS = ("baseline", "control", "host", "eager", "fused")


def parse_args():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    p.add_argument("--dataset-class", default="imaging")
    p.add_argument("--model-type", default="mge", help="mge | pixelization | delaunay")
    p.add_argument("--instrument", default="hst")
    p.add_argument("--n-starts", type=int, default=N_STARTS_DEFAULT)
    p.add_argument("--n-steps", type=int, default=N_STEPS_DEFAULT)
    p.add_argument("--reps", type=int, default=REPS_DEFAULT)
    p.add_argument("--mixed-precision", action="store_true")
    p.add_argument("--tag", default="", help="free-form tag recorded in the JSON")
    return p.parse_args()


def hardware_label(jax) -> str:
    kind = jax.default_backend()
    if kind == "gpu":
        dev = jax.devices()[0]
        return f"local_gpu_{dev.device_kind.replace(' ', '_')}"
    return f"local_{kind}"


def build_objective(args):
    """The real negative-log-posterior the gradient samplers optimize."""
    import jax.numpy as jnp
    from searches._setup import build_for_cell

    _dataset, model, analysis = build_for_cell(
        dataset_class=args.dataset_class,
        model_type=args.model_type,
        instrument=args.instrument,
        use_jax=True,
        use_mixed_precision=args.mixed_precision,
    )

    def f(params):
        instance = model.instance_from_vector(vector=params, xp=jnp)
        log_l = analysis.log_likelihood_function(instance=instance)
        log_p = jnp.sum(jnp.asarray(model.log_prior_list_from_vector(vector=params, xp=jnp)))
        return -(log_l + log_p)

    x0 = jnp.asarray(model.vector_from_unit_vector([0.5] * model.prior_count))
    return f, x0, model.prior_count


def build_callables(f):
    """The two jitted entry points: today's 2-tuple, and the fused 3-tuple."""
    import jax
    import jax.numpy as jnp

    vag = jax.value_and_grad(f)

    def _vag_finite(vector):
        fom, grad = vag(vector)
        return fom, grad, jnp.all(jnp.isfinite(grad))

    return jax.jit(jax.vmap(vag)), jax.jit(jax.vmap(_vag_finite))


def run_variant(variant, vmapped, fused, params, n_steps):
    """One timed loop, shaped like the real fit loop.

    Every variant syncs on ``foms`` and consumes ``grads``, exactly as the fit
    loop does; they differ ONLY in how gradient finiteness is obtained.
    """
    import jax.numpy as jnp
    import numpy as np

    sink = 0.0
    for _ in range(n_steps):
        if variant == "fused":
            foms, grads, grad_finite_dev = fused(params)
            alive = np.isfinite(np.asarray(foms))
            grad_finite = np.asarray(grad_finite_dev)
        else:
            foms, grads = vmapped(params)
            alive = np.isfinite(np.asarray(foms))
            if variant == "host":
                grad_finite = np.all(np.isfinite(np.asarray(grads)), axis=1)
            elif variant == "eager":
                grad_finite = np.asarray(jnp.all(jnp.isfinite(grads), axis=1))
            else:  # baseline / control -- no gradient accounting at all
                grad_finite = None

        # Stand-in for step_update + apply_updates: keeps `grads` consumed on
        # device so the variants differ only in the accounting, not in whether
        # the gradient is used at all.
        params = params - 1e-6 * grads

        sink += float(alive.sum())
        if grad_finite is not None:
            sink += float(grad_finite.sum())

    return sink


def measure(args, vmapped, fused, params):
    """Interleaved reps so slow drift hits every variant equally.

    Progress is printed per rep. On CPU a real 16-start lens likelihood makes
    the full grid a many-minute run, and a silent process is indistinguishable
    from a hung one -- the first rep also absorbs the XLA compile, so the wait
    before any output is the longest of the run.
    """
    total_steps = args.reps * len(VARIANTS) * args.n_steps
    print(
        f"[bench] {len(VARIANTS)} variants x {args.reps} reps x {args.n_steps} "
        f"steps = {total_steps} timed steps (plus warmup + compile)",
        flush=True,
    )

    t_warm = time.perf_counter()
    for variant in VARIANTS:
        run_variant(
            "baseline" if variant == "control" else variant,
            vmapped,
            fused,
            params,
            WARMUP_STEPS,
        )
    print(
        f"[bench] warmup + compile done in {time.perf_counter() - t_warm:.1f}s",
        flush=True,
    )

    samples = {v: [] for v in VARIANTS}
    t_start = time.perf_counter()
    for rep in range(args.reps):
        for variant in VARIANTS:
            actual = "baseline" if variant == "control" else variant
            t0 = time.perf_counter()
            run_variant(actual, vmapped, fused, params, args.n_steps)
            elapsed = time.perf_counter() - t0
            samples[variant].append(elapsed / args.n_steps * 1e6)

        done = time.perf_counter() - t_start
        eta = done / (rep + 1) * (args.reps - rep - 1)
        print(
            f"[bench] rep {rep + 1}/{args.reps} done ({done:.1f}s elapsed, ~{eta:.0f}s remaining)",
            flush=True,
        )

    return samples


def measure_accounting_only(args, vmapped, fused, params):
    """Time the accounting op ALONE, at microsecond resolution.

    This is the discriminating measurement, and the reason the script does not
    simply diff two end-to-end loops. A real lens step costs ~1s; the accounting
    costs ~10-60us. Differencing whole loops therefore asks a stopwatch with
    ~10ms of run-to-run jitter to resolve a 30us effect -- a ~200x resolution
    gap, which shows up as variants coming out NEGATIVE (faster than a baseline
    that does strictly less work). Such a run cannot distinguish `fused` from a
    variant costing 9ms; it would call both "below the noise floor".

    So: measure the numerator directly on a cached gradient (no likelihood in
    the loop, thousands of reps), and divide by the separately-measured real
    step cost. Both halves are then measured where each is resolvable.
    """
    import jax
    import jax.numpy as jnp
    import numpy as np

    foms, grads = vmapped(params)
    jax.block_until_ready((foms, grads))

    def _host():
        return np.all(np.isfinite(np.asarray(grads)), axis=1)

    def _eager():
        return np.asarray(jnp.all(jnp.isfinite(grads), axis=1))

    def _noop():
        return None

    ops = {"control": _noop, "host": _host, "eager": _eager}

    # `fused` has no isolated cost to time: its reduction happens inside the
    # jitted call, so it is measured as the delta between the two jitted
    # entry points rather than as a separate op.
    reps = ACCOUNTING_REPS
    out = {}
    for name, op in ops.items():
        best = None
        for _ in range(5):
            t0 = time.perf_counter()
            for _ in range(reps):
                op()
            elapsed = (time.perf_counter() - t0) / reps * 1e6
            best = elapsed if best is None else min(best, elapsed)
        out[name] = best

    # fused vs today's call: same work, one extra (n_starts,) bool output.
    def _time_call(fn):
        best = None
        for _ in range(5):
            t0 = time.perf_counter()
            for _ in range(ACCOUNTING_CALL_REPS):
                jax.block_until_ready(fn(params))
            elapsed = (time.perf_counter() - t0) / ACCOUNTING_CALL_REPS * 1e6
            best = elapsed if best is None else min(best, elapsed)
        return best

    # `fused` is measured on a PROXY objective, not by differencing the two real
    # jitted calls. Differencing two ~1s calls to resolve a ~5us effect hits the
    # exact resolution collapse this function exists to avoid -- it returns
    # plausible-looking nonsense, including negative "costs".
    #
    # What fused actually adds is a jnp.all(isfinite(.)) reduction over an
    # (n_starts, ndim) array plus one (n_starts,) bool output. That cost is a
    # property of the SHAPES, not of the likelihood, so it is measurable at the
    # same shapes over a trivial objective where the step is short enough to
    # resolve.
    #
    # Caveat this cannot see: XLA fuses the reduction into whatever backward
    # pass it sits in, so the proxy measures the reduction in isolation rather
    # than its interaction with the real gradient graph. It is an upper bound on
    # a fused cost, not the fused cost itself.
    out["fused"] = _fused_marginal_us(params.shape)

    # The op-only numbers include Python call overhead (the `_noop` control
    # measures exactly that); subtract it so each figure is the op itself.
    overhead = out.pop("control")
    return {k: v - overhead for k, v in out.items()}, overhead


def _fused_marginal_us(shape):
    """Marginal cost of the fused finiteness output, at the real array shapes."""
    import jax
    import jax.numpy as jnp

    def cheap(vector):
        return jnp.sum(vector**2)

    def cheap_finite(vector):
        fom, grad = jax.value_and_grad(cheap)(vector)
        return fom, grad, jnp.all(jnp.isfinite(grad))

    plain = jax.jit(jax.vmap(jax.value_and_grad(cheap)))
    finite = jax.jit(jax.vmap(cheap_finite))

    x = jnp.ones(shape)
    jax.block_until_ready(plain(x))
    jax.block_until_ready(finite(x))

    def _best(fn):
        best = None
        for _ in range(5):
            t0 = time.perf_counter()
            for _ in range(ACCOUNTING_REPS):
                jax.block_until_ready(fn(x))
            elapsed = (time.perf_counter() - t0) / ACCOUNTING_REPS * 1e6
            best = elapsed if best is None else min(best, elapsed)
        return best

    return _best(finite) - _best(plain)


def summarise(samples):
    import numpy as np

    base = min(samples["baseline"])
    rows = []
    for variant in VARIANTS:
        best = min(samples[variant])
        rows.append(
            {
                "variant": variant,
                "us_per_step": best,
                "us_per_step_median": float(np.median(samples[variant])),
                "overhead_us": best - base,
                "overhead_percent": 100.0 * (best - base) / base,
            }
        )
    noise_floor = 100.0 * (min(samples["control"]) - base) / base
    return rows, noise_floor


def plot(rows, noise_floor, out_path, title):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plotted = [r for r in rows if r["variant"] != "baseline"]
    names = [r["variant"] for r in plotted]
    values = [r["overhead_percent"] for r in plotted]

    fig, ax = plt.subplots(figsize=(7, 4))
    colours = ["#999999" if n == "control" else "#3b7dd8" for n in names]
    ax.bar(names, values, color=colours)
    ax.axhline(
        abs(noise_floor),
        color="#c0392b",
        linestyle="--",
        label=f"noise floor ({abs(noise_floor):.2f}%)",
    )
    ax.set_ylabel("overhead vs baseline (% per step)")
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=140)
    plt.close(fig)


def main():
    args = parse_args()

    import jax

    f, x0, ndim = build_objective(args)
    vmapped, fused = build_callables(f)

    import jax.numpy as jnp

    params = jnp.tile(x0, (args.n_starts, 1))

    accounting_us, call_overhead_us = measure_accounting_only(args, vmapped, fused, params)

    samples = measure(args, vmapped, fused, params)
    rows, noise_floor = summarise(samples)

    step_us = min(samples["baseline"])
    hardware = hardware_label(jax)

    print(f"\n=== NaN accounting overhead ({hardware}) ===")
    print(f"model={args.model_type} n_starts={args.n_starts} ndim={ndim}")

    # The measurement that actually resolves the variants.
    print(f"\nreal step cost: {step_us / 1e6:.3f} s/step")
    print(f"(python call overhead subtracted: {call_overhead_us:.2f} us)")
    print(f"\n{'variant':<10} {'accounting':>12} {'% of a step':>14}  source")
    for name in ("host", "eager", "fused"):
        us = accounting_us[name]
        source = "proxy shapes" if name == "fused" else "real gradient"
        print(f"{name:<10} {us:>10.2f}us {100.0 * us / step_us:>13.5f}%  {source}")

    # The end-to-end loop, kept as a sanity check only -- see
    # measure_accounting_only for why it cannot resolve these differences.
    print(f"\nend-to-end loop (resolution ~{abs(noise_floor):.2f}%, sanity check only):")
    for row in rows:
        print(
            f"{row['variant']:<10} {row['us_per_step']:>12.1f}us {row['overhead_percent']:>+8.2f}%"
        )

    fused_pct = 100.0 * accounting_us["fused"] / step_us
    resolution_us = abs(noise_floor) / 100.0 * step_us
    # Ratio only means anything against a positive effect; a non-positive
    # difference means the effect sits below what that method can resolve.
    largest_us = max(accounting_us.values())
    if largest_us > 0:
        ratio = f"{resolution_us / largest_us:,.0f}x larger than the largest effect"
    else:
        ratio = "larger than every effect measured"
    print(
        f"\nend-to-end resolution: {resolution_us:,.0f}us -- {ratio}, "
        f"so that loop BOUNDS the overhead rather than measuring it"
    )

    verdict = (
        f"fused accounting costs {accounting_us['fused']:.1f}us on a "
        f"{step_us / 1e6:.3f}s step = {fused_pct:.5f}% of run time"
    )
    print(f"\nshipped variant (fused): {verdict}")

    out_dir = _WORKSPACE_ROOT / "results" / "searches" / "multi_start_nan_accounting"
    out_dir.mkdir(parents=True, exist_ok=True)

    record = {
        "hardware": hardware,
        "jax_version": jax.__version__,
        "platform": platform.platform(),
        "dataset_class": args.dataset_class,
        "model_type": args.model_type,
        "instrument": args.instrument,
        "n_starts": args.n_starts,
        "ndim": ndim,
        "n_steps": args.n_steps,
        "reps": args.reps,
        "mixed_precision": args.mixed_precision,
        "tag": args.tag,
        "rows": rows,
        "noise_floor_percent": noise_floor,
        "step_us": step_us,
        "accounting_us": accounting_us,
        "accounting_percent_of_step": {k: 100.0 * v / step_us for k, v in accounting_us.items()},
        "python_call_overhead_us": call_overhead_us,
        "verdict": verdict,
    }

    out_path = out_dir / f"{hardware}.json"
    existing = json.loads(out_path.read_text()) if out_path.exists() else []
    existing.append(record)
    out_path.write_text(json.dumps(existing, indent=2) + "\n")

    png_path = out_dir / f"{hardware}.png"
    plot(
        rows,
        noise_floor,
        png_path,
        f"NaN accounting overhead -- {args.model_type} on {hardware}",
    )

    print(f"wrote {out_path}")
    print(f"wrote {png_path}")


if __name__ == "__main__":
    main()
