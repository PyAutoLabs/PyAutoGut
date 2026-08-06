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
