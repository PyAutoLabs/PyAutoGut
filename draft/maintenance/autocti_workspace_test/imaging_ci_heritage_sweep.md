# The root-level `imaging_ci/` heritage tree was missed by the Phase 5 legacy sweep

Type: maintenance
Target: autocti_workspace_test
Repos:
- @autocti_workspace_test
Difficulty: small
Autonomy: supervised
Priority: normal
Status: formalised
Filed: 2026-08-24

CTI resurrection Phase 5 (`complete/2026/07/cti-resurrection-phase5.md`) rebuilt
`autocti_workspace_test` as a modern integration suite and preserved the 2022-23
Euclid VIS heritage verbatim under `legacy/` — `euclid/`, `tvac/`, `temporal/`,
`validation/`, `overview_output/` and `config_2023/`, with a `legacy/README.md`
explaining the era.

**It missed a tree.** `imaging_ci/` still sits at the repository root — 43 files,
~284 KB — outside both `legacy/` and `scripts/`:

```
imaging_ci/
  cosmics/      cosmic-ray flagging + its simulators (imports `lacosmic`)
  profiling/    add_cti / likelihood / pruning / arctic run-time profiling scripts
  simulators/   uniform charge-injection simulators (parallel_x1/x3, serial_x1/x3)
  temporal/     individual_fits.py, individual_temporal.py
```

## Why this is the same heritage, not live material

Three independent signals, all checked against `main` (01f1d72):

1. **Same era, same dead API.** The files carry the pre-resurrection prose and
   imports — `import autocti.plot as aplt` (the removed Plotter object stack),
   docstrings writing datasets to `/autocti_workspace/dataset/...`, `lacosmic`
   as a hard import. `legacy/README.md` describes exactly this: "target the
   pre-2025 PyAutoCTI API ... **not runnable** against the current stack".
2. **Nothing references it.** Every `imaging_ci` reference outside the tree
   resolves to `scripts/imaging_ci/model_fit.py` — `smoke_tests.txt:2`,
   `AGENTS.md:23`, and the `aplt.subplot_imaging_ci*` calls in
   `scripts/plot/subplots.py`. No CI workflow, no config, no `.gitignore` entry
   names the root tree.
3. **It is undocumented.** `AGENTS.md` "Repository Structure" lists `scripts/`,
   `legacy/`, `config/` and `smoke_tests.txt` and does not mention it at all —
   so the repo's own canonical layout map already behaves as though the tree
   does not exist.

It is also a **naming hazard**: a root-level `imaging_ci/` sitting next to a
`smoke_tests.txt` line that reads `imaging_ci/model_fit.py` (resolved relative
to `scripts/`) invites exactly the wrong reading of which tree is live.

## Work

1. **Move `imaging_ci/` → `legacy/imaging_ci/` verbatim.** `git mv` only — no
   content edits, no reformatting, no modernization. The Phase 5 precedent is
   preservation, and `AGENTS.md` already says "Never edit `legacy/`".
2. **Extend `legacy/README.md`** with the `imaging_ci/` entry, matching the
   existing one-line-per-subtree style, and note it was swept later than the
   rest (Phase 5 missed it) so the record is honest about provenance.
3. **Update the `AGENTS.md` "Repository Structure" block** so its `legacy/`
   line names `imaging_ci/` alongside the trees it already covers. The block
   never listed the root tree, so this is the first time the layout map and the
   repository agree.
4. **Verify nothing broke.** `python .github/scripts/run_smoke.py` (3/3) after
   the move, and re-grep for `imaging_ci` references to confirm the only hits
   outside `legacy/` are the `scripts/` ones listed above.

## Explicitly out of scope

- **Modernizing** any of the moved scripts to the current PyAutoCTI API. If the
  profiling scripts are wanted live, that is a separate task against
  `autolens_profiling` conventions, not this sweep.
- **Condemning** the tree (Gut transit-and-void). Phase 5 chose preservation for
  its sibling trees; this sweep follows that choice rather than re-litigating it.
  If the heritage should instead be condemned, that is a decision to take across
  all of `legacy/` at once, not for this one subtree.

## Context

- `PyAutoMind/complete/2026/07/cti-resurrection-phase5.md` — the sweep that
  established `legacy/` and named the trees it moved.
- `autocti_workspace_test/legacy/README.md` — the preservation rationale.
- `autocti_workspace_test/AGENTS.md` — "Never edit `legacy/`" and the structure
  block this task updates.
