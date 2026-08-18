# cli-noise-pyautofit-batch

- shipped: 2026-08-18
- issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1495
- library-pr: https://github.com/PyAutoLabs/PyAutoFit/pull/1496 (`pending-release`) — MERGED 2026-08-18 as `7d4d931`, all 3 checks green (unittest 3.12 + 3.13, docs-build)
- repos:
  - PyAutoFit: `claude/pyautofit-cli-noise-fixes-vqs7mg` → `7d1fe19`
- session: Claude Code web (remote); no local worktree

## Summary

The five mechanical fixes from the 2026-08-06 `-W all` CLI-noise audit, in one
PyAutoFit PR (6 files, +42/−5). Each warning was reproduced on `main` first and
shown gone after the fix; full suite on py3.13 + scipy 1.17.1: 1884 passed,
3 skipped.

1. `configure_handler` (`abstract_search.py`) now calls `handler.close()`
   beside `removeHandler` in its `finally` — ends the 44-per-run
   `ResourceWarning` and file-descriptor leak from `search.log`.
2. `Fit.arrays` carries `overlaps="fit"`, `Fit.hdus` carries
   `overlaps="arrays,fit"` (`database/model/fit.py`) — the exact strings
   SQLAlchemy 2.0.52's two `SAWarning`s suggest; `configure_mappers()` is now
   silent.
3. Nautilus `samples_info_from` reads `.log_z` instead of the deprecated
   `evidence()` (nautilus 1.0.5's method is a warn-then-`return self.log_z`
   wrapper — exactly equivalent).
4. `LBFGS.options` drops the `disp`/`iprint` keys scipy 1.15 deprecated for
   L-BFGS-B (removal slated 1.18); constructor still accepts both, `disp`
   stays live for plain `BFGS`; `test_lbfgs.py` pins the contract.
5. `test_fork_context.py` filters both fork warnings module-locally —
   CPython 3.12+'s DeprecationWarning *and* JAX's equivalent RuntimeWarning.

## Traps / findings

- **JAX adds a second fork warning.** Once JAX is imported it registers its own
  `os.fork()` RuntimeWarning hook, so a filter for CPython's DeprecationWarning
  alone leaves the module noisy in JAX-enabled runs. Both are needed; the
  regexes differ (`This process` vs `os\.fork\(\) was called`).
- **SQLAlchemy names the fix for you.** The `SAWarning` text contains the exact
  `overlaps="..."` string per relationship — reproduce with
  `sa.orm.configure_mappers()` under `warnings.catch_warnings(record=True)` and
  copy it verbatim rather than deriving the overlap set by hand.
- **Prompt line numbers drift.** The prompt's `bfgs/search.py:194` (filed
  2026-08-06) no longer matched; the sites were re-located by symbol
  (`options` property / `samples_info_from`), not by line.
- Out of scope, still open on `main`: fork warnings from the dynesty pool tests
  elsewhere in `test_autofit/non_linear/search/`, and the deliberately
  degenerate-input numerical warnings (`interpolator/covariance.py`,
  `messages/normal.py`, `fitness.py`) the prompt marked lowest priority.

## Workflow notes

- Remote web session: `pyauto-heart` unavailable, so the ship gate ran as the
  WORKFLOW.md fallback (full repo suite as the verdict); vitals faculty not
  consultable — noted here rather than silently skipped.
- Deliberate conflict override (file-disjoint) with the two in-flight PyAutoFit
  claims `stored-sample-reconstruction-guard` and `version-stamp-sync-guards`,
  documented in the `active.md` entry at registration.
- No workspace impact: API changes "None — internal"; no workspace migration
  needed (option iii).

## Original prompt

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
