Repaired the `aplt.Output` stale-API drift in the last two repos the
2026-08-04 `plot-array-stale-kwargs` task deliberately stopped short of — and
found that the drift's real shape was not what the prompt described.

## Outcome

| Repo | PR | Merged |
|---|---|---|
| PyAutoGalaxy | [#586](https://github.com/PyAutoLabs/PyAutoGalaxy/pull/586) | `d68a8f6` |
| euclid_strong_lens_modeling_pipeline | [#39](https://github.com/PyAutoLabs/euclid_strong_lens_modeling_pipeline/pull/39) | `62b2fd4` |

Classification changed during planning from workspace-only to **library +
workspace**, which is why a PyAutoGalaxy PR exists at all.

## The prompt was wrong in three ways, each found by verifying rather than trusting

**1. `autocti_workspace_test` is out of scope — the hedge resolved, then the
scope collapsed.** The prompt flagged 27 files as "UNVERIFIED — check first",
suspecting PyAutoCTI might still export `Output`. It does not:
`autocti/plot/__init__.py` is 49 lines of flat functions. So those files are
genuinely broken — but an alias-aware scan found **31**, not 27, and:

- **18 are under `legacy/`**, which `autocti_workspace_test/AGENTS.md:52`
  forbids editing ("preserved Euclid VIS history"). Its README says outright
  that they target the removed Plotter object stack and are not runnable.
- **13 are top-level `imaging_ci/`** — undocumented in AGENTS.md's structure
  block, absent from `smoke_tests.txt`, substantive history **2023-02**, the
  same era as `legacy/` (created 2026-07-17 by "CTI resurrection Phase 5").
  Its only 2026 commits are repo-wide mechanical sweeps that also hit `legacy/`.

Following the prompt literally would have modernised dead code *and* violated
the repo's own hard rule. Filed as
`draft/maintenance/autocti_workspace_test/imaging_ci_heritage_sweep.md` for a
human decision against the CTI resurrection epic (PyAutoCTI#82).

**2. The drift was never really about `Output`.** The whole plotter-object stack
is gone from every public namespace — `MatPlot2D`, `MatPlot1D`, `Cmap`,
`Array2DPlotter`, `Visuals2D`, `MassProfileCentresScatter`, the `*Plotter`
family. `Output` was 6 of 13 missing symbols in autocti, 2 of 6 in euclid.

**3. Two library defects the prompt never mentioned.** `Cmap` is exported by
**no** public plot namespace, yet:

- `Scribbler.__init__` required a `Cmap`-shaped object for `cmap=`, so callers
  had no public way to colour the GUI.
- `Clicker.start()` built `aplt.Cmap(...)` on `autoarray.plot`
  *unconditionally* — reproduced on the installed stack as
  `AttributeError: module 'autoarray.plot' has no attribute 'Cmap'`. That GUI
  was dead for every caller.

Fixed library-side because the only workspace alternative was a private-path
import — the "autoimmune reaction" the Bug Agent's fix-locus rule warns against.

## The plan's worst assumption, caught before it shipped

The approved plan said euclid's explicit `mask=` could simply drop out, since
`plot_array` auto-derives the outline. It cannot. `data` there comes from
`Array2D.from_fits` and is **unmasked**, so `auto_mask_edge(data)` returns
`None` — verified directly. Worse, the mask being drawn is a *separately
constructed* circular one whose radius is grown at line 160 to enclose the
clicked galaxies, so it is the entire subject of the figure.

A literal reading would have silently deleted the mask radius from the PNG that
exists to show it, and nothing would have failed. Fixing it needed a second
library change: autogalaxy's `plot_array` wrapper delegates to autoarray's but
was dropping its `mask=` parameter.

## Verification

- PyAutoGalaxy CI green on **every leg**: `unittest (3.12)`, `unittest (3.13)`,
  `unittest-nojax`, Docs. 1129 tests, 16 new across two files (`test_autogalaxy/gui/`
  did not previously exist).
- Alias-aware AST re-scan — aliases resolved from each file's own imports, the
  correction carried forward from HowToGalaxy#56 — **0 residual stale symbols**
  in both repos.
- All 10 changed `aplt.*`/`al.*` calls bound against real signatures: 10 ok, 0 failures.
- Mask passthrough verified by **rendering**: 2436 pixels differ vs. the same
  call without `mask=`, confirmed by pixel diff rather than file size.
- `compileall` clean; CRLF preserved uniformly (see below).

## Not verified, stated plainly

- **The two euclid GUIs were never run end-to-end.** They need TkAgg and FITS
  data absent from the repo, and euclid has **no CI workflows at all**. The
  merge was made with that stated and acknowledged.
- **`Scribbler.__init__` has no direct test** — `matplotlib.use("TkAgg")` and
  `wm_geometry` cannot run headless. The extracted `norm_from` helper carries
  the logic and is fully tested; the constructor is covered only by binding.

## Behaviour change accepted

Extra-galaxy centre markers were cyan via `MassProfileCentresScatter(c="cy")`
and are now the `plot_array` default. `autoarray/plot/array.py:258-262`
hardcodes the overlay colour cycle, and `line_colors` (265-273) applies to
`lines`, not `positions` — an early misreading of mine, corrected before it
reached the code. Restoring the colour needs a PyAutoArray change; markers
remain visible and distinguishable from the mask outline by size and z-order.

## Process note

An intermediate "suite green" reading was wrong twice and caught both times:
pytest had exited 4 on an unrecognised `--timeout` flag without running, and a
later run was corrupted when a `git stash` reverted the tree mid-run. Reported
results come from clean runs on the final tree. Separately, a stop-hook flagged
the PyAutoGalaxy branch as unpushed: the commit *was* on GitHub, but the
`--depth 1` clone's single-branch refspec meant no remote-tracking ref existed,
so `@{u}` could not resolve — repaired by widening the refspec.

## Follow-ups filed, not fixed

- `draft/maintenance/autocti_workspace_test/imaging_ci_heritage_sweep.md` — the
  13 heritage files the `legacy/` sweep missed.
- `autoarray` duplicates this normalisation inline in `plot/array.py` and
  `plot/inversion.py`; a shared helper there is the real fix. This task added
  one copy in autogalaxy serving both GUIs rather than a third inline copy.
- euclid's three `tools/` files are **100% CRLF on `main`**, contradicting its
  own AGENTS.md ("CRLF will break shell scripts on the HPC"). Preserved rather
  than converted, to avoid whole-file diffs that would not fix the repo-wide
  problem.

## Original prompt

# `aplt.Output` stale-API drift in the remaining workspace repos

Type: bug
Target: workspaces
Repos:
- autocti_workspace_test
- euclid_strong_lens_modeling_pipeline
Difficulty: small
Autonomy: supervised
Priority: normal
Status: formalised
Filed: 2026-08-04 (backfilled from git)
Issued: 2026-08-24

Split out of `plot-array-stale-kwargs` (HowToGalaxy#56, 2026-08-04), which
repaired this same drift in `autolens_workspace_developer` but deliberately
stopped at that repo's boundary.

## The drift

`aplt.Output` no longer exists on the **autolens / autogalaxy** plot namespace —
verified: `hasattr(autolens.plot, "Output") == False`. It survives only as
`autoarray.plot.Output`. The removal was deliberate and is already documented in
`autolens_assistant/AGENTS.md:218` ("the `aplt.MatPlot2D` / `aplt.Output` objects
have been removed — do not use them").

Callers must move to the flat convention. Note the accepted kwargs differ per
callee — check each signature rather than blanket-renaming:

```python
# plot_array takes all three
aplt.plot_array(array=..., output_path=P, output_filename=F, output_format="png")
# subplot_* take only path + format (no output_filename)
aplt.subplot_tracer(tracer=..., grid=..., output_path=P, output_format="png")
```

## Sites

| Repo | Files | Status |
|------|-------|--------|
| `autocti_workspace_test` | 27 | **UNVERIFIED — check first** |
| `euclid_strong_lens_modeling_pipeline/tools/` | 2 (`psf_size.py`, `extra_galaxies_centres_gui.py`) | confirmed broken |

**Do not assume the autocti files are broken.** Those import
`import autocti.plot as aplt` — a *different* library's plot namespace.
`autocti` was not installed in the 2026-08-04 session so it could not be
checked. PyAutoCTI may still export `Output`, in which case those 27 files are
correct as written and must be left alone. Verify with
`hasattr(autocti.plot, "Output")` before touching anything.

Confirmed **not** bugs, do not "fix" them:
- `PyAutoArray/test_autoarray/plot/test_output.py` — there `aplt` *is*
  `autoarray.plot`, which does export `Output`.
- `autolens_assistant` markdown — documents the removal.

## Verification

Re-run an alias-aware AST scan after the fix (the 2026-08-04 session's first
sweep hardcoded the alias `aplt` and **missed** a call site written as `aaplt`;
resolve aliases from each file's own imports). Then bind each changed call's
kwargs against the real callee signature via `inspect.signature`, since these
repos have little or no CI to catch a wrong kwarg name.
