# Fix dead plotter references in PyAutoFit docs/api/plot.rst

Type: docs
Target: PyAutoFit
Repos:
- PyAutoFit
Difficulty: small
Autonomy: supervised
Priority: normal
Status: in-flight

Filed 2026-07-12 from a `/hygiene docs` (`/audit_docs`) audit.

## Status 2026-08-07 — implemented, pushed, no PR

Branch `claude/automind-simple-task-y079sm` on PyAutoFit, commit `4e23d8ab7`,
one commit, docs-only. **No GitHub issue and no PR** — this was picked up
directly rather than through `/start_dev`, so nothing was issued. Opening the
PR is the next step and needs a human ask.

Delivered: `docs/api/plot.rst` rewritten against `autofit/plot/__init__.py` —
corner plots (`corner_cornerpy`, `corner_anesthetic`), sampling traces
(`subplot_parameters`, `log_likelihood_vs_iteration`), and `output_figure`
under its own "Figure Output" heading. The `:template:
custom-class-template.rst` / `:recursive:` options were dropped (class-template
directives, wrong for a function surface). Mirrors PyAutoGalaxy/PyAutoLens
`docs/api/plot.rst`, which already document `autofit.plot` this way — that was
the reference for the shape.

**Scope grew by three prose sites, deliberately.** The same removed classes were
being *called* in `docs/overview/the_basics.md:542`,
`docs/cookbooks/samples.md:296` and `docs/cookbooks/search.md:168` — a reader
copying those snippets hits an AttributeError, so the same defect was live on
RTD outside the API page. Each now calls the function that replaced it. While in
`search.md`, two adjacent workspace notebook paths were also dead
(`searches/mcmc/Emcee.ipynb`, `plot/EmceePlotter.ipynb`) and were repointed at
`searches/mcmc.ipynb` / `plot/emcee_plotter.ipynb`, verified against the
`autofit_workspace` checkout.

**Duplicate merged in:** `draft/docs/autofit/api_plot_rst_stale_plotter_classes.md`
(filed 2026-07-30 from the later `/audit_docs` sweep) described the same defect.
Deleted in this change; this file is the survivor.

Not done: `corner_cornerpy` / `corner_anesthetic` accept `**kwargs` and silently
**discard** them, yet `autofit_workspace/scripts/plot/*.py` (and the `search.md`
snippet inherited from it) pass a long corner.py kwargs list as if it were
forwarded. That is a library/workspace bug, not a docs one — worth its own
prompt, deliberately left alone here.

## Verification limits

The container has no numpy/autonerves/sphinx, so `import autofit.plot` and a
docs build could not run. Every documented name was instead checked against
`autofit/plot/__init__.py`, which is the definitive export list (five names, all
functions), and a repo-wide grep confirms no `NestPlotter`/`MCMCPlotter`/
`MLEPlotter`/`EmceePlotter` reference survives anywhere under `docs/`.
The Docs CI job is the real check.

`docs/sphinx_warning_baseline.txt` (67) is a **ceiling**: PyAutoHeart's
`docs-build.yml` fails only when the count *exceeds* it and merely emits a
notice when it drops. Removing three broken autosummary stubs can only move it
down, so no baseline edit was needed — but the job prints the new count, and
ratcheting the file down once that is known is a clean follow-up.

The `feature/ep-graphical-docs` coordination note below is **stale**: no such
branch exists on PyAutoFit any more, so the collision it warns about cannot
occur and this shipped standalone.

## Why

`PyAutoFit/docs/api/plot.rst` documents three classes under
`.. currentmodule:: autofit.plot` that **no longer exist** in the installed
`autofit`:

- `NestPlotter`
- `MCMCPlotter`
- `MLEPlotter`

A package-wide search finds no `*Plotter` class anywhere in `autofit` (not
renamed — removed/relocated). `autofit.plot` imports but exposes zero public
classes. The autosummary block therefore generates broken `_autosummary`
stubs. This was previously parked behind the graphical-model docs work; the
docs audit re-surfaces it as the only broken reference across all three
libraries' API docs (18/18 modules OK, 392/395 class refs OK).

## Scope

- Determine the **current** PyAutoFit plotting entry points (what replaced the
  removed plotters — likely a different plotting API surface) and repoint or
  remove the `plot.rst` autosummary block accordingly. Do **not** just delete
  and leave a hole if a live plotting API exists to document.
- This is a judgement call on the current API, hence a `/docs` task not an
  auto-fix.

## Coordination

There is an active `feature/ep-graphical-docs` worktree on PyAutoFit whose
scope covers plotting/graphical docs but which has **not** yet touched
`plot.rst` (verified identical to `main`). Either fold this fix into that
branch or ship it standalone — decide at plan time to avoid a collision.

## Verify

- `python -c "import autofit.plot"` and confirm each documented name resolves.
- Docs build produces no missing-reference / autosummary warnings for plot.rst.
