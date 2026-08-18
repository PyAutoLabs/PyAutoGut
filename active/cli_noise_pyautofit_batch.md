# PyAutoFit CLI-noise batch: unclosed search.log handler + four small warning fixes

Type: maintenance
Target: PyAutoFit
Repos:
- PyAutoFit
Difficulty: small
Autonomy: safe
Priority: normal
Status: formalised

Filed 2026-08-06 from a full `/cli_noise_clean` audit (full PyAutoFit suite,
1667 tests, `-W all`). Five mechanical fixes, all in PyAutoFit:

1. **Unclosed `search.log` FileHandler (44 warnings/run)** —
   `autofit/non_linear/search/abstract_search.py:123-131` (`configure_handler`)
   removes the handler in `finally` but never calls `handler.close()`. Add
   `handler.close()` beside `removeHandler` at line 131.
2. **SQLAlchemy `SAWarning` relationship overlap** — `Fit.arrays`/`Fit.hdus`
   vs `HDU.fit` ("will copy column fit.id ... conflicts"). Add the
   `overlaps="..."` parameters SQLAlchemy suggests, in the DB model
   definitions (fires from `configure_mappers()`, not the test).
3. **Nautilus deprecation** — `non_linear/search/nest/nautilus/search.py:535`
   uses `search_internal.evidence()`; swap to the `.log_z` property.
4. **scipy L-BFGS-B deprecation** — `non_linear/search/mle/bfgs/search.py:194`
   passes deprecated `disp`/`iprint` options; drop them per scipy's migration
   note (or gate on scipy version).
5. **fork() DeprecationWarning in `test_fork_context.py`** — pytest's thread
   pool + `os.fork()`; add a module-local `filterwarnings` mark or use the
   `spawn` context in that test where feasible.

Edge-case numerical warnings from tests that deliberately exercise degenerate
inputs (`LinAlgWarning`/`RuntimeWarning` in `interpolator/covariance.py`,
`messages/normal.py`, `fitness.py`) are lowest priority — silence locally in
the triggering tests with `warnings.catch_warnings()`, never globally.
