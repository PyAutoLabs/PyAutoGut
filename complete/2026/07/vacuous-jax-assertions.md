## vacuous-jax-assertions (four workspace_test scripts validated numpy while presenting as JAX — SHIPPED)
- issue: https://github.com/PyAutoLabs/autolens_workspace_test/issues/229 (CLOSED)
- pr: autolens_workspace_test#230 + autogalaxy_workspace_test#99 — both MERGED
- completed: 2026-07-28
- type: test · repos: autolens_workspace_test, autogalaxy_workspace_test

### Summary

Closing follow-up to **PyAutoFit#1372**. Four scripts passed `use_jax=True` to an
analysis but resolved `PYAUTO_DISABLE_JAX=1` under the release profile, so they
validated the **numpy** path while presenting as JAX tests. Two distinct defects,
two different fixes:

- **Case A — genuinely vacuous.** `misc/latent/latent_nan_robustness.py` (both repos)
  deliberately builds *both* a numpy and a JAX analysis to contrast them, but declared
  no `__Env__` section, so both halves ran numpy. Renamed → `latent_nan_robustness_jax.py`
  so `derive_jax_markers` turns JAX on under release.
- **Case B — redundant kwarg.** `imaging/visualization/visualization.py` (both repos):
  `ag.*`/`al.*` analyses already default `use_jax=True`, so the explicit kwarg is a
  **no-op in every environment**. Dropped. The autogalaxy copy additionally labelled a
  likelihood-sanity assertion `"JAX/{source_name}"` while running numpy — label removed.

### KEY LESSON — the naming marker, NOT an in-file `ENV: jax` declaration

`ENV: jax` was the plan of record and was **wrong**; the human caught it by asking
whether the jax-in-filename rule should be used instead. Three independent reasons,
all verified in `PyAutoHands/autohands/`:

1. A declaration is **profile-agnostic**. Neither repo's `profile_smoke.yaml` sets
   `derive_jax_markers`, so a declaration flips JAX on under **smoke** too — and both
   scripts are in `smoke_tests.txt`, i.e. the per-PR gate. The *name* marker is
   profile-aware: JAX under release, numpy under smoke. This is the whole point.
2. `validate_env_profiles.py:152-161` names the exact move: unsetting
   `PYAUTO_DISABLE_JAX` on a **non-jax-marked** script "is NOT migratable — a `jax`
   declaration is profile-agnostic, so on a non-marked script it would flip the release
   resolution `1` -> absent (numpy -> JAX), a real behaviour change outside the verified
   `0` -> absent equivalence class."
3. It would **evade the marker audit** at `validate_env_profiles.py:190-198`, which
   tests `disabled == "0"` — a declaration *pops* the var, so it resolves to **absent**,
   not `"0"`. Silently unaudited: the exact silent-rot failure mode the derivation replaced.

`validate_env_profiles.py:138-145` separately forbids a release-profile override touching
`PYAUTO_DISABLE_JAX`. So in a release profile **the filename is the only sanctioned lever**.

### Findings

- **The JAX path had never run.** Post-rename the release log emits `JAX: Applying
  per-sample jit to latent variables (LATENT_BATCH_MODE='jit')` for the first time. Both
  scripts pass — no hidden bug, matching the autofit_workspace_test precedent in
  [[release-profile-jax-default]].
- **The validator is blind to this class**, before and after: `--strict-markers` is green
  on `main` in both repos. It audits *env resolution vs marker*, never `use_jax=True` in
  source, so "asks for JAX, silently gets numpy" is invisible. Possible hardening: flag a
  script whose source contains `use_jax=True` while resolving `PYAUTO_DISABLE_JAX=1` —
  needs the ~2 `SimulatorImaging` false positives handled first. NOT done.
- **The 300s cap is a smoke-only cap.** The autolens script runs 428.8s with JAX on, but
  `main` was **already 324.2s** without it. `mode=release` sets `BUILD_SCRIPT_TIMEOUT: "1800"`
  (PyAutoHeart `workspace-validation.yml:315`); the 300s default governs smoke. No `SLOW`
  marker needed — check which cap applies before treating a duration as a regression.
- **`use_jax=True` is a no-op in ag/al**, which default it `True`. Writing it explicitly
  signals an intent the script may not carry out — the misleading-but-inert case that made
  Case B look worse than it was.

### PyAutoFit#1372 closed alongside

Its library finding (`al.AnalysisDataset` read `PYAUTO_DISABLE_JAX` *before*
`super().__init__()`) was already fixed by `PyAutoLens@83016c1ea` "PYAUTO_DISABLE_JAX has
exactly one reader" (merged 2026-07-23, under an unrelated campaign), implemented exactly
as #1372 prescribed — forwarding `self._use_jax` after `super().__init__()` rather than
deleting the branch. It also fixed a live bug #1372 missed: `AnalysisPoint`/`AnalysisWeak`
*undid* the env downgrade (base set False, `AnalysisLens` overwrote True). The env var now
has exactly one reader across all five libraries.

Its second proposal — a `use_jax: Optional[bool] = None` sentinel threaded through af/ag/al
— was closed **won't-do**: its only consumer was the warning that #1372's own adversarial
review had already killed. The residual default asymmetry (`af`=False, `ag`/`al`=True) is
deliberate: PyAutoFit is generic and JAX-optional, the science layers are JAX-native.

### Blast radius (measured with `build_env_for_script`, not by eye)

| repo | `use_jax=True` | JAX OFF before | JAX OFF after |
|---|---|---|---|
| autofit_workspace_test | 10 | 0 | 0 |
| autolens_workspace_test | 55 | 4 | 2 (both `simulator_use_jax_parity` false positives) |
| autogalaxy_workspace_test | 36 | 2 | 0 |

`simulator_use_jax_parity.py` uses `SimulatorImaging`, which does not read the env var —
a genuine false positive of any naive `use_jax=True` string rule.

### Still open (deliberately unrecorded — human declined to file it)

Whether it is intended that `mode=release` validates the **numpy** path for most of the
autolens/autogalaxy surface. [[release-profile-jax-default]] flags "DO NOT COPY" its
`PYAUTO_DISABLE_JAX: "0"` flip here — ag/al analyses default `use_jax=True`, so flipping
the profile default is a real behaviour change across the whole surface, unlike in
autofit_workspace_test where it was a no-op for ~35 of 42 scripts. This task kept the
default at `"1"` and opted in one script. That record also claims a research brief was
filed at `draft/research/workspaces/env_profile_and_validation_gate_redesign.md` — **it does
not exist**. Human's call: "we'll get there eventually", so it stays unfiled.

### Gotchas

- Heart was YELLOW at ship; all four reasons pre-existing and unrelated (workspace
  validation 13 failed 2026-07-21; 33 stale parked scripts; tenant-firewall manifest drift;
  release validation stale). Human-acknowledged.
- The Brain Feature Agent scored this **large / score 8 / "re-home as research"**. Overridden
  to small — it scored the prompt's investigative prose and the explicitly out-of-scope
  research question recorded inside it, not the work (4 files, ~6 lines, 2 renames). Same
  family as [[feedback_brain_repo_count_difficulty_proxy]].
- `validate_env_profiles.py` uses a flat `from env_config import …`, so it must be run as a
  **script** with `PyAutoHands/autohands/` on `PYTHONPATH` — `python -m autohands.validate_env_profiles`
  fails with `ModuleNotFoundError: No module named 'env_config'`. It takes the workspace
  path as a positional arg.
- The `_jax` suffix is purely an env marker — siblings (`multi_analysis_jax.py`,
  `slam_pix_jax.py`) do **not** mirror it in search `name=`, so the output dir stays
  `latent_nan_robustness`.

## Original prompt

# Four workspace_test scripts declare use_jax=True but validate the numpy path

Type: test
Target: workspaces
Difficulty: small
Autonomy: safe
Priority: normal
Status: formalised

## Original request (verbatim)

> Triage the 4 workspace scripts that declare `use_jax=True` but resolve to
> PYAUTO_DISABLE_JAX=1 under the release profile (follow-up to PyAutoFit#1372,
> now closed). Repos: autolens_workspace_test, autogalaxy_workspace_test.
> Scripts: scripts/misc/latent/latent_nan_robustness.py (both repos — no
> `__Env__` section at all, so the JAX half of the deliberate numpy-vs-JAX pair
> runs on numpy; likely fix is `ENV: jax`), and
> scripts/imaging/visualization/visualization.py (both repos — declares
> `ENV: full_datasets real_plots`; file-existence asserts are valid on numpy and
> JAX-on siblings exist, but `use_jax=True` is misleading and the autogalaxy copy
> labels a likelihood check "JAX/{source_name}" while running numpy — needs a
> judgment call, not a blind override).

## Provenance

Closing follow-up of **PyAutoFit#1372** (closed 2026-07-28). That issue's library
finding — `al.AnalysisDataset` reading `PYAUTO_DISABLE_JAX` *before*
`super().__init__()` — was fixed by `PyAutoLens@83016c1ea` ("PYAUTO_DISABLE_JAX
has exactly one reader"). The env var now has exactly one reader across all five
libraries (`autofit/non_linear/analysis/analysis.py:68`). What #1372 deferred was
the workspace triage recorded here.

Blast radius re-measured with `autohands.env_config.build_env_for_script` against
each repo's `profile_release.yaml` (not by eye — the `jax_*` / `*_jax` / `*_jit`
marker derivation is easy to guess wrong):

| repo | declares `use_jax=True` | resolves JAX **OFF** |
|---|---|---|
| autofit_workspace_test | 10 | 0 (its release profile pins `"0"`) |
| autolens_workspace_test | 55 | 4 |
| autogalaxy_workspace_test | 36 | 2 |

Two of the six are the known false positives (`simulator_use_jax_parity` pair —
`SimulatorImaging` does not read the env var). The other four are this task.

## The two cases are different — do not apply one fix to both

### Case A — `scripts/misc/latent/latent_nan_robustness.py` (both repos): genuinely vacuous

Each script deliberately builds **both** analyses to contrast them:

```python
analysis     = ag.AnalysisImaging(dataset=dataset, use_jax=False, magzero=25.0)
analysis_jax = ag.AnalysisImaging(dataset=dataset, use_jax=True,  magzero=25.0)
```

Neither file declares an `__Env__` section at all, so both inherit the release
profile default `PYAUTO_DISABLE_JAX: "1"` and **both halves run numpy**. The
script's whole subject — that the JAX latent path masks NaN latents per batch via
`jnp.all(isfinite, axis=0)` — is never exercised.

Fix: **rename the file to carry the `_jax` marker** —
`latent_nan_robustness.py` → `latent_nan_robustness_jax.py` — so the release
profile's `derive_jax_markers` derivation turns JAX on. Update the
`smoke_tests.txt` entry in both repos and the path comment in
`autogalaxy_workspace_test/config/latent.yaml:3`.

The `use_jax=False` half is unaffected — the env var can only force `False`,
never `True` — so the numpy-vs-JAX contrast is preserved.

### Why the marker, and NOT an in-file `ENV: jax` declaration

`ENV: jax` was the first-choice fix and is **wrong here**. The naming marker is
the only sanctioned lever for JAX-on in a release profile:

- `validate_env_profiles.py:152-161` states the rule directly: unsetting
  `PYAUTO_DISABLE_JAX` for a **non-jax-marked** script "is NOT migratable — a
  `jax` declaration is profile-agnostic, so on a non-marked script it would flip
  the release resolution `1` -> absent (numpy -> JAX), a real behaviour change
  outside the verified `0` -> absent equivalence class."
- **Profile-agnostic is the actual defect**: neither repo's `profile_smoke.yaml`
  sets `derive_jax_markers`, so a declaration would turn JAX on under **smoke**
  too — and both of these scripts are in `smoke_tests.txt`, i.e. the per-PR gate.
  The marker is profile-aware: JAX under release, numpy under smoke.
- `validate_env_profiles.py:138-145` separately forbids a release profile
  override touching `PYAUTO_DISABLE_JAX` ("the derivation rule replaces
  enumeration"). Name → marker is the whole mechanism, by design.
- Note the declaration would *also* slip past the marker audit at
  `validate_env_profiles.py:190-198`, which tests `disabled == "0"`: a
  declaration **pops** the var, so it resolves to absent, not `"0"`. It would be
  silently unaudited — the exact silent-rot failure mode the derivation replaced.

`_jax` suffix matches the repo's established idiom (`visualization_jax.py`,
`multi_analysis_jax.py`, `slam_general_jax.py`). Under smoke the JAX half stays
vacuous, which is correct and intended — smoke is the fast numpy subset; release
is where fidelity lives.

Precedent: the **autofit_workspace_test** sibling of this same script had its JAX
half run for the first time under the `release-profile-jax-default` change and
exited 0 — no hidden bug. Expect the same here, but verify rather than assume.

### Case B — `scripts/imaging/visualization/visualization.py` (both repos): the kwarg is redundant, not load-bearing

`use_jax=True` here is a **no-op in every environment**, because `ag.*` / `al.*`
analyses already default `use_jax=True`. Writing it explicitly changes nothing —
it only signals an intent the script does not carry out.

The script's assertions are PNG/FITS existence checks, which are perfectly valid
on the numpy path. It has JAX-on siblings by design (`visualization_jax.py`,
`modeling_visualization_jit.py`) — so `visualization.py` **is** the numpy variant.

**Do not add `ENV: jax` here.** The entire `modeling_visualization_jit` family is
parked in `no_run.yaml` for exceeding the 300s cap ("JIT + full visualization
pipeline"). Turning JAX on for `visualization.py` invites the same perf wall, for
no assertion gain.

Fix: drop the redundant `use_jax=True` kwarg, and in the **autogalaxy** copy fix
the mislabelled likelihood check — `_assert_likelihood_sanity(f"JAX/{source_name}", ...)`
runs on numpy under both validation profiles, so the `"JAX/"` prefix is a false
claim in the output. (The autolens copy has no such label.)

## Files

Case A (rename + reference updates):
- `autolens_workspace_test/scripts/misc/latent/latent_nan_robustness.py` → `…_jax.py`
- `autogalaxy_workspace_test/scripts/misc/latent/latent_nan_robustness.py` → `…_jax.py`
- `autolens_workspace_test/smoke_tests.txt:25`
- `autogalaxy_workspace_test/smoke_tests.txt:37`
- `autogalaxy_workspace_test/config/latent.yaml:3` (path in a comment)

Case B (kwarg + label):
- `autolens_workspace_test/scripts/imaging/visualization/visualization.py`
- `autogalaxy_workspace_test/scripts/imaging/visualization/visualization.py`

## Validation

- Run `autohands validate_env_profiles` (with `--strict-markers`) in both repos —
  the rename must satisfy the marker audit rather than bypass it.
- Re-run the resolver sweep in both repos; the only `use_jax=True` scripts still
  resolving JAX-OFF should be the two `simulator_use_jax_parity` false positives.
- Run both renamed `latent_nan_robustness_jax.py` under the **release** profile and
  confirm exit 0 with JAX genuinely on, and that runtime stays under the 300s cap
  (if it does not, that is a real finding — park it with a `SLOW` marker rather
  than reverting).
- Confirm both still resolve JAX-**off** under the **smoke** profile (neither smoke
  profile sets `derive_jax_markers`), so the per-PR gate does not slow down.
- Run both `visualization.py` and confirm unchanged behaviour (the kwarg was a
  no-op; this should be a pure no-change-in-behaviour edit).

## Explicitly out of scope

The strategic question behind all of this — **whether it is intended that
`mode=release` validates the numpy path for most of the autolens/autogalaxy
surface** — is not settled here. The `release-profile-jax-default` record flags
"DO NOT COPY to autolens/autogalaxy_workspace_test" (their analyses default
`use_jax=True`, so flipping the profile default is a real behaviour change across
the whole surface, unlike in autofit_workspace_test where it was a no-op for ~35
of 42 scripts). This task keeps the profile default at `"1"` and opts in only the
one script that needs it.

That record also claims a research brief was filed at
`draft/research/workspaces/env_profile_and_validation_gate_redesign.md` — **it does
not exist anywhere in PyAutoMind**. The open question is currently unrecorded and
wants its own research prompt.
