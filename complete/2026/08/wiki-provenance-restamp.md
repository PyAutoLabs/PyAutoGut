Cleared the five `content_sha256` errors that failed `wiki_currency_check_autogalaxy`
during the 2026-08-07 release run (PyAutoHands release.yml 31200419263), and which
had persisted on `autogalaxy_assistant` main — reddening every future PR to that
repo — since 2026-08-06.

Shipped as `autogalaxy_assistant` 9e9f9dc on branch
`claude/automind-task-planning-k13fsk`. Five files under `wiki/core/`, no library,
workspace or skill code touched.

**The prompt's framing was inverted, and that changed the work.** Intake scoped this
as a pure `--write-provenance` re-stamp and warned against blessing stale *prose*.
The opposite was true: the prose was correct and the *pins* were stale. All five
mismatches traced to a single commit, b2fc57a ("docs: update HowToGalaxy references
for the tutorial restructure", PR #12), whose own message records the deferral —
*"The page's pinned_commit frontmatter is left for the ag_update_wiki maintainer
flow."* This was known debt, not an accident.

The load-bearing detail: **`--write-provenance` rewrites `content_sha256` only and
never touches `pinned_commit`** (`autoassistant/audit_skill_apis.py:1132-1133`). So
the one-line fix the prompt describes would have turned the job green while leaving
two pages attesting current prose against superseded source. Worth remembering the
next time a provenance red looks like a formality.

Re-pinned (2 pages), after re-validating the prose against those checkouts:

- `external/howtogalaxy.md` — HowToGalaxy `b1815e9d` -> `ee283c9d`. This pin *had*
  to move: b2fc57a rewrote the page's own `paths:` list to `chapter_3_pixelizations`
  / `chapter_4_scaling_up_galaxies`, directories that do not exist at `b1815e9d`.
  The checker cannot catch this — it verifies a pin is a real, reachable commit, not
  that the declared paths exist there. Verified against `ee283c9d`: 6+10+6+3+1 = 26
  tutorials, 6 simulators, 32 `.py` total, 26+6 = 32 matching notebooks, all three
  chapter tables agreeing with the files on disk.
- `external/skill_citation_map.md` — autogalaxy_assistant `a083753c` -> `239a61c`,
  4 commits stale on `skills/` (22 files, incl. two entirely new skills). Content was
  already current — 25 skills on disk, 25 rows, zero drift either way, and all 13
  HowToGalaxy cells resolve — so this was a pin correction, not a rewrite.

Re-stamped only (3 pages). Each took a one-line HowToGalaxy cross-reference from
b2fc57a, and none of their pinned projects moved; each claim was re-verified against
source: chapter 3 does carry the linear algebra and Bayesian statistics
(`tutorial_3_inversions`, `tutorial_5_bayesian_formalism`); chaining is
`tutorial_9_search_chaining` + `tutorial_10_prior_passing`; and `PyAutoGalaxy:docs/
howtogalaxy/` has exactly `chapter_1_introduction` .. `chapter_4_scaling_up_galaxies`
plus `chapter_optional`.

Key judgments and gotchas:

- **Self-check worth reusing.** Four of the five new hashes landed exactly on the
  "actual" values the checker had reported *before* any edit — proof that no prose
  changed in those four. Only `howtogalaxy.md` differed, and only by the one
  deliberate addition. A cheap way to prove a re-stamp is a re-stamp.
- **Folded in a cheap fix** (human-approved): HowToGalaxy carries two *extensionless
  prose files*, `chapter_2_modeling/tutorial_11_summary` and
  `chapter_3_pixelizations/introduction` — chapter narrative, not tutorials (no
  `.py`, no notebook, excluded from the counts). Undocumented, they are an active
  trap: listing the directory makes the first look like an eleventh tutorial, and the
  page's own URL-building rule (`scripts/<chapter>/<tutorial>.py`) yields a 404 for
  it. Now documented beside the existing chapter-1 caveats, including the contrast
  with chapter 1's `tutorial_5_summary.py`, which *is* a real script and *is* counted.
  (An earlier read mistook `tutorial_11_summary` for a directory; it is a file.)
- **Two of five audit legs were not gradeable in this session, deliberately.**
  `--check-version` and `--scope all` grade against an *installed* `autogalaxy`,
  which is absent from this cloud container — and per the `baseline-repin-TRAP`
  recorded under mge-sigma-min-workspace-sweep, grading against a local *source*
  install would have been meaningless anyway. CI is authoritative for those two. The
  change touches no PyAuto* symbols, only file paths and prose, so neither should
  move. Verified locally instead: `--check-provenance` **0 errors** (was 5),
  `--check-citations` 78 files / 1061 citations / 0 missing, `--lint-idioms` clean
  across 122 files.
- **The recorded `gh` SSH trap did not apply.** This clone's `origin` is HTTPS, not
  SSH, so `gh pr create` is usable here. The trap is real but clone-specific — check
  `git remote -v` rather than assuming.
- Worked direct on the designated branch rather than via `/start_dev` + worktree:
  this cloud session has a fixed branch across all repos, so the worktree half of
  that flow does not apply. Human-approved.

Follow-up: none owed. The sibling `wiki_currency_check` failure for **autolens** in
the same release run was a PyPI index-propagation race, already resolved and graded
clean on all five legs 2026-08-07 — no autolens counterpart to this task exists or
is needed.

## Original prompt

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
