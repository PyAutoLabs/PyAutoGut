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
