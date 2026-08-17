=== body header ===
Filed 2026-07-20 08:41 by the `/wake_up` overnight-failure triage; **fixed the
same day**, ~4 hours later, by PyAutoHands#170 → #171 (both closed
2026-07-20T12:51Z). The draft was never retired, so it sat in `draft/` for four
weeks and kept re-surfacing on `dashboard.md` as open work.

## What actually shipped

PyAutoHands#171 took the prompt's **option 2**, minimally:

- `python_matrix.yml` smoke install: `-e ./PyAutoFit` → `-e "./PyAutoFit[optional]"`,
  matching the `[optional]` already given to Array and Lens.
- Smoke matrix narrowed `3.9–3.13` → `3.11–3.13`, because `autonerves[jax]` is
  gated to Python ≥3.11 and the demo cannot run below it.
- Unit-test job deliberately left on plain `./PyAutoFit` — no JAX in unit tests.

Option 1 (dropping `searches/mle.py` from the smoke set) was **not** taken:
the script is still line 4 of `autofit_workspace/smoke_tests.txt`, and it runs.

## Verification 2026-08-17

Latest scheduled `python_matrix` (run 31992457345, 2026-08-17): **success**.
Every `autofit_workspace` leg — 3.12, 3.13 and 3.14 — reports **8/8 PASS**
including `PASS: searches/mle.py`, with the executed-script count matching all
8 entries in `smoke_tests.txt`, so nothing was silently skipped. `optax-0.2.8`
appears in the install manifest.

The one intervening red (run 31356134172, 2026-08-10) was **autolens_workspace**
on 3.13/3.14 — a different failure, not this one; `autofit_workspace` was green
in that run too.

## Dependency chain worth knowing

`optax` reaches the smoke env transitively, not directly:
`PyAutoFit[optional]` → `blackjax>=1.2.0` → `optax>=0.2.3`. The direct
declaration lives in a *different* extra — `autofit[jax] = ["autonerves[jax]",
"optax>=0.2.5"]` — which the smoke job does not install. So the guarantee is
real but indirect: pruning `blackjax` from `[optional]` would reintroduce this
exact `ModuleNotFoundError`, and extras do get pruned here (cf. `dbed2df89
refactor: remove the NSS nested sampler and its [nss] extra`). Not filed as
work — flagged so a future extras change is read with this coupling in mind.

## Lifecycle note

No `complete/` record existed because the fix shipped in **PyAutoHands**, via
its own issues, and never passed through the Mind draft→active→complete
lifecycle. This record exists to retire the ghost, not to claim new work.

## Original prompt

# python_matrix smoke fails: autofit_workspace searches/mle.py needs optax not in smoke env

Type: bug
Target: autofit_workspace
Repos:
- autofit_workspace
Difficulty: small
Autonomy: safe
Priority: normal
Status: formalised

The nightly `python_matrix` (PyAutoHands) smoke matrix fails on `autofit_workspace`
across **every** Python version (3.9–3.13), while `autolens_workspace` and
`autogalaxy_workspace` pass. Deterministic, single failing script.

## Evidence

Run 29721343824 → `1 smoke test(s) failed`, `FAIL: searches/mle.py`:

```
File ".../PyAutoFit/autofit/non_linear/search/mle/multi_start_gradient/search.py", line 129, in _fit
ModuleNotFoundError: No module named 'optax'
...
ImportError: MultiStartAdam requires the optional `jax` and `optax` dependencies.
Install them with `pip install autofit[jax] optax`.
```

`searches/mle.py` demonstrates `MultiStartAdam`, a JAX/optax gradient search. The
smoke matrix installs the release wheels **without** the `[jax]`/`optax` extras,
so the script raises a (correct, helpful) ImportError at runtime and the smoke
job fails.

## Fix locus — decide (do NOT degrade the user-facing script)

`MultiStartAdam`'s ImportError is correct behaviour — do not add a silent guard
or mask it. Two clean options:
1. **Exclude `searches/mle.py` from the numpy-only smoke set** — it's a JAX/optax
   demo, in the same class as other JAX-requiring scripts already kept out of the
   curated smoke subset (see the smoke-tests-are-a-small-curated-subset and
   no-JAX-in-unit-tests conventions). Preferred if the smoke matrix is meant to
   stay dependency-light.
2. **Install the extras for the autofit_workspace smoke job** — add
   `autofit[jax] optax` (or `autonerves[jax]`) to that matrix leg's install step
   in PyAutoHands `python_matrix.yml` so the demo runs as intended.

Confirm which smoke-tier `searches/mle.py` belongs to, then apply the matching
fix. Check whether other new JAX/optax search demos (`searches_minimal/*` in the
developer workspace are already excluded) have the same exposure.

## Validation

Re-run the `python_matrix` `autofit_workspace` leg (or the workspace's smoke
runner) and confirm `searches/mle.py` no longer fails the job.

<!-- filed from /wake_up overnight-failure triage on 2026-07-20 -->
