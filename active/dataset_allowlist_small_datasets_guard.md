# Guard: allowlisted datasets reachable from a capped `should_simulate` call site

Type: feature
Target: pyautohands
Repos:
- @PyAutoHands
- @PyAutoArray
Difficulty: small
Autonomy: supervised
Priority: medium
Status: in-review (PyAutoHands#253, PyAutoArray#480)

Follow-up from autolens_workspace_test#264 (fix for PyAutoArray#470). That PR
fixed the single live instance by declaring `full_datasets` on the one offending
script; this prompt closes the general footgun and corrects a docstring that
actively misleads about it.

Deliberately **not** ridden into #264: `PyAutoHands` was claimed by the
`hands-hygiene-leftovers` task at the time. Started 2026-08-22 as a **parallel
claim** — that task's branch is disjoint at file level (`AGENTS.md`,
`generate_release_notes.py`, `bin/autohands`, two unrelated test files), so the
`worktree_check_conflict` block was overridden after the hand check that
[[feedback_worktree_conflict_guard_never_fires]] prescribes.

**Design note that only surfaced in implementation:** the obvious predicate —
"the resolved path sits under an `!dataset/...` allowlist prefix" — is WRONG and
over-reports. `autocti_workspace` commits five doc images directly in
`dataset/overview/` while its overview scripts regenerate
`dataset/overview/imaging_ci/uniform` and `dataset/overview/dataset_1d`, which
hold nothing tracked; prefix matching called all six release-blocking failures.
The correct invariant is **"`rmtree(path)` would delete git-tracked files"**.
Caught only by running the guard across every workspace before trusting it.

## Part 1 — extend the allowlist guard (PyAutoHands)

`autohands/check_dataset_allowlist.py` today asserts that every tracked file
under `dataset/` is covered by the workspace's `!dataset/...` allowlist — i.e.
that nothing *generated* got committed. It does not check the mirror-image
failure: that nothing *committed* gets deleted.

Add that second assertion. For each allowlisted dataset directory that has
tracked files, fail when it is reachable from a `should_simulate` call site in a
script whose `__Env__` `ENV:` tokens do not release `PYAUTO_SMALL_DATASETS`
(i.e. contain neither `full_datasets` nor `real_output` — resolve via
`ENV_DECLARATION_TOKENS` in `autohands/env_config.py`, do not hardcode the pair,
so a future token that releases the var is picked up automatically).

Why here rather than a new checker: this module already parses these allowlists,
already runs from a workspace root, and already runs as leg 4 of `pre_build`.
It is the lean existing lever.

Sharp edge to design around: matching a call site to a dataset directory is not
purely syntactic — `dataset_path` is often assembled from variables
(`Path("dataset") / "point_source" / dataset_name`). A conservative
literal/leaf match that under-reports is acceptable; one that over-reports and
fails `pre_build` spuriously is not. Whatever bound is chosen, **log what was
skipped** — a silent partial sweep reads as "covered everything".

Reference sweep (the one that found the single live instance) and its false
positives are in autolens_workspace_test#264's description.

## Part 2 — correct the `should_simulate` docstring (PyAutoArray)

`autoarray/util/dataset_util.py`, `should_simulate`'s "Known gap" section ends:

> Note that point-source datasets are **not** in this gap: they write a
> top-level `data.fits` alongside their JSON and are covered normally. The
> original issue text grouped them with weak lensing as "JSON with no FITS";
> that is true of weak lensing only.

That holds in `autolens_workspace`. It is **false** in
`autolens_workspace_test`, whose `dataset/point_source/simple` is three tracked
JSON files and no FITS — that repo's `.gitignore` lists `data.fits` under
"Generated artifacts — never check in", so the stamp can never reach it under
any placement. This is precisely the directory PyAutoArray#470 was about, so the
docstring currently reassures the reader about the one case that bit us.

Docstring-only; no behaviour change, no release exposure.

<!-- Filed 2026-08-22 from the start_dev session for
     draft/bug/autoarray/small_datasets_rmtree_of_committed_data.md. -->
