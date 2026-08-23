# Backport `run_smoke.py`'s per-script timeout to the three workspace_test siblings

Type: test
Target: workspaces
Repos:
- @autogalaxy_workspace_test
- @autocti_workspace_test
- @autofit_workspace_test
Difficulty: low
Autonomy: supervised
Priority: high
Status: formalised
Filed: 2026-08-23
Issued: 2026-08-23

Split out of `draft/research/workspaces/intermittent_smoke_hang_jax_mge.md` (the
root-cause investigation) because this guardrail is bounded, already designed, and
valuable **whether or not** the underlying hang is ever diagnosed.

## This is drift, not a new feature

`autolens_workspace_test/.github/scripts/run_smoke.py` **already implements** a
per-script timeout (PyAutoHands#226/#227): `subprocess.Popen(..., start_new_session=True)`,
`communicate(timeout=timeout_for(env))`, a `_kill_group()` SIGKILL of the whole
process group on `TimeoutExpired`, return code 124, and a `TIMEOUT (Ns)` status in
the summary.

The other three workspace_test repos never received it. They still run a bare
`subprocess.run(...)` with no cap:

| Repo | `run_smoke.py` | Timeout |
|------|----------------|---------|
| autolens_workspace_test | 193 lines | **yes** — reference implementation |
| autogalaxy_workspace_test | 113 lines | no |
| autocti_workspace_test | 113 lines | no |
| autofit_workspace_test | 113 lines | no |

The three un-capped copies are **identical in code** — they differ only in the
wording of one docstring paragraph. So this is a single diff applied three times,
not three separate ports.

## What the gap costs

Observed 2026-08-23 on autogalaxy_workspace_test run 32652329340 attempt 1:

```
16:41:58  ##[group]imaging/jax_likelihood/mge.py
          <<< 59 minutes, zero output >>>
17:40:36  ##[error]The operation was canceled.
17:40:36  Terminate orphan process: pid (2860) (python)
```

The asymmetry is the whole argument: **autolens would have capped that script and
carried on**; autogalaxy had nothing to stop it. Four earlier autogalaxy runs (268,
255, 239, 242) each ran ~6h to GitHub's ceiling against an 11-14 min norm.

A hang is strictly worse than a failure. It burns up to 6 runner-hours; `cancelled`
is in Heart's `FAILURE_CONCLUSIONS`, so a hung run on `main` reads as red CI to the
`ws_ci` gate with no failing test to point at; and it yields no traceback, so the
only response has been to park the script and lose real coverage. It also blocked
the ship workflow directly — autogalaxy_workspace_test#107 was merged with its smoke
run still in flight because there was no bounded signal to wait for.

## Suggested scope

1. Port the timeout machinery from `autolens_workspace_test`'s `run_smoke.py` to the
   three siblings: the `timeout_for` import (with its `ImportError` fallback), the
   `Popen`/`communicate(timeout=...)` structure, `_kill_group()`, the 124 return
   code, and the `TIMEOUT (Ns)` summary status. Take it verbatim where possible —
   the design questions (why kill the group not the child, why 124 and not the
   signal, why the cap is resolved parent-side) are already answered in that file's
   comments and should not be re-litigated.
2. Preserve each repo's existing docstring wording where the copies legitimately
   differ; the port is a code change, not a prose sync.
3. Confirm `timeout_for` resolves in each repo's CI — it comes from PyAutoHands's
   `autohands/build_util.py`, and the fallback silently degrades to the whole-run
   cap if the import fails, which would make the backport look applied while doing
   less than intended. Assert it rather than assume it, in the spirit of the guard
   this task exists to add.
4. Sanity-check each repo's resolved cap against its own slowest scripts before
   merging, so the backport does not start failing legitimately-slow scripts.

## Not in scope

Root-causing the hang itself, and unparking
`multi_dataset/jax_likelihood/rectangular.py` — both belong to the research prompt
named above. This task deliberately treats the hang as a black box.

<!-- Sizing: declared low. The feature agent derived large (score 8) and suggested
     phasing, on an earlier draft that described this as designing a timeout from
     scratch across two repos. That reading is superseded: there is a production
     reference implementation and the three targets are code-identical, so the work
     is a mechanical port. The prompt is long because the evidence is. -->
