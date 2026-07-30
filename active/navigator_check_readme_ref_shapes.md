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
