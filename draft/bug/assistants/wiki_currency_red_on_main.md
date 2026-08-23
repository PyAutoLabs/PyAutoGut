# Both assistant repos have a red wiki-currency check on main

Type: bug
Target: assistants
Repos:
- @autolens_assistant
- @autogalaxy_assistant
Difficulty: low
Autonomy: supervised
Priority: normal
Status: draft
Filed: 2026-08-23

## Provenance

Found while shipping `pynufft_removal_downstream_residue` phase 2
(`complete/2026/08/pynufft-removal-residue-phase-2.md`), which recorded it as
**"Found while shipping, NOT filed anywhere"**. This prompt is that filing; it
is not a regression caused by phase 2 — establishing that is the useful part
below.

Both assistant PRs in phase 2 (@autogalaxy_assistant#19, @autolens_assistant#115)
merged over this red, human-authorized, after the check was run on untouched
`main` to establish whose fault it was.

## The evidence (2026-08-23)

Symbol audit `--scope all`:

- `main` reports **missing/broken: 2** in *both* repos.
- The phase-2 PR branches reported **1** — the PRs REDUCED the count by exactly
  the `TransformerNUFFTPyNUFFT` reference they removed.

So one survivor predates that work in each repo:

- **`al.mesh.RectangularAdaptImage`** — absent from the installed stack.
  Audit suggestions: `RectangularRTUAdaptImage`, `RectangularBilinearAdaptImage`.
  Related: `draft/feature/autoarray/rectangular_bilinear_rtu_mesh_split.md`,
  which is the mesh split that renamed this surface — check whether the wiki
  text should be repointed now or should wait for that task to land, rather
  than mechanically swapping the symbol.
- **@autogalaxy_assistant additionally fails `--check-citations`** on
  `wiki/core/operations/sandbox.md`, which cites
  `PyAutoGalaxy:autogalaxy/plot/plot_utils.py` — a file that no longer exists.
  That page was untouched by phase 2.

## Why it matters

A permanently-red check on `main` is a broken signal: the next PR to either
repo cannot tell its own red from the inherited one, which is exactly the
situation phase 2 had to spend effort disambiguating.

## Acceptance

- Symbol audit `--scope all` reports `missing/broken: 0` on `main` in both
  assistant repos.
- `--check-citations` passes on @autogalaxy_assistant.
- Wiki body edits carry `--write-provenance` (scoped `--page`, so no unrelated
  pin moves).
