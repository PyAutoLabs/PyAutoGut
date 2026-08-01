# Build autogalaxy_assistant — the galaxy structure modeling assistant cell

Type: feature
Target: autogalaxy_assistant
Repos:
- @autogalaxy_assistant
- @PyAutoBrain
- @autogalaxy_workspace
- @PyAutoGalaxy
- @HowToGalaxy
Difficulty: large
Autonomy: supervised
Priority: normal
Status: formalised

Build **autogalaxy_assistant**, the science-assistant cell for galaxy structure
modeling with PyAutoGalaxy, hand-built as a mirror of the mature reference cell
`autolens_assistant` (the autofit_assistant precedent: hand-authored by direct
comparison, with the Clone Agent's template partition used as a checklist only —
the clone tool is NOT run; user judged it a bit outdated). This completes the
llms.txt-census birth checklist (`complete/2026/08/llms-txt-census-fixes.md`)
and resolves the 8 public places that already advertise the assistant and 404
today (PyAutoGalaxy README/RTD ×4, autogalaxy_workspace start_here ×3, org
profile README).

## Original request (verbatim)

> Make the autogalaxy_assistant, which is basically a mirror of the
> autolens_assistant but for galaxy structure moeling, which is of course
> PyAutoGalxy's science case. I think this is self explanatory but ask
> questions if not. and of course this will continue and build on the llms.txt
> work

## Locked human decisions (2026-08-01)

- Repo gate: **PyAutoLabs/autogalaxy_assistant, PUBLIC at birth** (autofit
  precedent) — every merged PR must leave the tree honest, zero lensing
  residue, green CI.
- **Real galaxy cutouts sourced now** (recommended: one multi-band JWST
  COSMOS-Web NIRCam cutout of a non-lens galaxy; human names/approves the
  target — never invent provenance). Second HST/PyAutoReduce dataset deferred.
- **Phased PRs under one epic** on PyAutoBrain (autocti precedent #136), 7
  phases: 0 epic/repo/registry → 1 frame+tooling+stack reference → 2 real
  dataset+README+external signposts → 3 wiki/core+tooling skills → 4a/4b ag_*
  skill set → 5 wiki/literature → 6 benchmarks+HPC+full newborn gate.
- Execution phases delegated to **Opus** subagents (user override of the usual
  Sonnet split); judgment/review stay in the driving session.

## Routing / gates

- Partition verified live: 56 generic / 89 mixed / 301 domain / **0
  unclassified** @ reference `b9c10a9` — no reference-side Phase-0 unblock
  needed (unlike autocti).
- Intake trap (hit on ic50 + autocti): the Target is the assistant cell —
  PyAutoGalaxy is a consumed dependency, never the edit target.
- Privacy seam: `PyAutoMemory/wiki/galaxies/` (thin: 2 concepts / 0 entities /
  12 sources) consulted for structure/pointers only, never copied; all
  literature content authored from public sources with WebSearch-verified
  citations.
- Publish gate: `PyAutoHeart/docs/newborn_validation.md` legs 1-4 run
  per-phase where applicable and in full at Phase 6 (public at birth means the
  gate protects honesty, not the visibility flip).
- Full approved plan: the epic issue carries the phase checklist; detailed
  design in the driving session's plan record.
