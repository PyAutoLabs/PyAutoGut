- issue: https://github.com/PyAutoLabs/autofit_workspace_test/issues/77
- prs: autofit_workspace_test#78 + PyAutoGalaxy#530 + PyAutoHeart#111 — ALL MERGED
- summary: |
    PyAutoHeart/workspace-validation red since 2026-07-26 on the
    run_scripts (3.12, autofit_test, searches) shard — 4 failures, TWO
    independent causes, both confirmed by local reproduction.

    (a) MultiStartProdigy.py + MultiStartResurrect.py carried no __Env__
    declaration, so they inherited the smoke defaults PYAUTO_TEST_MODE=2 +
    PYAUTO_DISABLE_JAX=1 and ran the BYPASS path. Bypass returns prior
    midpoints, so Prodigy's truth assert saw normalization=1.0 (the
    LogUniform(1e-2,1e2) midpoint, truth 25.0) -> "AssertionError: 1.0", and
    Resurrect's samples_info had no n_resurrections (bypass builds no
    search_internal) -> KeyError. Missed by the #187/#189 ENV migration, which
    declared only the two siblings (MultiStartAdam, BlackJAXNUTS).

    (b) The smoke leg installs autolens[optional], whose extras chain is
    autolens[jax] -> autogalaxy[jax] -> autonerves[jax]. It never reaches
    autofit[jax] (optax) or autofit[optional] (blackjax). optax missing from
    the jax chain was a REAL USER-FACING GAP: `pip install autolens[jax]` did
    not get optax, so af.MultiStartAdam/MultiStartProdigy raised ImportError.
    Fixed at the chain (autogalaxy[jax] -> autofit[jax], strictly additive) and
    in the workflow (explicit autofit[optional] for blackjax, mirroring the
    existing nufftax precedent; mode=release already had it).

    Also corrected a stale docstring API reference caught by the PyAuto API
    gate: AbstractMultiStartGradient is the shared base class, not an af.*
    export.
- verification: |
    Resolved-env diff across all 63 scripts: exactly 2 changed, each releasing
    only PYAUTO_TEST_MODE + PYAUTO_DISABLE_JAX; the other 61 byte-identical.
    (Config changes are verified by resolved-env diff, not smoke alone.)
    Both scripts then ran the real JAX search and passed. PyAutoGalaxy built
    wheel metadata: `Requires-Dist: autofit[jax]; extra == "jax"`.
- traps: |
    TRAP: the morning /wake_up digest attributed these to the MultiStart cadence
    PRs (#1421/#1423). WRONG — those merged 16:00 BST, ~10h AFTER the 06:15
    failing run. Always check merge timestamps against the run timestamp before
    attributing a CI failure to a recent merge.
    TRAP: Brain scored this too-large (20) and proposed a 4-phase split. That
    score tracks REPO COUNT (4), not change size — the real diff was two
    docstring sections and two one-liners. Override recorded in the prompt.
    OPEN: Nautilus_jax.py / Dynesty_jax.py also lack declarations. They do not
    fail (no truth assert) but analysis.py:68 silently forces use_jax=False, so
    they are duplicate numpy runs contributing ZERO JAX coverage. Reported on
    issue #77, not fixed.
