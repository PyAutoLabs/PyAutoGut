# Unguarded LinAlgError in inversion CSV export (`inversion_plots.py` second call site)

Type: bug
Target: autoarray
Repos:
- @PyAutoArray
Difficulty: easy
Autonomy: supervised
Priority: normal
Status: draft

## Context

PyAutoArray#405 (2026-07-25) fixed the nightly-validation flake where
`reconstruction_noise_map_dict[mapper]` → `np.sqrt(np.linalg.inv(curvature_reg_matrix))`
raises `numpy.linalg.LinAlgError: Singular matrix` on the rank-deficient
curvature matrices that reduced-iteration test profiles routinely produce
(`PYAUTO_TEST_MODE=1` + `PYAUTO_SMALL_DATASETS=1`; measured 784×784 rank 426).
The fix widened the noise-map *subplot panel's* existing best-effort guard
(`except (KeyError, TypeError)` — which `LinAlgError`, a `ValueError` subclass,
escaped) to include `np.linalg.LinAlgError`.

## The remaining call site

`autoarray/inversion/plot/inversion_plots.py:386` (post-#405 numbering may
shift) also reads `reconstruction_noise_map_dict[mapper]`, inside the **CSV
export** function, with **no try/except at all**. On the same rank-deficient
input it raises the same `LinAlgError` and kills the enclosing fit.

This was deliberately left out of #405: a CSV export is not an optional
diagnostic panel, so silently emitting a file with a missing column may be the
wrong remedy. The right handling needs a decision:

- skip the noise-map column with a logged warning?
- write NaNs for that column?
- catch-and-skip like the panel (accepting a silently incomplete CSV)?
- or compute a pseudo-inverse fallback for output-only purposes?

## Acceptance

- A deliberate, documented behaviour for the CSV export when
  `curvature_reg_matrix` is singular; no path by which `LinAlgError` from this
  call site can abort a model-fit.
- Regression test mirroring
  `test_inversion_plotters.py::test__inversion_subplot_of_mapper__singular_curvature_reg_matrix`
  (monkeypatch `reconstruction_noise_map_with_covariance` to invert a singular
  matrix).
