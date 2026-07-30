Closed the README ref-drift arc by teaching PyAutoHands' `check_navigator.py`
the relative folder references its token regex could never match.

- PyAutoHands#213 MERGED (`d121bea`), issue #212 closed.

## The blind spot this closes

`check_navigator.py` is a hard per-PR gate on **six** repos and already scanned
`scripts/**/README.md` — but `_PATH_TOKEN_RE` anchors every token on
`(?:scripts|notebooks)/`. Workspace READMEs name packages relative to their own
location ("The `imaging/data_preparation` package …"), so those references were
invisible. That is how a restructure rewrote folder lists across every workspace
while CI stayed green: the scripts still ran, only the reader was misdirected.

## Scope — narrow, by human decision

The approved plan said "mirror phase 1's rules". Reading both, that meant
duplicating ~200 lines of heuristic into a second organ where the copies would
drift, and the Brain/Hands boundary forbids sharing the module. Human chose the
narrow option:

- backticked, multi-segment, extension-less tokens only
- resolved against the referencing file's own folder, the repo, and the
  scripts/notebooks trees — exact, path-**suffix** or glob, `.py`/`.ipynb` folded
- skipped unless one end names something real (English shorthand "bulge/disk"
  must never fail a PR); accepting head **or** tail is essential, since
  requiring both misses the typo'd-head cases (`guide/advanced`)
- leading `./`, `../`, `<reponame>/` stripped; runtime roots ignored

**Bare structure-list names (``- `slam_pipeline`: ``) are deliberately NOT
gated** — the very symptom that started the arc. Telling a folder list from a
parameter glossary needs the quorum heuristic, which stays in `hygiene refs`
where a false positive is free. Pinned by a test so the boundary is explicit.

## The lesson worth keeping

**A gate must agree with the audit.** An early version rejected
`results/aggregator` and `modeling/advanced` — legitimate tail-quoted paths that
hygiene resolves, one of which *this arc had just written*. A gate that
contradicts the audit is worse than no gate, so resolution semantics were matched
deliberately rather than reinvented.

**Validate a gate in both directions.** "No findings" cannot distinguish a
working check from a broken one. Verified green on all six repos (before and
after merge) *and* red on a reintroduced `data_preparation/imaging` reversal.

## Traps

- `navigator_check.yml` is consumed `@main` by all six repos, so merging arms the
  gate everywhere immediately. All six were verified green first; PyAutoHands has
  **no PR-level CI**, so the local suite is the only gate.
- `worktree_check_conflict` fired for the first time on record (prior note said
  it never does), flagging PyAutoHands as claimed by `python-312-floor`. Hand
  check: the claim was a `repos:` entry recording release commit `95f7502`, with
  no PyAutoHands worktree and a clean tree; its phase-5a touches pre-build
  staging, this touched `check_navigator.py`. Proceeded on human go-ahead.
- The module had **no tests at all** before this (`tests/test_check_navigator.py`
  is new); full suite now 250.

## Original prompt

# Teach the navigator CI gate the workspace-README reference shapes

Type: feature
Target: pyautohands
Repos:
- PyAutoHands
- autofit_workspace
- HowToFit
- HowToGalaxy
- HowToLens
Difficulty: small
Autonomy: supervised
Priority: normal
Status: formalised

`autohands/check_navigator.py` already scans `scripts/**/README.md` (its
`reference_files()` expands them), but `_PATH_TOKEN_RE` hard-anchors every token
on `(?:scripts|notebooks)/`. Workspace READMEs reference packages *relative to
their own location* (`data_preparation/imaging`), as bare structure-list bullets
(``- `slam_pipeline`: …``), and as config file names (`mcmc.yaml`) — none of
which that regex can match. This is why a per-PR hard gate stayed green while the
READMEs drifted (see the sibling autolens/autogalaxy sweep prompt).

Extend the token patterns to mirror the widened hygiene `refs` rules from
`draft/feature/pyautobrain/hygiene_refs_readme_drift_class.md`, so the periodic
audit and the hard gate agree on what counts as a reference. Reuse the existing
`load_ignore` / `is_ignored` machinery; do not add a parallel suppression system.

**Blast radius — the reason this phase lands last.** The checker is
repo-agnostic and the `navigator_check.yml` workflow runs on **six** repos:
autolens_workspace, autogalaxy_workspace, autofit_workspace, HowToFit,
HowToGalaxy, HowToLens. The workspace sweep only cleans the first two, so
widening the regex would turn the other four red on their next PR.

Mitigation: run the extended checker against the four unswept repos, grandfather
their existing findings into each repo's `.navigator_check_ignore` (the
mechanism already exists and is already present in five of the six repos) with a
dated comment naming this prompt, and file a follow-up prompt to sweep them
properly. New drift is gated everywhere; pre-existing drift is explicitly
deferred, not silently hidden.

Land only after `draft/docs/workspaces/workspace_readme_drift_sweep.md` has
merged, or the two swept repos will fail their own gate.

Acceptance: `python autohands/check_navigator.py --root <repo>` exits 0 for all
six gated repos, and a real PR on autolens_workspace shows `navigator_check`
green.

## Original request

> the autolens workspacde readme has API drift (e.g. it refers to slam_pipeline).
> Can you do a sweep of this over autolens_workspaceand gaalxy and then put the
> thing in the hygeine agent?

(The CI-gate half was added after the audit found the same blind spot in both
scanners; the human chose "Hygiene + CI gate" when asked.)
