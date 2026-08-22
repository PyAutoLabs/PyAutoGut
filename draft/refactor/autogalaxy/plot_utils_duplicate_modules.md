# autogalaxy has two byte-identical plot_utils modules

Type: refactor
Target: autogalaxy
Repos:
- @PyAutoGalaxy
Difficulty: small
Autonomy: safe
Priority: low
Status: formalised

Found 2026-08-22 while auditing every FITS write path in the stack for
PyAutoNerves#153 (`complete/2026/08/small-datasets-regime-stamp.md`); unrelated to
that change and deliberately not absorbed into it.

`autogalaxy/util/plot_utils.py` and `autogalaxy/plot/plot_utils.py` are
**byte-identical** — same md5 (`a6eed88a228524d55403418fdf01d32a`). Both define
`fits_array`, which routes to `output_to_fits`.

Import counts inside `autogalaxy/`:

- `util.plot_utils` — 8 importers
- `plot.plot_utils` — 1 importer

So the `util` one is the de-facto home and `plot` one is near-dead, but neither
is unused, which is why this needs a real check rather than a delete.

## Why it matters slightly more than ordinary duplication

Both modules are on a FITS write path. A future change to how figures are written
— the regime stamp landed on exactly this surface — applied to one copy and not
the other produces a silent behavioural split between callers, with nothing to
catch it: they are separate modules, so no test compares them and no import fails.

## Suggested scope

1. Confirm the two files are still identical (they may have diverged since
   2026-08-22 — if they have, that divergence is itself the finding and this
   prompt should be rewritten around it).
2. Check for external importers outside `autogalaxy/` before deleting either —
   PyAutoLens, the workspaces and any notebook may reach in.
3. Keep `util/plot_utils.py`, re-point the single `plot.plot_utils` importer, and
   delete the duplicate. Or, if `plot/` is the intended long-term home, do the
   reverse — but pick one deliberately rather than by import count.
4. Behaviour-preserving: no output should change.
