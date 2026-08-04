Expanded HowTo smoke from a hand-maintained allowlist to opt-out coverage, after
shipping #57 revealed a public teaching notebook broken in three places that no
CI job had ever executed.

## Outcome

| Repo | PR | Merged |
|---|---|---|
| PyAutoHands | [#225](https://github.com/PyAutoLabs/PyAutoHands/pull/225) | 2026-08-04 |
| HowToGalaxy | [#59](https://github.com/PyAutoLabs/HowToGalaxy/pull/59) mesh fix | 2026-08-04 |
| HowToGalaxy | [#60](https://github.com/PyAutoLabs/HowToGalaxy/pull/60) | 15:30:40Z |
| HowToFit | [#43](https://github.com/PyAutoLabs/HowToFit/pull/43) | 15:28:27Z |
| HowToLens | [#66](https://github.com/PyAutoLabs/HowToLens/pull/66) | 15:48:50Z |

Coverage, verified from CI job logs (not a green tick — green already passed
while testing 4 of 26 files):

| repo | before | after |
|------|--------|-------|
| HowToGalaxy | 4 | **26** pass, 0 fail |
| HowToLens | 6 | **39** pass, 0 fail (both 3.12 and 3.13) |
| HowToFit | 10 | **15** pass, 0 fail |

## Why the allowlist was the bug

A script was tested only if someone remembered to add it, so every new tutorial
was uncovered from birth. The only backstop is Heart's `workspace-smoke`, which
is **weekly** — and the run that caught #57 was a manual `workflow_dispatch`, not
the schedule. The allowlist also concealed a false claim in
`profile_smoke.yaml` ("the chapters run correctly at 16x16"), untrue for
chapter 4 and untested because chapter 4 was never listed.

## The blocker that nearly made this worthless

`build_util.execute_script()` contained `if "inversion" in f:` — a match on the
**script path**, not the exception — that rewrote any failure to `PASSED`
("Inversion script failure (ignored)"). Proven on a file containing only
`raise SystemExit`: `main` recorded `PASSED / has_failures=False`; with the
escape removed, `FAILED / True`.

Three scripts workspace-wide matched, two being the HowToGalaxy and HowToLens
`chapter_4_pixelizations/tutorial_3_inversions.py` — so the escape covered
**exactly** the tutorial from #56/#57. `execute_notebooks_in_folder` never had
the clause, which is why the notebook job reported that failure and a script run
never would have. Delegating smoke to the canonical runner without removing this
would have certified the one broken file as green.

## Design

`run_smoke.py` in all three repos is now a thin shim over
`PyAutoHands/autohands/run_python.py` — the entry point Heart's
workspace-validation already uses for `run_scripts` — so the PR gate and the
validation runner share one code path and one exclusion list
(`config/build/no_run.yaml`, already honoured by the notebook runner).
`smoke_tests.txt` is deleted.

`--report-dir` is mandatory, not cosmetic: `run_python.py` only propagates
failures when a report was built, and without it the suite runs to completion and
**always exits 0**, while `execute_script` also switches to abort-on-first-failure.

## What the expansion immediately caught

On the 3.13 leg, `tutorial_7_adaptive_pixelization` and
`tutorial_10_brightness_adaption` failed with `ModuleNotFoundError: No module
named 'jax'`: `smoke_install.sh` installs the `[optional]` extras only on 3.12,
the 3.13 leg deliberately testing the lean path. Neither was in the old 6-script
allowlist. Fixed with the workspace's established optional-dependency idiom
(`find_spec` → `sys.exit(0)`), which `is_clean_skip_exit()` already recognises.
Verified both ways: jax blocked → exit 0 with a message; jax present → both run
fully (25.0s / 78.7s).

## Mistakes made and corrected

- **Three commits contained none of the work.** `git add -A <paths> smoke_tests.txt`
  named a path already `git rm`'d; a stale pathspec aborts the entire add, and
  because the deletion was already staged the commit still succeeded. The PRs
  deleted the allowlist while leaving the old runner, and CI failed with
  "no smoke_tests.txt". Local verification had been run against the working tree,
  so it was true but proved nothing about the artifact. Fixed by staging explicit
  paths and printing the staged list before every commit.
- **A CI monitor reported "no-checks" for all three PRs.** `gh pr checks` has no
  `--json` flag in this version; the command errored and empty output was parsed
  as absence. Re-checked bare and found real failures. Second instance this
  session of a missing signal reading as a clean one.
- **`skipguard=0` was unobservable, not absent.** `execute_script` uses
  `capture_output=True` and prints only `PASS (duration)`, so a passing script's
  stdout never reaches the log. The guard did fire; the evidence is the 2
  `No module named 'jax'` errors dropping to 0 at an unchanged count of 39.
- Earlier in the session an unrelated claim that the ch4 reconstruction "prints
  all zeros" was wrong — 96% non-zero and finite; it was numpy's truncated repr
  of zero-valued edge pixels.

## Also fixed

- HowToGalaxy `chapter_4 tutorial_3` sized its mesh from `dataset.shape_native`
  (10000 pixels full-res, 256 capped), so fixed `pix_indexes` ran off the end.
  Now `shape=(25, 25)`, matching HowToLens and this file's own line 176. 19x
  faster in smoke (8.2s vs 156.7s).
- `tutorial_searches` exclusion removed from HowToGalaxy and HowToLens — no
  stated reason, passes in both.
- HowToLens `tutorial_5_borders` reason corrected: recorded as "Cant get right
  masks", but on identical dataset files it fails **with** the cap and passes
  **without** it. Cap-induced, now tagged `NEEDS_FIX`.
- HowToGalaxy `AGENTS.md` corrected — it claimed `PYAUTO_SMALL_DATASETS` is
  "deliberately not used" while the profile sets it for every script.

## Left for a human decision

`execute_notebooks_in_folder` has `if "InversionException" in traceback` → PASS.
Same species as the escape removed here, but keyed on exception type rather than
filename, so it is defensible for genuinely data-dependent failures and removing
it could redden Heart. Deliberately untouched.

Follow-up worth doing: `run_smoke.py` is now identical in all three repos and
could be centralised into PyAutoHands so the next change lands once.
