# `autofit.plot` functions accept `**kwargs` and silently discard them

Type: bug
Target: autofit
Repos:
- PyAutoFit
- autofit_workspace
Difficulty: small
Autonomy: supervised
Priority: normal
Status: shipped

## Shipped 2026-08-24 — PyAutoFit#1524 + autofit_workspace#148 MERGED

Issue **PyAutoFit#1523**. Branch `claude/autofit-plot-functions-kwargs-vvwj5x` in
both repos, merged library-first: PyAutoFit `56f1b87`, autofit_workspace `5056fa3`.
Both proven merged (`merge-base --is-ancestor` YES, 0 unmerged commits) before
this record was written.

CI green on every run and every leg, first attempt, no re-runs: PyAutoFit
`Tests` (`unittest (3.12)`, `unittest (3.13)`, `unittest-nojax`) + `Docs`;
autofit_workspace `Smoke Tests` (`changes`, `smoke (3.12)`, `smoke (3.13)`) +
`Navigator Check`. Each head sha produced only `pull_request` runs — these
workflows have no `push` trigger on a feature branch, so four runs is the
complete set.

**A release is owed**: library code plus a user-visible behaviour change. Both
PRs carry `pending-release`.

## The decision, and why the prompt's framing was incomplete

The prompt offered two fixes — forward the kwargs, or drop `**kwargs` — and
reserved the choice for a human. The human chose a **third**: forward *with a
strict signature filter*. That option only became visible after measuring what
plain forwarding would actually do, and the measurement is the finding worth
keeping:

**`corner.corner` has its own silent sink.** What it does not name goes to
`corner_impl(**hist2d_kwargs)` → `hist2d(**kwargs)`, whose body reads only
`extent` and drops the rest. So the prompt's fix 1 would *not* have fixed the
tutorials — 18 of their 76 kwargs would have stayed silently ignored, one layer
deeper. Any "just forward `**kwargs`" fix against a library with a `**kwargs`
sink has this shape; validating against *named* parameters only is what closes
it. `accepted_kwarg_names` therefore refuses to treat a `VAR_KEYWORD` parameter
as "accepts anything" — that refusal is the whole mechanism.

## Second defect found while verifying: weights were never applied

`corner_cornerpy` called `corner.corner(data=..., weight_list=samples.weight_list, ...)`.
corner has no `weight_list` parameter — it is `weights`. The weights went into
the same `hist2d` sink, so **every weighted corner posterior had been rendering
unweighted**, silently, for as long as that call has existed. Nested-sampling
and importance-weighted figures change appearance as of this PR.

Found by reading corner's real signature rather than trusting the call site.
The lesson generalises: a wrapper that passes a kwarg the wrapped library does
not name is indistinguishable from one that does, until you check.

## Traps hit

- **`figsize` is not a named parameter of `make_2d_axes`.** anesthetic takes
  `figsize` / `facecolor` through its own `**fig_kw`. The first routing split
  therefore sent a caller's `figsize` to `plot_2d` and the library's computed
  value won. A test caught it; the axes-routed set now names `figsize` /
  `facecolor` / `dpi` explicitly. Signature introspection is not enough when the
  target itself forwards through a sink — check where the values you compute
  actually land.
- **`@log_plot_exception` catches `TypeError`.** A rejected kwarg on
  `corner_anesthetic` would have surfaced as the misleading "posterior estimate
  not yet sufficient" info log. The decorator now re-raises `PlotKwargsError`.
- **`range=None` from a caller must not blank the guard.** `emcee_plotter.py`
  passes exactly that, and honouring it literally would hand `corner` back the
  degenerate columns `_corner_range_from` exists to widen. A caller `None`
  against a library-computed value means "use the default".
- **Monkeypatching the target breaks signature validation.** The test stub for
  `corner.corner` needed `functools.wraps` so `inspect.signature` still saw the
  real parameter list through `__wrapped__`.
- **Three of four workspace scripts had the wrong library's kwargs.**
  `dynesty_plotter.py` carried dynesty's `cornerplot` arguments, `zeus_plotter.py`
  zeus's, `nautilus_plotter.py` figure-geometry names corner never had — all
  passed to a function wrapping `corner.py`. Copy-paste from the sampler's own
  plotting docs is the likely origin, and the prose in each script pointed the
  reader back at those same docs, compounding it.

## Not done / follow-ups

- **`figure_of_merit_vs_iteration` is not re-exported from `autofit.plot`** — it
  lives only on `autofit.non_linear.plot`, unlike the other four. Pre-existing,
  noticed here, deliberately left alone as out of scope. Worth a prompt.
- **The four plot scripts are in neither `smoke_tests.txt` nor
  `smoke_notebooks.txt`**, so workspace CI never executes them. Verification came
  from rendering each script's exact kwarg list through the real
  `corner_cornerpy` locally. The gap is real and outlives this task.

## Verification limits

`pyauto-heart` was unavailable (web-github session, no PyAutoHeart checkout), so
the ship gate used the documented per-repo pytest fallback: **2089 passed, 36
skipped** on Python 3.12. Beyond the suite, figures were rendered against the
pinned `corner==2.2.2` and compared by RGBA buffer hash — `bins=5`,
`show_titles=True` and weighting each change the output; all-constant columns
still render. corner's signature was re-checked against 2.2.2 (the pin) as well
as 2.3.0; identical for every name involved.

One process note: two full pytest runs launched concurrently collided on the
shared `test_autofit/output/` directory and produced 5 and 7 phantom failures in
unrelated subtrees. A single serial run is green. Do not run this suite twice in
parallel in the same checkout.

## Sizing calibration

`pyauto-brain bug` and the sizing faculty both scored this **too-large (13)** and
advised phasing. Overridden deliberately at start_dev, and the override was
right: 613 insertions / 16 deletions across 11 library files plus 4 workspace
scripts and their notebooks, shipped as one coherent PR pair. The score inflates
on prompt word-count and the multi-repo flag; the prompt's own
`Difficulty: small` header was the better estimate.

## Original prompt

# `autofit.plot` functions accept `**kwargs` and silently discard them

Type: bug
Target: autofit
Repos:
- PyAutoFit
- autofit_workspace
Difficulty: small
Autonomy: supervised
Priority: normal
Status: formalised
Filed: 2026-08-07 (backfilled from git)
Issued: 2026-08-24

Filed 2026-08-07, found while fixing `docs/api/plot.rst`
(complete/2026/08/pyautofit_plot_rst_dead_plotters.md). Deliberately left out of
that PR: it is a library/workspace defect, not a docs one, and the docs change
was docs-only by design.

## The defect

All five public `autofit.plot` functions take `**kwargs` in their signature and
**never reference it in the body**. Verified mechanically — `kwargs` appears in
`autofit/non_linear/plot/{samples_plotters,nest_plotters,mle_plotters}.py` only
on the `def` lines:

- `corner_cornerpy(samples, path=None, filename="corner", format="show", **kwargs)`
- `corner_anesthetic(samples, path=None, filename="corner_anesthetic", format="show", **kwargs)`
- `subplot_parameters(...)`, `log_likelihood_vs_iteration(...)`,
  `figure_of_merit_vs_iteration(...)` — same shape

`corner_cornerpy` calls the underlying library with a **fixed** argument set:

```python
corner.corner(
    data=data,
    weight_list=samples.weight_list,
    labels=samples.model.parameter_labels_with_superscripts_latex,
    range=_corner_range_from(data),
)
```

So a caller's customization is accepted without error and has no effect. The
failure mode is the bad one: **silent**. No `TypeError`, no warning, just a plot
that ignores what you asked for.

## Why it matters — the workspace teaches the broken idiom

`autofit_workspace/scripts/plot/*.py` passes long kwarg lists as though they
were forwarded, and says so in prose: *"In all the examples below, we use the
`kwargs` of this function to pass in any of the input parameters that are
described in the API docs."* That claim is false today.

Silently-discarded kwargs at those call sites (counted 2026-08-07):

| script | discarded kwargs |
|---|---|
| `scripts/plot/emcee_plotter.py` | 30 |
| `scripts/plot/dynesty_plotter.py` | 19 |
| `scripts/plot/zeus_plotter.py` | 16 |
| `scripts/plot/nautilus_plotter.py` | 11 |
| **total** | **76** |

A user following the plot tutorials sets `bins`, `smooth`, `show_titles`,
`truths`, … and sees none of them applied. The tutorials are the documentation
for this API, so this is the primary way the behaviour is encountered.

## The decision to make (why supervised, not auto)

Two coherent fixes; picking one is a judgement about the intended surface:

1. **Forward them** — pass `**kwargs` through to `corner.corner` /
   `anesthetic` / matplotlib. Matches what the workspace already claims and
   makes the existing tutorials correct as written. Watch the collisions:
   `corner_cornerpy` already sets `data`, `weight_list`, `labels` and `range`
   explicitly, and `range` in particular is computed by `_corner_range_from`
   to dodge corner's "no dynamic range" crash on degenerate columns — a
   user-supplied `range` must not silently reintroduce that. Decide precedence
   (caller wins / library wins) and state it.
2. **Drop `**kwargs`** from the signatures and correct the workspace scripts +
   prose. Honest, and callers get a loud `TypeError` instead of silence — but
   it removes customization the tutorials imply exists, so it is the bigger
   user-facing change.

Either way the workspace scripts and their prose need updating in the same
wave, so this is a paired PyAutoFit + autofit_workspace task.

## Verify

- A call passing a non-default kwarg (e.g. `bins=5`) visibly changes the
  output figure (fix 1), or raises `TypeError` (fix 2).
- The four `scripts/plot/*.py` tutorials and their surrounding prose agree with
  whichever behaviour was chosen — no script still passes an argument that does
  nothing.
- Degenerate-column input (every sample equal, e.g. a `PYAUTO_TEST_MODE=1` run)
  still does not crash `corner`, i.e. the `_corner_range_from` guard survives.

<!-- Grounding: verified against PyAutoFit main at 75bbc76a1 by reading the
     three plot modules and counting kwargs at the workspace call sites. The
     docs page that surfaced it is docs/api/plot.rst, rewritten in PyAutoFit#1455. -->
