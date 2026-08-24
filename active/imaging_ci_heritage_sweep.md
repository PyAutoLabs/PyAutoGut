# Top-level `imaging_ci/` is pre-resurrection heritage the legacy sweep missed

Type: maintenance
Target: autocti_workspace_test
Repos:
- autocti_workspace_test
Difficulty: small
Autonomy: supervised
Priority: low
Status: formalised
Filed: 2026-08-24
Issued: 2026-08-24

Split out of `aplt-output-drift-remaining-repos` (PyAutoGalaxy#585, 2026-08-24),
which scoped `autocti_workspace_test` out rather than modernising code that
looks dead.

## The observation

`autocti_workspace_test` has a top-level `imaging_ci/` directory — 41 Python
files — that behaves in every observable way like the `legacy/` tree beside it,
but is not in it:

- **Not documented.** AGENTS.md's "Repository Structure" block lists `scripts/`,
  `legacy/`, `config/` and `smoke_tests.txt`. Top-level `imaging_ci/` appears
  nowhere in it.
- **Not exercised.** `smoke_tests.txt` lists three scripts
  (`dataset_1d/model_fit.py`, `imaging_ci/model_fit.py`, `plot/subplots.py`) —
  all of them under `scripts/`, none under top-level `imaging_ci/`. Nothing in
  CI touches it.
- **Not maintained since 2023.** Its substantive history is `2023-02-07 add all
  files` and `2023-02-13 temporal fit now runs`. Its only 2026 commits are
  repo-wide mechanical sweeps (`remove the Finished./Finish. notebook-generation
  crutch`, `remove legacy notebook bootstrap`) that also touched `legacy/`.
- **Broken against the current stack, in exactly the `legacy/` way.** 13 of its
  files call the removed plotter-object API — `ImagingCIPlotter`, `MatPlot2D`,
  `MatPlot1D`, `Output`, `Array2DPlotter`, `Cmap`, `Title`, `Axis` — none of
  which `autocti.plot` exports (its `__init__.py` is 49 lines of flat functions).
  `legacy/README.md` describes its own contents in the same terms: *"target the
  pre-2025 PyAutoCTI API (the removed Plotter object stack, analysis summing,
  etc.) and are not runnable against the current stack."*

`legacy/` was created on 2026-07-17 by *"CTI resurrection Phase 5: rebuild as a
modern integration-test suite (#1)"*, which swept the pre-resurrection contents
into it. The reading this prompt proposes: `imaging_ci/` is part of that same
heritage and the sweep simply missed it.

## Why it matters

`AGENTS.md:52` says *"Never edit `legacy/` — it is preserved Euclid VIS
history."* That rule protects the tree it names. Because `imaging_ci/` sits
outside it, an API-drift sweep reads those 13 files as live breakage and
"fixes" them — modernising dead code against no CI and no dataset. That is the
mistake PyAutoGalaxy#585 stopped one step short of making.

## What to decide

Confirm the reading before acting — the point of this prompt is the question,
not a foregone move. Check `imaging_ci/` against the CTI resurrection epic
(PyAutoCTI#82): is any of it slated for modernisation, or is it all superseded
by `scripts/`?

Then one of:

1. **`git mv imaging_ci/ legacy/imaging_ci/`** and extend `legacy/README.md` +
   AGENTS.md's structure block to cover it. Preserves the history, and puts it
   behind the never-edit rule where a future sweep will leave it alone.
2. **Condemn it** via the Gut's transit-and-void lifecycle (see PyAutoGut), if
   `legacy/` is meant to hold only the Euclid VIS material specifically and this
   is something else.
3. **Keep and modernise** — only if the epic actually wants these 13 files
   working. Then it is a real dev task, not maintenance, and wants its own
   prompt with a plan for validating them (no CI, no committed dataset).

Note `imaging_ci/profiling/` (17 files) and `imaging_ci/temporal/` are in the
directory too and are *not* part of the 13 broken ones — they need the same
decision but on their own evidence, not by association.

## Evidence to re-derive

```bash
git -C autocti_workspace_test log --format="%ad %s" --date=short -- imaging_ci | head
git -C autocti_workspace_test log --diff-filter=A --format="%ad %s" --date=short -- legacy/README.md
```

Alias-aware AST scan (resolve the plot alias from each file's own imports, then
diff attribute use against `autocti/plot/__init__.py`'s real export list) —
the scan written for PyAutoGalaxy#585 reports 31 broken files repo-wide,
18 under `legacy/` and 13 under top-level `imaging_ci/`.
