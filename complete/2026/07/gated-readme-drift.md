Cleared the remaining README drift in the four repos that run PyAutoHands'
reusable `navigator_check` workflow but were not covered by phase 2:
autofit_workspace, HowToFit, HowToGalaxy, HowToLens. 40 findings.

- autofit_workspace#124 (8/8 green), HowToFit#37, HowToGalaxy#49,
  HowToLens#60 (10/10 each) — all MERGED, issue #123 closed.

## Why this existed as its own phase

Not tidying — a **prerequisite**. `check_navigator.py` is repo-agnostic and gates
**six** repos. Widening it (phase 3) while these four were dirty would have
turned them red on their next PR. The approved plan had them grandfathered into
`.navigator_check_ignore`; sweeping instead means the gate lands clean everywhere
and carries no deferred-debt ignore file. All six repos are now README-clean.

## What was wrong

Dominated by one class, identical to autolens/autogalaxy: `config/**/README.md`
inventories listing YAML that is not shipped — `grids` (gone), `non-linear`
(it is `non_linear`), `notation` (now a file), `mcmc`/`nest`/`mle.yaml` (only
`GridSearch.yaml` ships), `include`/`mat_wrap*.yaml` (only general/plots/
plots_search). Plus: `scipts` typo and a non-existent `projects` folder
(autofit_workspace README); `config.py` → `configs.py` and a deleted
`database.py` (cookbooks); `overview_2_science_workflow` →
`overview_2_scientific_workflow` (3 HowToFit files); `chapter_5_hyper_mode`
(HowToLens, gone).

## Trap: the generator project is per-repo, not per-library

First push failed `Catalogue staleness` on all three HowTo repos. I regenerated
their catalogues with the **library** project name (`autolens`/`autogalaxy`/
`autofit`), but each HowTo repo declares its own in
`.github/workflows/navigator_check.yml`: `howtolens`/`howtogalaxy`/`howtofit`.
Wrong project ⇒ catalogue title rewritten ⇒ staleness failure. Always read the
`project:` input from the repo's own workflow before running
`regenerate_navigator.py`.

## Clone lineage, second confirmation

HowToGalaxy carried the same `generag.yaml` (blind `al`→`ag` substitution of
`general.yaml`) fixed in autogalaxy_workspace, and all four shared byte-similar
stale config READMEs. These repos were cloned from a common source and the
config docs were never re-checked.

## Follow-on

Phase 3 (`draft/feature/pyautohands/navigator_check_readme_ref_shapes.md`) is now
unblocked, and scoped by human decision to the **narrow** design: teach the gate
relative-to-file path resolution only, leaving the structure-list quorum and
anchoring heuristics to the periodic `/hygiene` audit. Rationale: porting the
full rule set would duplicate ~200 lines into a second organ where the two copies
would drift, and the Brain/Hands boundary forbids sharing the module.
16 script-prose findings remain in these four repos (out of scope; covered by
`draft/docs/workspaces/script_prose_and_howto_ref_drift.md`).
