- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/503
- completed: 2026-08-24
- workspace-pr: autolens_workspace#504 (merged b19750cad64d2b5a0d809c132086371dccde27bc -> main)
- what shipped: the "Loading From Output Folder" teaching section in `scripts/imaging/modeling.py` guarded on `files/tracer.json` and then, inside that branch, read `image/tracer.fits`. Split into two independent guards, one per file, so each read is gated on the file it actually reads. Same fix applied to `scripts/multi_galaxy/modeling.py`; both notebook mirrors regenerated.
- the actual bug: under TEST_MODE the reduced search writes `files/tracer.json` but NOT the visualisation output `image/tracer.fits`, so the guard passed and the read raised FileNotFoundError. Long-standing (present since cfd5334c, 2026-04-14), not a regression. Never blocked a release — the `release` job's `needs:` excludes `run_smoke_tests` — but left the smoke gate permanently red, so a genuine workspace regression would have looked identical to this known failure.
- guard shape is now canonical: guard-each-read-on-its-own-file, matching what `scripts/guides/results/start_here.py` already did. `draft/maintenance/workspaces/read_through_issues.md` asks for this section to be ADDED to the group/cluster/interferometer examples — this is the shape to propagate, or the same bug ships to those scripts.
- scope decision: `scripts/multi_galaxy/modeling.py` was NOT in the reported scope but carried the byte-identical block and is also on `smoke_tests.txt`. Fixing only `imaging/` would have left the smoke gate red anyway, so both went in one PR.
- trap for reproducing: the smoke profile's DEFAULT `PYAUTO_TEST_MODE=2` bypasses the sampler and writes no `tracer.json` at all, so the guard is never entered and the bug does NOT surface. `PYAUTO_TEST_MODE=1` (reduced search) is the mode that writes `tracer.json` but not `tracer.fits`. Anyone re-checking this under the plain smoke default will wrongly conclude it is already fixed.
- validation: reproduced-then-fixed under profile_smoke.yaml + PYAUTO_TEST_MODE=1 — both scripts exit 1 with the reported FileNotFoundError before, exit 0 after. CI green on the merged head 0c14d00 across 3 workflow runs / 7 jobs (Smoke Tests changes+3.12+3.13, Navigator Check x3, Script Size Guard); mergeable_state clean at merge.
- heart: NOT EVALUATED — `pyauto-heart` is unreachable from a web-github session, so leg 4 of the ship gate has no verdict. Stated on the PR and issue rather than assumed green.
- environment note: run entirely in a cloud web-github session — no worktree, no `activate.sh`. autolens needs Python >= 3.12 (the PyPI 2026.7.29.1.post1 sdist raises a RuntimeError below that as a deliberate floor guard) while the session default was 3.11; a uv venv on /usr/bin/python3.12 was needed. `.github/scripts/run_smoke.py` could not be used (needs a sibling PyAutoHands checkout on PYTHONPATH), so profile_smoke.yaml's env was applied by hand. Notebook regeneration DID work by cloning PyAutoHands read-only and running `autohands/generate.py autolens` with the venv's bin on PATH — it rewrote only the two changed notebooks, no catalogue or unrelated drift.
- gotcha for future cloud sessions: an `add_repo` clone arrives with `remote.origin.fetch = +refs/heads/main:refs/remotes/origin/main`, so `git push -u` sets the branch remote but can never create the `origin/<branch>` tracking ref — the stop-hook git check then reports pushed commits as unpushed. Fix is `git config remote.origin.fetch '+refs/heads/*:refs/remotes/origin/*'` then fetch.
- follow-up not done (deliberately out of scope): the hard-coded `pixel_scales=0.1` / `0.05` in these blocks are the same literal pattern autolens_workspace#502 replaced with `dataset.pixel_scales` elsewhere.
- autonomy: `--auto` launch, effective level supervised (prompt header safe, bug work-type cap supervised). Parked at ship sign-off per the contract; human typed /prm, which authorized PR-open, merge and the full close-out.

## Original prompt

# Bug: fix the tracer.fits existence guard in autolens_workspace imaging modeling.py

Type: bug
Target: workspaces
Repos:
- autolens_workspace
Difficulty: small
Autonomy: safe
Priority: normal
Status: formalised
Filed: 2026-08-22 (backfilled from git)
Issued: 2026-08-24

Bug: fix the tracer.fits existence guard in autolens_workspace imaging modeling.py. The script crashes with FileNotFoundError because the guard checks the wrong file. It tests whether files/tracer.json exists, then reads image/tracer.fits, which TEST_MODE never writes. This fails the release smoke gate.


## Evidence (2026-08-23, gathered during the 2026.8.23.1 release)

`autolens_workspace/scripts/imaging/modeling.py:641`. The guard and the read
name **different files**:

```python
if (result_path / "files" / "tracer.json").exists():
    tracer = from_json(file_path=result_path / "files" / "tracer.json")

    tracer_fits = al.Array2D.from_fits(
        file_path=result_path / "image" / "tracer.fits", hdu=0, pixel_scales=0.1
    )
```

Under TEST_MODE the search is reduced, so `files/tracer.json` IS written but the
visualisation output `image/tracer.fits` is not. The guard passes and the read
raises:

```
FileNotFoundError: .../output/test_mode/imaging/simple/modeling/<id>/image/tracer.fits
FAIL: imaging/modeling.py
```

- Present since `cfd5334c` (2026-04-14); the script is untouched since 2026-08-04,
  so this is long-standing, not a regression from the regime-stamp release.
- **TEST_MODE-specific.** The same script passes at release fidelity — Heart's
  Stage 3 integrate ran `run_scripts (3.12, autolens, imaging)` green
  (672p/0f), because a full-fidelity fit does write `tracer.fits`.
- Reproduced in PyAutoHands `release.yml` run 32542888112, job
  `run_smoke_tests (3.12, autolens_workspace)`.

## Why it matters (and why it is NOT urgent)

It does not block releases: the `release` job's `needs:` is
`[resolve_mode, release_test_pypi, version_number]` and excludes
`run_smoke_tests`, so the publish succeeds regardless — run 32542888112 is marked
`failure` yet published 2026.8.22.1. The real cost is that it leaves the smoke
gate permanently red, so a genuine workspace regression would look identical to
this known failure and be ignored.

## Traps

- Do **not** "fix" this by deleting the result-loading block. It is a documented
  teaching section, and `draft/maintenance/workspaces/read_through_issues.md`
  separately asks for the equivalent section to be **added** to the other
  `modeling.py` examples (group, cluster, interferometer). Coordinate with that
  prompt — whatever guard shape is chosen here should be the one propagated
  there, or the same bug ships to four more scripts.
- Guarding on `image/tracer.fits` alone would silently skip the `tracer.json`
  load in test mode. Prefer guarding each read on the file it actually reads.

<!-- formalised by the Intake (Conception) Agent on 2026-08-22 from user-intake -->
