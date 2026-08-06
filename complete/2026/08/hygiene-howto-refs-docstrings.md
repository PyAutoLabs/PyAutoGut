Routed from the 2026-08-06 full /hygiene run (refs + docstrings modes). Four
mechanical prose/structure fixes across the HowTo repos, shipped same-day:

- HowToGalaxy `scripts/README.md` — chapter_3/chapter_4 bullets repointed to
  the post-restructure folders (`chapter_3_pixelizations`,
  `chapter_4_scaling_up_galaxies`); rest of the README already matched.
- HowToGalaxy `tutorial_2_multi_galaxy.py` + HowToLens
  `tutorial_3_scaling_relation.py` — adjacent `"""` blocks merged at the
  `__Model__` / `__Model Fit__` boundaries; notebooks regenerated 1:1 via
  `autohands/generate.py` (no orphan churn).
- PRs: HowToGalaxy#64 (fd70659e) + HowToLens#69 (f1ad338a), both
  `pending-release`, merged 2026-08-06 on explicit human instruction with CI
  UNRUN — GitHub Actions was in a major outage (githubstatus: Actions =
  major_outage) that swallowed the pull_request events; validation was local
  (py_compile + 1:1 notebook regen on a prose-only diff). Ship gate was Heart
  RED (release-drive integrate artifact), human-authorized override recorded
  in the active.md entry.

Key judgments and gotchas:
- Brain sized this 9/large + split-into-phases — prose-driven artifact;
  human-precedented override kept it single-task (2 repos / 3 files).
- 5 of the 7 hygiene `refs` findings were scanner false positives: `weak/*.py`
  references in HowToLens `tutorial_6_weak_lensing.py` are sibling-repo
  references whose targets all exist in `autolens_workspace/scripts/weak/` —
  deliberately untouched (memory: hygiene-refs-cross-repo-false-positives).
- The same outage had failed the day's main-branch workflow runs in both
  repos ("Failed to resolve action download info") — re-triggered; not code.

Follow-up: none owed by this task. The tutorials' LaTeX SyntaxWarnings found
en route are filed as draft/maintenance/workspaces/latex_raw_string_docstrings.md.

## Original prompt

# Hygiene batch: HowToGalaxy README chapter repoint + two adjacent-docstring merges

Type: refactor
Target: workspaces
Repos:
- HowToGalaxy
- HowToLens
Difficulty: small
Autonomy: safe
Priority: low
Status: formalised

Original request (2026-08-06, after a full `/hygiene` run): "ok, action all
this with good delegation where possible., do as much as possible" — approving
the hygiene digest's 4-item refactor batch.

The 2026-08-06 `/hygiene` scan (`pyauto-brain hygiene refs` + `hygiene
docstrings`) found exactly four real items of mechanical debt, all
behavior-preserving prose/structure fixes:

1. **HowToGalaxy `scripts/README.md:7-8` — dead folder references.** The
   bullets describe `chapter_3_search_chaining` and `chapter_4_pixelizations`,
   but the folders on disk are `chapter_3_pixelizations` and
   `chapter_4_scaling_up_galaxies`. Rewrite both bullets (label + description)
   to match the current chapter structure.
2. **HowToGalaxy
   `scripts/chapter_4_scaling_up_galaxies/tutorial_2_multi_galaxy.py:170-172`
   — adjacent `"""` boundary.** Two back-to-back docstring blocks with no code
   between; merge into one block (the second opens `__Model__`).
3. **HowToLens
   `scripts/chapter_4_scaling_up_lensing/tutorial_3_scaling_relation.py:478-480`
   — same adjacent `"""` merge (the second block opens `__Model Fit__`).**
4. Verified NON-items, do not "fix": the 5 `weak/*.py` refs in HowToLens
   `tutorial_6_weak_lensing.py` are sibling-repo references whose targets all
   exist in `autolens_workspace/scripts/weak/` — correct as written.

Notebook regeneration for the two touched tutorials follows the standard
workspace ship path. No API surface, no science content changes — pure
mechanical hygiene routed from the Hygiene Agent to /refactor.
