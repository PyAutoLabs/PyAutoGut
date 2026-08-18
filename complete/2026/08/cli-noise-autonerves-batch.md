# cli-noise-autonerves-batch

**Completed:** 2026-08-18 · **Type:** maintenance · **Target:** PyAutoNerves
**PRs:** PyAutoNerves#149 (fixes), PyAutoMind#232 (implementation notes) — both
merged 2026-08-18. No GitHub issue (small `Autonomy: safe` batch, driven
straight from the draft prompt in a remote session).

## What shipped

The three autonerves-rooted CLI-noise sources from the 2026-08-06
`/cli_noise_clean` audit, all fixed in one PyAutoNerves PR with regression
tests:

1. **fits leak** — `fitsable.ndarray_via_fits_from` called `fits.open` without
   closing, emitting `ResourceWarning: unclosed file` in every downstream repo
   that loads FITS. Now `with fits.open(...)`. The same fix was applied to
   `header_obj_from`, which had the identical unclosed-handle pattern a few
   lines below the one the audit named — an astropy `Header` stays valid after
   the file closes, so the `with` block is safe there too.
2. **pytest collection** — `test_test_mode.py` imported the real API functions
   `test_mode_level`/`test_mode_samples` by bare name, so pytest collected them
   as tests (`PytestReturnNotNoneWarning`, an ERROR in a future pytest). The
   unused `test_mode_level` import was dropped; `test_mode_samples` is aliased
   to `_test_mode_samples`, with a comment so nobody "cleans up" the alias.
3. **`check_version` false positive** — fix option (b) from the prompt:
   `check_version` now returns silently when its root (defaulting to cwd) is a
   package source checkout (`setup.py` or `pyproject.toml` at its top level)
   and no version floor is recorded. A recorded floor is still enforced even in
   a source checkout, and a genuine workspace missing its version keys still
   warns. Chosen over option (a) (per-library conftest env vars) because it is
   self-contained in autonerves — no changes needed in the five library repos.

Full `test_autonerves` suite green (157/157) under `pytest -W all`; verified
`check_version()` is silent with cwd at a library repo root and that
`test_mode_*` no longer appear in `pytest --collect-only`.

## Surface decision (the prompt's item-3 open question)

The prompt flagged that PyAutoArray/PyAutoNerves don't call `check_version` at
all, unlike autofit/autogalaxy/autolens. Decided: **the asymmetry is intended,
not drift.** `check_version` is the surface of the *workspace-facing* libraries
only — users run scripts from workspace clones that import those three.
autoarray and autonerves are infrastructure layers never driven from a
workspace cwd directly. No library `__init__` was changed.

## Traps / findings

- The audit named one leak site (`fitsable.py:210`); the sibling
  `header_obj_from` had the same leak and would have kept a residual
  ResourceWarning trickle if only the named line were fixed. When fixing a
  pattern-shaped noise source, grep the module for the pattern, not the line.
- The downstream ResourceWarning surfaces the audit lists
  (`autofit/database/aggregator/scrape.py`, `autoarray` visibilities /
  interferometer dataset, Galaxy/Lens runs) all route through these two
  helpers, so no downstream-repo changes are needed — re-run the audit after
  the next release picks up autonerves to confirm the stack-wide clearance.

## Original prompt

# Silence the three autonerves-rooted CLI-noise sources (fits leak, pytest collection, check_version false positive)

Type: maintenance
Target: PyAutoNerves
Repos:
- PyAutoNerves
Difficulty: small
Autonomy: safe
Priority: normal
Status: implemented — fixes pushed to PyAutoNerves branch
`claude/autonerves-cli-noise-h1w8sq` (2026-08-18), awaiting PR/merge

Filed 2026-08-06 from a full `/cli_noise_clean` audit (pytest `-W all` across
all five libraries + workspace script runs). Three root causes live in
autonerves; the first pollutes the entire downstream stack.

1. **Unclosed `fits.open` in `autonerves/fitsable.py:210`** — `fits.open` is
   called without `with`/close, emitting `ResourceWarning: unclosed file` in
   every repo that loads FITS via `ndarray_via_fits_from` (surfaces at
   `autofit/database/aggregator/scrape.py:187`,
   `autoarray/structures/visibilities.py:179` ×10,
   `autoarray/dataset/interferometer/dataset.py:198` ×4, and throughout
   Galaxy/Lens runs). Fix: `with fits.open(...) as hdu_list: return
   ndarray_via_hdu_from(hdu_list[hdu])`. One upstream fix clears the majority
   of ResourceWarning noise stack-wide.
2. **`test_mode_level`/`test_mode_samples` collected as pytest tests** —
   `autonerves/test_mode.py:5,24` are real API functions, but
   `test_autonerves/test_test_mode.py:11-16` imports them by bare name, so
   pytest collects them (`PytestReturnNotNoneWarning`, becomes an ERROR in a
   future pytest). Fix: alias the imports (`... as _test_mode_level`) or import
   the module and call qualified.
3. **`check_version` UserWarning on every library import from a source repo** —
   `autonerves/workspace.py:206` (default `workspace_root=Path.cwd()`) is
   called unconditionally by `autofit/autogalaxy/autolens.__init__`, and fires
   "Cannot verify the workspace ... is compatible" whenever cwd lacks
   `config/general.yaml` — always true in the libraries' own repos, so every
   pytest run/collection emits it. Fix options: (a) each library's
   `test_<pkg>/conftest.py` sets `PYAUTO_SKIP_WORKSPACE_VERSION_CHECK=1`, or
   (b) `check_version` detects it is running from inside a library source tree
   and skips. Note PyAutoArray/PyAutoNerves don't call `check_version` at all —
   inconsistent with the other three; decide the intended surface while here.

## Implementation notes (2026-08-18, branch `claude/autonerves-cli-noise-h1w8sq`)

- **1 (fits leak)**: fixed with `with fits.open(...)` in
  `ndarray_via_fits_from` **and** `header_obj_from`, which had the identical
  unclosed-handle pattern. Regression test asserts no `ResourceWarning`.
- **2 (pytest collection)**: dropped the unused bare-name `test_mode_level`
  import; aliased `test_mode_samples as _test_mode_samples` with a comment
  explaining why, so collection skips it.
- **3 (check_version false positive)**: chose fix (b) — `check_version` now
  skips silently when the root is a package source checkout (`setup.py` or
  `pyproject.toml` at its top level) and no version floor is recorded. A
  recorded floor is still enforced even in a source checkout, and a genuine
  workspace missing its version keys still warns. Self-contained in
  autonerves; no per-library conftest changes needed.
- **Surface decision** (the item-3 note): `check_version` is intentionally the
  surface of the *workspace-facing* libraries only (autofit / autogalaxy /
  autolens import it at package init because users run their scripts from
  workspace clones). autoarray and autonerves are infrastructure layers never
  driven from a workspace cwd directly, so they correctly do not call it — the
  asymmetry is intended, not drift. No change made to any library `__init__`.
