# Re-stamp 5 drifted provenance content_sha256 hashes in autogalaxy_assistant

Type: maintenance
Target: autogalaxy_assistant
Repos:
- (single repo) autogalaxy_assistant — wiki/core pages only, no library or workspace code
Status: planned
Difficulty: small
Autonomy: safe
Priority: normal

## Why

The 2026-08-07 release run (PyAutoHands release.yml 31200419263, publishing
2026.8.7.1) failed its `wiki_currency_check_autogalaxy / wiki-currency` job on
**real drift**. This is not the PyPI index-propagation race that killed the
autolens sibling job — autogalaxy installed cleanly and then found genuine
provenance errors.

The drift is narrowly scoped. Everything else in that job is clean:

- version drift (`--check-version`): clean — installed public API surface matches
  baseline (autogalaxy 2026.8.7.1)
- symbol audit (`--scope all`): 46 files, 221 symbols, **0 missing/broken**
- idiom deny-list (`--lint-idioms`): clean, 122 files
- citations (`--check-citations`): 78 files, 1061 citations, **0 missing paths**
- provenance (`--check-provenance`): **5 errors**, 101 warnings

Only provenance fails, and it fails the whole job (`exited 1`), so this red will
persist on autogalaxy_assistant main — and on every future PR to that repo —
until it is re-stamped. That is the same "red persists on main for every future
PR" trap already recorded for this repo under mge-sigma-min-workspace-sweep
(phase-2-ci / DEBT 1).

## What is wrong

Five `wiki/core` pages have a `content_sha256` mismatch — the body was edited
after stamping, so the declared hash no longer matches the actual body:

- `wiki/core/concepts/inversions_and_pixelizations.md` (declared `3719a1a00664…`, actual `488dca78b057…`)
- `wiki/core/concepts/non_linear_search.md` (declared `05120accc325…`, actual `ba0c3184a959…`)
- `wiki/core/external/howtogalaxy.md` (declared `f6443e77f49a…`, actual `cd80be76ccf9…`)
- `wiki/core/external/rtd.md` (declared `4a680d62d8a2…`, actual `9663f05ab039…`)
- `wiki/core/external/skill_citation_map.md` (declared `85756d5daf2d…`, actual `b8455d3ccf68…`)

The tool's own instruction for each: *"Re-validate against the pinned commit,
then `--write-provenance`."*

## Scope note — the 101 warnings are NOT in scope

Every warning is of the form `<Repo>: no git checkout resolvable — commit checks
skipped (packaged install?)`. That is expected on a CI runner, where the
libraries are pip-installed rather than checked out. They are not actionable and
must not be "fixed" by making CI check out every source repo.

## How

1. Re-validate each of the five pages against its pinned commit — the point of
   the stamp is that a human confirmed the prose still matches the source at that
   commit. Do **not** blind-restamp: `--write-provenance` will happily bless
   wrong prose, which converts a real signal into a green light.
2. Then re-stamp: `python3 autoassistant/audit_skill_apis.py --write-provenance`
3. Confirm the provenance leg exits 0 and the other four legs stay clean.

## Traps

- **Do NOT run `--write-baseline` from this workspace.** Recorded under
  mge-sigma-min-workspace-sweep (`baseline-repin-TRAP`): it derives api_surface
  from the INSTALLED library, and local installs are the SOURCE checkouts, not
  the released stack CI grades against — a local re-pin stamps the wrong version
  and turns the check green on a false premise. This task does not need a
  baseline re-pin at all (version drift is already clean); it only needs
  provenance re-stamping.
- **gh trap:** autogalaxy_assistant siblings use SSH remotes, where `gh pr create`
  fails with "none of the git remotes … point to a known GitHub host". Create the
  PR via `gh api repos/<owner>/<repo>/pulls --method POST --input <json>`.
  (Recorded for autogalaxy_assistant under mge-sigma-min-workspace-sweep.)
- **wiki-currency CI has paired-PR support** — it checks out any cited source repo
  having a branch matching the PR head, so a paired branch is the grading ground
  truth.

## Evidence

Full drift report captured to `~/.pyauto-heart/release_20260807_wiki_drift/drift-report.md`
(the autofit sibling, 0 errors, is under `autofit/`). Captured deliberately on the
laptop: Actions artifact downloads are blocked from cloud/mobile sessions, so this
evidence is not retrievable from a phone session and the artifact eventually expires.

## Related, not folded in

`wiki_currency_check` for **autolens** failed separately on a PyPI
index-propagation race and never got as far as checking anything. RESOLVED
2026-08-07: graded locally against a clean venv on released `autolens==2026.8.7.1`
(PYTHONPATH cleared, all four libraries verified resolving to venv site-packages)
— **all five legs clean**: version drift clean, 0 missing/broken symbols, idioms
clean, 0 missing citations, 0 provenance errors. **No equivalent autolens prompt
is needed.** This task is autogalaxy_assistant only.
