# Intermittent XLA compile stall in JAX vmap likelihood scripts — third repo, still unfixed

Type: bug
Target: ci
Repos:
- @autogalaxy_workspace_test
- @autolens_workspace_test
- @PyAutoFit
Difficulty: medium
Autonomy: supervised
Priority: high
Status: formalised
Filed: 2026-08-23

Surfaced 2026-08-23 by the per-script timeout backport
([`backport_per_script_timeout.md`](../../maintenance/ci/backport_per_script_timeout.md)),
which put a 300s cap on `autogalaxy_workspace_test`'s previously uncapped smoke
gate. The cap fired on its very first run — not on the change under test, but on
a latent hang the uncapped runner had been absorbing.

## What was observed

`autogalaxy_workspace_test#109`, `smoke (3.13)`, 36/37 passed:

```
TIMEOUT (300s)  imaging/jax_likelihood/mge_group.py
```

The captured tail — preserved precisely because the cap keeps the killed child's
output — names the stall:

```
18:47:53  autoarray...dataset - INFO - IMAGING - Data masked, 1264 image-pixels
18:47:55  jax._src.xla_bridge - INFO - Unable to initialize backend 'tpu' ...
18:47:55  autofit.non_linear.jax_compile - INFO - JAX jit compiling vectorized
          (vmap) likelihood function, could take seconds or minutes...
          [silence for the full 300s]
```

It never emitted another line. This is a stall inside JAX vmap/JIT compilation,
not a slow script:

- its sibling `imaging/jax_likelihood/mge.py` passes in **9.4s**, reporting
  `JAX Time To VMAP + JIT Function: 2.50s`;
- `multi_dataset/jax_likelihood/mge_group.py` — same basename, same tier —
  passes in **28.8s** in the same run;
- the script passes on `main`.

So the same code path completes in seconds normally and occasionally never
completes at all.

## Why this is worth a task rather than a marker

This is the **third** repo/script to hit the same signature, and the pattern in
the `no_run.yaml` files is that each occurrence gets quarantined and the
underlying stall is never diagnosed:

| Entry | Marker | Note |
|---|---|---|
| `multi_dataset/jax_likelihood/rectangular.py` (autogalaxy_workspace_test) | NEEDS_FIX 2026-08-01 | "hung to the 1800s release cap … passes ~19s otherwise; intermittent XLA compile stall, same family as autolens_workspace_test delaunay" |
| autolens_workspace_test delaunay | — | `autolens_workspace_test#245` |
| `imaging/jax_likelihood/mge_group.py` (autogalaxy_workspace_test) | NEEDS_FIX 2026-08-23 | this one |

Plus six `interferometer/jax_likelihood/*` and two `jax_grad/*` entries
SLOW-skipped on 2026-07-14 for "flaking at the 1800s cap" (PyAutoHeart#74) —
which, given this evidence, may not be slowness at all but the same stall
wearing a different label. **That distinction matters**: a SLOW marker says
"make it faster", a stall says "it never finishes", and the Profiling Agent has
been handed a set of scripts under the first description when some may belong to
the second.

The cost was invisible until now because nothing was capped.
`autogalaxy_workspace_test` has **four** runs cancelled at the 6-hour Actions
ceiling (runs 30088422799, 30051301212, 30289779988, 31319423047) — roughly 24
hours of runner time, with no diagnostic output, because the uncapped runner sat
on a held stdout pipe. Those runs are now impossible: the cap turns a 6-hour
silent hang into a 300s TIMEOUT with the compiling-step tail attached. That is
what made this diagnosable at all.

## Task

1. Establish whether the SLOW-marked `jax_likelihood`/`jax_grad` entries are
   genuinely slow or are this stall mislabelled. Re-time them against the real
   caps; a slow script has a tight timing distribution, a stalling one is
   bimodal.
2. Reproduce the stall deliberately — loop `imaging/jax_likelihood/mge_group.py`
   until it hangs, then attach `py-spy dump` / `faulthandler` to see where inside
   the XLA compile it is parked.
3. Determine whether the trigger is a JAX/XLA version interaction (this repo has
   prior form: `delaunay_mge.py` is disabled outright because `jax 0.7` removed
   `jax.interpreters.xla.pytype_aval_mappings`, and the smoke installer once
   clobbered a working `tfp-nightly`), a `vmap` shape/donation issue, or
   contention on the runner.
4. Fix, then remove the NEEDS_FIX markers — including the 2026-08-01 one, which
   this task inherits.

## Acceptance

- A stated root cause for the stall, not another quarantine.
- Every entry currently marked NEEDS_FIX for this signature is either restored to
  its suite or re-marked with the real reason.
- The SLOW-vs-stall question in step 1 answered in writing, so the Profiling
  Agent is not chasing speedups on scripts that are hanging.
