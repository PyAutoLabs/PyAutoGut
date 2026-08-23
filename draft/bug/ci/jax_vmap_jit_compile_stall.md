# Intermittent XLA compile stall in JAX vmap likelihood scripts — third repo, still unfixed

Type: bug
Target: ci
Repos:
- @autogalaxy_workspace_test
- @autolens_workspace_test
- @PyAutoFit
Difficulty: too-large
Autonomy: supervised
Priority: high
Status: campaign map — phases route through /start_dev one at a time; this
Epic: jax-compile-stall
        file is never issued itself and nothing here is bulk-issued
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

## It is not one script — the second leg named a second one

The two matrix legs of the **same commit** disagreed, and the slower leg found
more:

| Leg | Result | Timed out |
|---|---|---|
| `smoke (3.13)` | 36/37 | `imaging/jax_likelihood/mge_group.py` |
| `smoke (3.12)` | **35/37** | `imaging/jax_likelihood/mge_group.py` **and `imaging/jax_likelihood/rectangular_mge.py`** |

`rectangular_mge.py` **passed on 3.13 and stalled on 3.12, on the same commit**.
So the stall is not a property of one script, and not deterministic per Python
version either — it is a per-compile probability that two runs of the same code
sample differently.

The affected set has a shape. Of `imaging/jax_likelihood/`:

| Script | State |
|---|---|
| `mge.py` | passes, 9.4s (2.5s vmap+JIT) |
| `mge_group.py` | stalled on both legs |
| `rectangular_mge.py` | stalled on 3.12, passed on 3.13 |
| `delaunay_mge.py` | already disabled (jax 0.7 removed `jax.interpreters.xla.pytype_aval_mappings`) |

The plain `mge` is fine; the **composite** MGE variants — group, rectangular-MGE,
delaunay-MGE — are the ones that stall or are already out. That points at compile
graph size/complexity in the vmap trace, not at any one script's logic, and it
predicts which other entries are at risk.

**This is why quarantining is the wrong end state.** Parking scripts as they
stall is whack-a-mole against a probability: each park removes coverage of
exactly the heaviest JAX paths, which are the ones most worth testing.

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

## CLOSED AS PARTIAL — 2026-08-23

Phase 1 shipped. Phases 2 and 3 were taken to a deliberate stopping point and the
epic closed: the stall is **instrumented and characterised but not root-caused**,
and nothing was un-quarantined. The full account, including the two live leads and
every trap, is the record
[`complete/2026/08/jax-compile-stall-slow-vs-stall-audit.md`](../../../complete/2026/08/jax-compile-stall-slow-vs-stall-audit.md).
Resume through [`../../research/ci/smoke_timing_and_profiling.md`](../../research/ci/smoke_timing_and_profiling.md).

## Phase map (added 2026-08-23 at /start_dev)

The Bug Agent sizes this `too-large` and returns `split-into-phases`. It is one
root cause but three separable deliverables, and phases 2 and 3 are both blocked
on evidence that does not exist today. Each phase is its own prompt, issued one
at a time — nothing here is bulk-issued.

| Phase | Prompt | Deliverable | Repos |
|---|---|---|---|
| 1 | ~~`jax_compile_stall_1_evidence.md`~~ **SHIPPED 2026-08-23** — record [`complete/2026/08/jax-compile-stall-evidence.md`](../../../complete/2026/08/jax-compile-stall-evidence.md) (PyAutoFit#1516, PR#1517 merged) | A stalled compile reports itself: heartbeat, `faulthandler` dump, compile-vs-execute split | PyAutoFit |
| 2 | [`jax_compile_stall_2_slow_vs_stall_audit.md`](jax_compile_stall_2_slow_vs_stall_audit.md) | The SLOW-vs-stall question (task step 1) answered in writing; every marker carries its real reason | autogalaxy_workspace_test, autolens_workspace_test |
| 3 | [`jax_compile_stall_3_root_cause.md`](jax_compile_stall_3_root_cause.md) | Root cause + fix; every NEEDS_FIX for this signature cleared (task steps 2–4) | PyAutoFit, both `_workspace_test` |

Acceptance for the campaign as a whole is the § Acceptance section above; each
phase carries only its own slice of it.

## Supersedes an earlier filing of the same defect

[`../autolens_workspace_test/multi_dataset_jax_likelihood_xla_stall.md`](../autolens_workspace_test/multi_dataset_jax_likelihood_xla_stall.md)
(filed 2026-08-22, never issued) describes this same stall from the
`autolens_workspace_test` side. It is superseded by this campaign rather than
run alongside it — one root cause is one task. Its two asks that this filing did
not already carry are folded in: the runner leaving diagnostic evidence behind
(phase 1) and re-enabling `multi_dataset/jax_likelihood/mge.py` +
`shared_preloads.py` in `smoke_tests.txt` (phase 3).

## Two source-level findings from the /start_dev read of PyAutoFit

Recorded here because they are the leads phase 3 starts from, and neither was
known when this prompt was filed.

**1. The stalling wrapper is `vmap` *of* `jit`, the inverted ordering.**
`Fitness._vmap` (`autofit/non_linear/fitness.py`) builds
`jax.vmap(jax.jit(self.call))`, while `latent.py`'s batched latent computation
builds `jax.jit(jax.vmap(compute_latent_for_model))` — the conventional order.
The path that stalls is exactly the `vmap` path; the `_jit`-only scripts in the
same directories do not stall. Whether the ordering is causal is unproven, but
it is a one-line A/B and it is the first thing phase 3 should try.

**2. The silence spans two different waits, and nothing distinguishes them.**
`log_on_first_compile` (`autofit/non_linear/jax_compile.py`) logs
`JAX jit compiling {description}...`, calls the wrapped function, then calls
`jax.block_until_ready(result)` — trace/lower/compile and execution, with one
log line covering both and no heartbeat in between. That is why three
quarantines produced no diagnosis: the captured tail cannot say whether the
process is in XLA, in execution, or blocked on a lock. Phase 1 fixes exactly
this.

**Timeline worth testing in phase 3.** Both NEEDS_FIX stalls (2026-08-01,
2026-08-23) post-date the persistent-compilation-cache default (PyAutoConf#128,
merged 2026-07-17); the eight SLOW entries predate it. `complete/2026/07/jax-compile-time-research.md`
also records that XLA compiles on host CPUs and that compile timing is
load-sensitive by up to 7×. Cache-lock contention and runner CPU contention are
therefore both live hypotheses alongside the version-interaction one already in
§ Task step 3.
