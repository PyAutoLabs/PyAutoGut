- issue: none — shipped directly as a PR (small, single-repo, behaviour-preserving)
- completed: 2026-08-22
- library-pr: https://github.com/PyAutoLabs/PyAutoGalaxy/pull/584 (merged 506f153)
- workspace-pr: none — no workspace change needed

`autogalaxy/util/plot_utils.py` and `autogalaxy/plot/plot_utils.py` were
byte-identical (md5 `a6eed88a228524d55403418fdf01d32a`), both defining the plot
helpers and `fits_array`. Found while auditing every FITS write path in the stack
for PyAutoNerves#153 (`complete/2026/08/small-datasets-regime-stamp.md`).

`util/` is the real home: `plot/__init__.py:9` imports the public
`plot_array`/`plot_grid`/`fits_array` from it, eight internal modules import it,
PyAutoLens references it thirteen times. The duplicate was deleted.

**Why it was worth doing rather than tolerating.** Both copies sat on a FITS write
path. A change applied to one and not the other splits behaviour between callers
with nothing to catch it — separate modules, so no test compares them and no
import fails. That is a silent-divergence trap, not just untidiness.

**THE METHOD LESSON, and the reason this nearly shipped broken.** The importer
search used a LINE-ANCHORED grep (`^from autogalaxy.plot.plot_utils`) and returned
ZERO across every repo. The deletion looked provably safe. It was not:
`test_autogalaxy/plot/mat_wrap/test_visuals.py:41` has an INDENTED, FUNCTION-LOCAL
import, which an anchored pattern silently skips. The test suite caught it
immediately (passed on clean main, `ModuleNotFoundError` with the change).

**When removing a module, search UNANCHORED.** Python's function-local imports do
not sit at column zero, and a `^`-anchored grep reports a false negative that reads
exactly like proof of safety. The unanchored search then found exactly one
reference, which is what shipped.

**TRAPS**
- `^from X` / `^import X` greps miss function-local, class-body and conditional
  imports. Never treat an anchored search as proof a module is dead.
- Verify behaviour-preservation with an IDENTICAL test COUNT against clean main,
  not just "the suite passes" — a deleted or uncollected test also passes.
- A dead-module deletion leaves dangling Sphinx cross-references. `galaxies_plots.py`
  pointed `:func:`~autogalaxy.plot.plot_utils._critical_curves_from`` at the deleted
  module; re-pointed. PyAutoGalaxy's CI has a `docs / docs-build` job that the other
  library repos lack, and it is the check that matters for this class of change.

**Debris found and removed.** A stray `/btw ok` line was sitting inside the
`_critical_curves_from` docstring, having arrived in `3ca31bf` (#582) and been
inherited by both copies. It renders into the API docs. Treated as committed junk,
not as an instruction. Worth a wider sweep: a stray keystroke reached a merged PR
once and may have siblings elsewhere.

Tests: 1099 passed / 5 skipped, an IDENTICAL count to clean main. CI green on
3.12 / 3.13 / nojax / docs-build.

**Gate note.** Heart was not consulted — no PyAutoHeart checkout in this
web-github session; the documented per-repo suite fallback was used, and CI agreed.

## Original prompt

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
