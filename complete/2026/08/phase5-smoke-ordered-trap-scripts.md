- completed: 2026-08-24
- issue: https://github.com/PyAutoLabs/autocti_workspace/issues/27
- prs:
  - https://github.com/PyAutoLabs/autocti_workspace/pull/28 (merged)
- summary: |
    CTI resurrection epic **Phase 5**. Smoke coverage for the ordered-trap
    `modeling/start_here.py`-class scripts, unblocked by PyAutoFit#1520
    (`438f56fac`). All nine verified running bypassed; a curated three promoted.
    This is autocti_workspace's FIRST CI.

## The prompt's premise did not hold

The prompt said to "add them back to the workspace `smoke_tests.txt`". **There is
no `smoke_tests.txt`, and never was.** autocti_workspace has no `.github/`
directory and no `config/build/`; `git ls-files` finds neither, and
`git log --diff-filter=D` shows nothing was ever deleted. So the coverage had to
be *created*, not re-enabled — which is why the task was larger than its
"add lines to a file" sizing suggested.

That also surfaced pre-existing drift worth knowing about:
`PyAutoHeart/config/repos.yaml` lists autocti_workspace under `workspaces`,
whose required checks are `["Smoke Tests", "Navigator Check"]`. Neither workflow
existed, so that gate had been vacuous. This PR closes the smoke half.
(Heart's *local* smoke runner table — the `smoke:` block in the same file — has
no autocti entry either, and its `import_names` map has no PyAutoCTI. Untouched
here; a genuine follow-up.)

## Verification — all nine run bypassed

Stack built from source `main` with PyAutoFit at `438f56fac` (which is `main`
HEAD, so "a PyAutoFit main containing that SHA" is satisfied by definition),
autonerves/autoarray 2026.8.17.1, autocti 2024.11.13.2, arcticpy 2.6.

`output/` cleared between EVERY run. This matters: a bypassed fit calls
`paths.completed()`, so re-running with the same `unique_tag` replays the old
result via `result_via_completed_fit` and looks exactly like "the fix didn't
work".

| script | time | promoted |
|---|---|---|
| `dataset_1d/modeling/start_here.py` | 13 s | yes |
| `dataset_1d/modeling/customize/priors.py` | 12 s | no |
| `dataset_1d/modeling/features/species_x3.py` | 18 s | yes |
| `dataset_1d/modeling/features/visualize_full.py` | 20 s | no |
| `imaging_ci/modeling/start_here.py` | 96 s | yes |
| `imaging_ci/modeling/features/cosmic_rays.py` | 120 s | no |
| `imaging_ci/modeling/features/non_uniform.py` | 53 s | no |
| `imaging_ci/modeling/features/serial_cti.py` | 94 s | no |
| `imaging_ci/modeling/features/visualize_full.py` | 96 s | no |

All nine **pass**. The fix is directly visible in the output:
`dataset_1d/modeling/start_here.py` builds two `TrapInstantCapture` models with
identical priors under `trap_0.release_timescale < trap_1.release_timescale`,
and resolves them to `0.14` and `1.68` — distinct and correctly ordered — rather
than tying at the prior medians and hard-failing the bypass.

## Why three, not nine

Every CTI repo's AGENTS.md says to keep the smoke list a small curated subset
and not to mass-promote. Measured the existing CTI smoke suite
(autocti_workspace_test) for a like-for-like baseline: **20 s** total
(8 + 5 + 7). All nine here cost **~522 s** — a ~26x jump on the CTI smoke bill.

Promoted three, covering both dataset geometries and the multi-species
ordered-trap case — the surface the bypass fix actually unblocked. **132 s
measured cold**, with `dataset/` wiped to its committed state so every dataset
is simulated first (datasets are gitignored and auto-simulated by the scripts'
`should_simulate` guards, so a fresh CI checkout always pays that).

CI confirmed the estimate: the runner step took **129 s** on Python 3.12 and
~123 s on 3.13. Both legs green.

## What was added

- `.github/workflows/smoke_tests.yml` — thin caller for Heart's reusable smoke
  workflow, chain `PyAutoNerves PyAutoFit PyAutoArray PyAutoCTI`, `arcticpy: true`.
- `.github/scripts/smoke_install.sh` — install epilogue carrying **no** arcticpy
  recipe; the same-day arcticpy-install-standardisation task made Heart's
  `install-arcticpy` action its single owner, and Heart runs it before this
  epilogue. This repo never had a copy to delete.
- `.github/scripts/run_smoke.py` — thin shim over PyAutoHands' `run_python.py`,
  mirroring autocti_workspace_test's. Holds no logic, so it needs none of the
  sweeps the old 198-line copies did.
- `config/build/profile_smoke.yaml` — `PYAUTO_TEST_MODE=2` and cache dirs.
  Passed Heart's strict env-profile validator first time.
- `smoke_tests.txt` — the curated three.
- `AGENTS.md` — a "Smoke tests (CI)" section carrying the full nine-script
  timing table, so the next person promoting a script starts from numbers.

## Left undone, deliberately

**Navigator Check.** Heart lists it as a required check for this repo alongside
Smoke Tests and it is still absent. Out of scope for an ordered-trap smoke task;
adding a second unrelated workflow would have widened the PR. Worth a follow-up
prompt.

## Still open for a human

autocti_workspace_test's `## Conventions` says integration scripts are
"single-trap" with no stated reason. The reason was almost certainly the bypass
crash, which is now fixed — so either drop it and exercise multi-trap ordered
models (better coverage, since ordered traps are the realistic CTI case), or
write the real reason in. Deliberately not decided here.

## Original prompt

# Re-enable autocti_workspace smoke coverage of the ordered-trap modeling scripts

Type: test
Target: autocti_workspace
Repos:
- @autocti_workspace
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised
Filed: 2026-08-24
Issued: 2026-08-24
Epic: CTI resurrection — Phase 5

Re-homed from `draft/test/autofit/` by the filing session. Intake set
`Target: PyAutoFit` and listed PyAutoFit as an affected repo — wrong on both:
the PyAutoFit fix has already merged (438f56fac), so this task changes no
library source and only needs a PyAutoFit main that contains it. Difficulty
lowered from `large`: the work is verify-scripts-run, add lines to
`smoke_tests.txt`, and time them against the gate cap — sized by script count,
which is not yet known, hence `medium` rather than `small`.

Re-enable @autocti_workspace smoke coverage of the modeling/start_here.py-class scripts, unblocked by PyAutoFit#1520 (merged 438f56fac). Those scripts were un-smokeable at PYAUTO_TEST_MODE=2 because ordered trap models tie at the prior medians and the bypass hard-failed; the bypass now selects a deterministic assertion-valid point, at TEST_MODE 2 and 3. This is CTI resurrection epic Phase 5. Work: confirm the scripts now run bypassed against a PyAutoFit main that includes 438f56fac, add them back to the workspace smoke_tests.txt, and check timings against the smoke gate cap before adding them.

<!-- formalised by the Intake (Conception) Agent on 2026-08-24 from user-intake -->
