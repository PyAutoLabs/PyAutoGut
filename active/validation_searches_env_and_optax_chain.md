# workspace-validation red: missing ENV declarations + optax/blackjax never installed

Type: bug
Target: autofit
Repos:
- @autofit_workspace_test
- @PyAutoGalaxy
- @PyAutoHeart
Difficulty: easy
Autonomy: supervised
Priority: high
Status: draft

## Original Request

> can we sequentially tackle everything in 3 overnight jobs red

(from the 2026-07-27 `/wake_up` digest; this is the first of the three.)

## Symptom

`PyAutoHeart/workspace-validation` has been red since 2026-07-26. The failing
shard is `run_scripts (3.12, autofit_test, searches)`:

```
scripts/searches/BlackJAXNUTS.py        FAIL  ModuleNotFoundError: No module named 'blackjax'
scripts/searches/MultiStartAdam.py      FAIL  ImportError: requires optional `jax` and `optax`
scripts/searches/MultiStartProdigy.py   FAIL  AssertionError: 1.0
scripts/searches/MultiStartResurrect.py FAIL  KeyError: 'n_resurrections'
```

Two independent root causes, confirmed by local reproduction.

## Cause (a) — two scripts have no `__Env__` declaration

`MultiStartProdigy.py` and `MultiStartResurrect.py` carry **no** `__Env__` /
`ENV:` section, so they inherit the smoke-profile defaults
`PYAUTO_TEST_MODE=2` + `PYAUTO_DISABLE_JAX=1` and run the *bypass* path
instead of a real JAX search.

Reproduced locally — byte-identical to CI:

```bash
PYAUTO_TEST_MODE=2 PYAUTO_DISABLE_JAX=1 python3 scripts/searches/MultiStartProdigy.py
#   Recovered: centre=50.000, normalization=1.000, sigma=15.000
#   AssertionError: 1.0
```

`1.0` is the `LogUniform(1e-2, 1e2)` midpoint the bypass returns for
`normalization` (truth is 25.0); `n_resurrections` is absent because the bypass
never builds a `search_internal`. Both scripts **pass** on a normal run.

This is fallout from the #187/#189 ENV migration (2026-07-23), which named only
their two siblings (`MultiStartAdam`, `BlackJAXNUTS`) and missed these two.

**Fix:** append an `__Env__` section carrying `ENV: real_search jax` to the end
of each script's module docstring, mirroring `MultiStartAdam.py:24-30` exactly
(column-0 header, one `ENV:` line, no leading `#` — the legacy comment form now
raises, `PyAutoHands/autohands/env_config.py:82-92`). The tokens release
`PYAUTO_TEST_MODE` and `PYAUTO_DISABLE_JAX` respectively
(`env_config.py:43-54`).

**Also audit (report, do not silently fix):** `Nautilus_jax.py` and
`Dynesty_jax.py` use JAX with no declaration too. They don't fail — no
truth-recovery assert — but they are therefore running the **numpy** path under
smoke, i.e. contributing zero JAX coverage. Report and recommend; the remaining
searches scripts are numpy-only and correctly need nothing.

## Cause (b) — the validation env never installs optax or blackjax

The smoke leg installs `autolens[optional]`. The extras chain is

```
autolens[optional] -> autolens[jax] -> autogalaxy[jax] -> autonerves[jax]
```

which stops at jax/jaxlib/jaxnnls. It never reaches `autofit[jax]`
(`optax>=0.2.5`) or `autofit[optional]` (`blackjax>=1.2.0`).

`optax` missing from the `jax` chain is a **user-facing packaging gap**, not just
a CI one: `pip install autolens[jax]` today does not get optax, so
`af.MultiStartAdam` / `af.MultiStartProdigy` raise ImportError for users.

**Fix (two parts):**

1. `PyAutoGalaxy/pyproject.toml` `jax` extra: `"autonerves[jax]"` ->
   `"autofit[jax]"`. Strictly additive (`autofit[jax]` already includes
   `autonerves[jax]`), and PyAutoGalaxy already depends on `autofit`
   (`pyproject.toml:29`), so no new dependency edge. `autolens[jax]` inherits it.
2. `PyAutoHeart/.github/workflows/workspace-validation.yml`, **smoke** install
   step (~236-248): add `pip install "autofit[optional]"` for blackjax, with a
   comment matching the existing `nufftax` precedent immediately above it.
   `mode=release` already installs `autofit[optional]==$TESTPYPI_VERSION`, so
   only the smoke leg changes.

## Verification

- Re-run both scripts under the exact smoke defaults above — they must now run
  the real JAX search and pass.
- `PyAutoHands/autohands/validate_env_profiles.py` reports both scripts as
  declared, and the **resolved-env diff** shows the two vars released for them
  and unchanged for every other script (config changes are verified by
  resolved-env diff, not smoke alone).
- Scratch venv: `pip install -e PyAutoGalaxy[jax]` then `import optax`.
- `workspace-validation` green on the next scheduled run (read the verdict via
  the Actions API — `gh pr checks` is unparseable on this `gh` build). Do **not**
  hand-dispatch the nightly release.

## Notes

- **Brain phase-split overridden.** `pyauto-brain feature` scored this
  `too-large (score 20)` and proposed a 4-phase split (design / core-api /
  workspace / docs). That score is driven by the repo *count* (4), not the
  change size: the total diff is two docstring sections, one `pyproject.toml`
  line, and one `pip install` line. There is no API change and no public-API
  ripple, so the "library/workspace coordination" and "too large for one PR"
  risks it flagged do not apply. Kept as a single easy task; one PR per repo.
- The morning digest first attributed these to the MultiStart cadence PRs
  (#1421/#1423). That was wrong — they merged 2026-07-27 16:00 BST, ~10h *after*
  the 06:15 failing run.
- Do not "fix" BlackJAXNUTS by deleting it or dropping blackjax — blackjax is a
  kept dependency.
