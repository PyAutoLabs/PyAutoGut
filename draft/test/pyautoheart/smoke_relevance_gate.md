# Relevance-gate the reusable smoke workflow so a PR only runs what its diff can affect

Type: test
Target: PyAutoHeart
Repos:
- PyAutoHeart
- autolens_workspace_test
- autolens_workspace
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised

`PyAutoHeart/.github/workflows/smoke-tests.yml` — the reusable workflow every
workspace's `smoke_tests.yml` is a thin caller of — has exactly one skip
condition: a docs-only gate that skips the matrix when every changed file
matches `*.md`, `docs/`, `LICENSE` or `runtime.txt`. Anything else runs the
full curated smoke list, whatever it touched.

This prompt cuts how *often* the gate runs. Making the slow entries cheaper is
the sibling prompt `draft/test/workspaces/slowest_smoke_gate_scripts.md`; they
compound but are separate changes in separate repos.

## Why

- `autolens_workspace_test` smoke costs ~11m20s and fires on every PR event
  plus every push to `main`. Run numbers put it at roughly 17 runs/week
  (#555 on 2026-07-28 → #616 on 2026-08-22; approximate, since superseded PR
  runs are cancelled).
- `autolens_workspace` costs ~8m40s over 37 entries, 5.8 runs/day in the week
  to 2026-08-23.
- The failure mode is already recorded in the repo. `smoke_tests.txt`, on the
  2026-08-22 disable of `multi_dataset/jax_likelihood/mge.py`: *"Hit 4/4 jobs
  (3.12 and 3.13, twice each) on autolens_workspace_test#261, whose diff
  touches no script this gate runs."*
- The two extremes already exist and are 80x apart: a docs-only PR finishes in
  **8 seconds** (autolens_workspace_test run #605, autogalaxy_workspace #545);
  a one-character change to any non-markdown file costs the full run.

## Task

Two tiers, shippable independently. Tier 1 alone is most of the win.

1. **Skip when no script can be affected.** Extend the existing `changes` job's
   classification: if the diff touches nothing under `scripts/`, `config/`,
   `smoke_tests.txt`, `smoke_notebooks.txt` or `.github/`, skip the matrix the
   same way the docs-only path does. Same fail-closed shape, same
   `docs_only`-style output, one more reason to skip.
2. **Narrow the entry list to the packages the diff touches, plus a fixed
   core.** The smoke entries cluster cleanly by top-level package, so a
   directory-level mapping is enough — no dependency analysis needed:

   | package | autolens_workspace_test | autolens_workspace |
   |---|---:|---:|
   | `imaging/` | 232.8s (42%) | 63.6s (18%) |
   | `misc/` | 154.6s (28%) | — |
   | `interferometer/` | 92.1s (17%) | 54.6s (16%) |
   | `point_source/` | 47.7s (9%) | 15.7s (4%) |
   | `multi_galaxy/` | 25.8s (5%) | 166.4s (47%) |
   | `group/` | — | 22.9s (7%) |
   | `guides/` | — | 14.3s (4%) |
   | `multi_dataset/` | — | 13.5s (4%) |

   A PR touching only `scripts/misc/` would run 155s instead of 553s; one
   touching only `multi_galaxy/` in `_test` would run 26s. Tier 2 needs the
   selected set passed down to `run_smoke.py` as an input, so it also touches
   each workspace's vendored runner — scope it deliberately or defer it.

## Hard constraints

- **Do not implement this with `on.pull_request.paths`.** A job skipped by a
  path filter never reports a conclusion, so a required status check sits
  pending forever and blocks the merge. The in-workflow `changes` job emits a
  real `skipped`, which satisfies required-check semantics — the workflow's own
  comment already says so. Keep the skip inside the workflow.
- **Fail closed**, matching the docs-only gate exactly: no base SHA, unfetchable
  base, empty diff, or a single unclassifiable path ⇒ run everything. Only an
  explicit every-file-matches verdict may skip. Keep the two-dot diff against
  the base *tip* so upstream drift shows up as extra files.
- **Do not touch the push-to-`main` run.** `PyAutoHeart/config/repos.yaml` lists
  `workspaces_test: ["Smoke Tests"]` and `workspaces: ["Smoke Tests",
  "Navigator Check"]` under `required_workflows`; `ci_status` reads their
  conclusion on the `main` HEAD commit and `readiness` gates RED on failure.
  `cancelled` is in Heart's `FAILURE_CONCLUSIONS`, which is why the callers'
  concurrency block only cancels non-`main` refs. Narrowing PR-side runs is
  free — Heart never reads them — but a skipped or cancelled `main` run breaks
  the readiness gate. If tier 1 would skip on a `main` push, gate it to
  `pull_request` events only.
- The change is Heart-owned and lands once for every caller (both `_workspace`
  and `_workspace_test` families, plus the HowTo repos). Verify against at
  least one caller of each shape before merging.

## Acceptance

- A PR touching only `scripts/misc/` in `autolens_workspace_test` runs
  materially less than the full 553s (tier 2), or a PR touching only
  `README.md` + a config sidecar still skips (tier 1).
- A PR with an unresolvable base still runs the full matrix.
- The `Smoke Tests` check reports `skipped`, not pending, on every skip path.
- `main`-push runs are unchanged and Heart's `ci_status` still reads a real
  conclusion.

<!-- formalised by the Intake (Conception) Agent on 2026-08-23 from user-intake -->
