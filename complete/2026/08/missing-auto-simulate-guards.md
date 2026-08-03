Fixed 3 of the 4 missing-dataset smoke failures from PyAutoHeart run 30790463134
(the 4th, `group/data_preparation/start_here`, was deleted by #456). All three
were reproduced on a clean checkout before any edit, and **every paired
simulator already existed** — the fix was an auto-simulate guard in each case.

- autolens_workspace#460 (issue #455)
- HowToLens#65

## Root cause shape

Two of the three failing scripts already carried a *correct* guard — for their
**first** dataset. The load that failed was a **second** dataset further down the
same file that nobody guarded. `mask_irregular.py` had no guard at all.

A sweep widened this to a class: dataset loads reaching `from_fits` with no guard
pass smoke only because an earlier script in the run happens to simulate the same
dataset first. **End state: zero unguarded dataset loads remain in either repo**
(corrected sweep re-run on the merged tree returns empty).

Final scope: **16 guards across 18 files.**

## Three faults the triage did not name

1. **`dataset/imaging/lens_sersic` has ZERO producers.** Referenced by
   `gui/lens_light_centre.py:32`, `guides/results/database/start_here.py:73`, and
   `aggregator/queries.py:60` (prose only). Repointing at
   `dataset/multi_dataset/imaging/lens_sersic` was rejected — it is multi-band
   with `g_` prefixes, so a plain `from_fits(data_path=.../"data.fits")` cannot
   load it. Both consumers repointed at `dataset/imaging/simple`.

2. **`guides/results/database/start_here.py` had THREE faults, not the one its
   NEEDS_FIX marker named.** Behind the missing dataset sat a missing
   `info.json` — the sole producer writes it for `simple` ALONE, so nothing wrote
   `simple__no_lens_light/info.json` in any run order; built inline instead, dead
   `import json` removed. Behind that sat an **unbounded real search**.

3. **The unbounded search was a missing convention, not a slow script.** It
   declares `ENV: real_search` (so `PYAUTO_TEST_MODE` is unset and the sampler
   genuinely runs) but was the ONLY such script in the workspace without an
   `n_like_max`; its four siblings in `guides/results/` all cap at 300, and
   `_quick_fit.py:16` documents why. Unbounded (>9min, fit 1 of 2 not
   converging) → **EXIT 0 in 245s**. Invariant `real_search` ⟹ `n_like_max` now
   holds with zero exceptions (exactly 5 scripts declare `real_search` + use
   `af.Nautilus`; all 5 capped).

## Two self-corrections worth carrying forward

- **Sweep under-detected guards.** The first pass grepped only
  `should_simulate` and missed 4 scripts with hand-rolled
  `subprocess.run(... simulator.py ...)` guards, inflating scope from 16 to 21.
  A guard-detection sweep must accept BOTH idioms.
- **`PYAUTO_TEST_MODE=1` is not smoke.** Smoke uses `TEST_MODE=2` (sampler
  skipped); `=1` is reduced-iterations and SLOWER. Verifying under `=1` made two
  scripts appear to stall for 15 minutes. Rebuilt every verification via
  `autohands.env_config.build_env_for_script` against
  `config/build/profile_smoke.yaml` — those same scripts then ran in 19s and 20s.

## Validation

Every changed script that can run, run under its real smoke env. Because those
envs set `PYAUTO_SMALL_DATASETS=1`, `should_simulate` rmtree's and re-simulates,
so every guard was genuinely exercised rather than skipped over pre-existing
data. mask_irregular 8s · imaging_and_interferometer 20s · tutorial_3_inversions
19s · database/start_here 245s · queries 68s · delaunay 24s ·
linear_light_profiles 11s · guides/results/start_here 11s · psf 10s ·
latent_variables 9s · data_preparation/start_here 9s.

NOT verified by execution: the 5 GUI scripts + `tutorial_5_borders.py`, all
`no_run` (cannot run headless). Syntax- and import-checked only; stated as such
in both PR bodies.

`check_sizes.sh` clean. Full `generate.py autolens` left `workspace_index.json`
and `llms-full.txt` byte-identical, so the generated-index collision feared
against #453/#459 never materialised.

## Ship gate + the CI regression it collided with

Heart RED at ship time (2026-08-03T17:44:16Z); shipped under the corrective-PR
exception, human-authorized, scoped to the YELLOW
`"workspace validation not passing (... cloud#30790463134 ...)"`. None of the
three RED reasons related to this change.

Both PRs then went red on CI for a reason that was **not** this change: the six
`intra-family-dep-floors` PRs merged 18:08:00–18:08:15Z and broke source-chain
install organism-wide (`autofit 1.0.dev0 depends on autonerves>=2026.7.29.2` →
`ResolutionImpossible`), because CI installs the chain from local source where
everything versions as `1.0.dev0`. Diagnosed, and a steering prompt filed at
`draft/bug/health_fixes/dep_floors_break_source_chain_ci.md` (10 affected repos,
control test, explicit "do NOT revert the floors", and the trap that a "fix"
could go green by silently switching CI to released wheels). Another session
took it and shipped PyAutoNerves#147 — `setup.py` default `1.0.dev0` →
`9999.0.0.dev0` across all five libraries. CI green after that.

## Follow-up left open (deliberately not bundled)

Two guard idioms coexist and are NOT equivalent: `should_simulate` also
deletes-and-rebuilds under `PYAUTO_SMALL_DATASETS=1`; the hand-rolled variants in
4 scripts do not, so those keep FULL-RESOLUTION data on disk in a capped run.
Not folded in — it is a behaviour change to scripts that currently pass. Prompt:
`draft/maintenance/autolens_workspace/normalise_auto_simulate_guard_idiom.md`.

Also corrected in-flight: the triage's "several start_here NEEDS_FIX markers"
claim — `no_run.yaml` carried 4 NEEDS_FIX entries, exactly one dataset-related.
`imaging/data_preparation/start_here` and `guides/results/start_here` were never
in `no_run`; they passed only by run-ordering luck and are now guarded.

## Original prompt

# Missing auto-simulate guards on second-and-later dataset loads

Type: bug
Target: autolens_workspace
Repos:
- autolens_workspace
- HowToLens
Difficulty: small
Autonomy: supervised
Priority: normal
Status: formalised

## Original request (verbatim)

> 4 — Missing-dataset failures (claims autolens_workspace + HowToLens — conflict group)
> Four workspace-smoke failures, all FileNotFoundError on a dataset the script
> never simulates:
>   - autolens  notebooks/group/data_preparation/start_here.ipynb
>       -> dataset/group/simple/data.fits
>   - autolens  notebooks/imaging/data_preparation/manual/mask_irregular*.ipynb
>       -> dataset/imaging/simple__no_lens_light/data.fits
>   - autolens  notebooks/multi_dataset/features/imaging_and_interferometer*
>       -> dataset/multi_dataset/imaging/lens_sersic/...
>   - howtolens notebooks/chapter_4_pixelizations/tutorial_3_inversion*
>       -> dataset/imaging/source_complex/data.fits
>
> Evidence: PyAutoHeart workspace-smoke run 30790463134. The smoke report also
> carries NEEDS_FIX markers dated 2026-07-30 for several start_here scripts saying
> they "fail fast in a clean checkout - needs simulator outputs".
>
> Reproduce each in a genuinely clean checkout before trusting the markers. Work
> out whether the fix is an auto-simulate guard, a missing shipped dataset, or a
> no_run entry - and note that the auto-simulate guard checks EXISTENCE only, so a
> stale directory can mask the failure. Other than the group data prepratation start here, which another issue is fixing, I think these all just need Auto Simulate things added? if the right simulator script to pair to the aut simulator is missing let me know

## Verdict

The user's read is correct: the fix is an auto-simulate guard in every case, and
**no simulator is missing** for any of the three in-scope failures.

`group/data_preparation/start_here.py` is OUT OF SCOPE (handled by another issue).

## Reproduced on clean local main

`autolens_workspace/dataset/imaging/` contains only the real shipped datasets
(`cosmos_web_ring`, `simulated_lens`, `slacs1430+4105`), so no stale directory is
masking anything — the existence-only `should_simulate` check is honest here.

| Script | Missing file (reproduced) | Paired simulator |
|---|---|---|
| `autolens_workspace/scripts/imaging/data_preparation/manual/mask_irregular.py:42` | `dataset/imaging/simple__no_lens_light/data.fits` | `scripts/imaging/features/no_lens_light/simulator.py` ✅ |
| `autolens_workspace/scripts/multi_dataset/features/imaging_and_interferometer/modeling.py:103` | `dataset/multi_dataset/imaging/lens_sersic/g_data.fits` | `scripts/multi_dataset/simulator.py` ✅ |
| `HowToLens/scripts/chapter_4_pixelizations/tutorial_3_inversions.py:153` | `dataset/imaging/source_complex/data.fits` | `scripts/simulator/source_complex.py` ✅ |

## Root cause shape

Two of the three scripts already carry a *correct* guard — for their FIRST
dataset. The load that fails is a SECOND dataset further down the same file that
nobody guarded:

- `imaging_and_interferometer/modeling.py` — guard at L73 covers the
  interferometer dataset; the imaging block at L100-108 (`lens_sersic`) has none.
- `tutorial_3_inversions.py` — guard at L49 covers `simple__no_lens_light`; the
  `source_complex` block at L152-158 has none.
- `mask_irregular.py` — no guard at all (single dataset).

## Wider sweep (in scope — human-approved)

A sweep of both repos for `dataset_path = …` blocks that reach `from_fits`
without a preceding `should_simulate`, excluding shipped real datasets and
excluding re-assignments of a path already guarded earlier in the same file,
found **22 unguarded blocks**. Only 4 fail smoke; the rest pass ONLY because an
earlier script in the smoke run happens to simulate the same dataset first. That
ordering dependence is real fragility — a script run standalone in a clean
checkout still breaks.

Scope decision (human, 2026-08-03): **fix all 22**, minus
`group/data_preparation/start_here.py` (other issue).

Full list:

- `scripts/cluster/likelihood_function.py:104` → `dataset/cluster/simple` → `scripts/cluster/simulator.py`
- `scripts/guides/results/database/start_here.py:98` → `dataset/imaging/simple` → `scripts/imaging/simulator.py`
- `scripts/guides/results/latent_variables.py:136` → `dataset/imaging/simple__no_lens_light` → `scripts/imaging/features/no_lens_light/simulator.py`
- `scripts/guides/results/start_here.py:131` → same as above
- `scripts/imaging/data_preparation/examples/psf.py:52` → `dataset/imaging/simple` → `scripts/imaging/simulator.py`
- `scripts/imaging/data_preparation/gui/extra_galaxies_centres.py:39` → `dataset/imaging/extra_galaxies` → `scripts/imaging/features/extra_galaxies/simulator.py`
- `scripts/imaging/data_preparation/gui/lens_light_centre.py:33` → **see dead-path note below**
- `scripts/imaging/data_preparation/gui/mask.py:35` → `dataset/imaging/simple__no_lens_light`
- `scripts/imaging/data_preparation/gui/mask_extra_galaxies.py:39` → `dataset/imaging/extra_galaxies`
- `scripts/imaging/data_preparation/gui/positions.py:36` → `dataset/imaging/simple__no_lens_light`
- `scripts/imaging/data_preparation/manual/mask_irregular.py:42` → **smoke failure**
- `scripts/imaging/data_preparation/start_here.py:48` → `dataset/imaging/simple`
- `scripts/imaging/features/advanced/subhalo/sensitivity/slam_source_parametric.py:868` → `dataset/imaging/dark_matter_subhalo` → `scripts/imaging/features/advanced/subhalo/simulator.py`
- `scripts/imaging/features/advanced/subhalo/sensitivity/slam_source_pixelized.py:995` → same
- `scripts/imaging/features/linear_light_profiles/likelihood_function.py:65` → `dataset/imaging/simple`
- `scripts/imaging/features/pixelization/delaunay.py:932` → `dataset/imaging/simple` (the second unguarded block at `:1041` resolves to the SAME path and runs later in the same linear script, so one guard at `:932` covers both — do not add two)
- `scripts/interferometer/features/pixelization/many_visibilities_preparation.py:82` → `dataset/interferometer/simple` → `scripts/interferometer/simulator.py`
- `scripts/multi_dataset/features/imaging_and_interferometer/modeling.py:103` → **smoke failure**
- `HowToLens/scripts/chapter_4_pixelizations/tutorial_3_inversions.py:153` → **smoke failure**
- `HowToLens/scripts/chapter_4_pixelizations/tutorial_5_borders.py:280` → `dataset/imaging/x2_lens_galaxies` → `scripts/simulator/lens_x2.py` (script is `no_run` for an unrelated mask reason; guard it anyway)

## Dead dataset path — `dataset/imaging/lens_sersic` (ZERO producers)

No simulator in either repo writes `dataset/imaging/lens_sersic`. Three places
reference it:

- `scripts/imaging/data_preparation/gui/lens_light_centre.py:32` (+ docstring L30)
- `scripts/guides/results/database/start_here.py:73` — loops over
  `["simple", "lens_sersic", "simple__no_lens_light"]`, so this script needs
  THREE datasets, one of which does not exist. Its `no_run` NEEDS_FIX marker
  blames only `dataset/imaging/simple/data.fits` — that is the first failure,
  not the whole story.
- `scripts/guides/results/aggregator/queries.py:60` — **prose only**. The code
  at L64 already queries `simple__no_lens_light`; the sentence naming
  `lens_sersic` is stale. No functional dependency.

Rejected: repointing at `dataset/multi_dataset/imaging/lens_sersic` (the only
real `lens_sersic` dataset). It is multi-band with `g_data.fits`/`g_psf.fits`/
`g_noise_map.fits` prefixes, so a plain `from_fits(data_path=dataset_path/"data.fits")`
cannot load it.

Fix (human decision, 2026-08-03) — **repoint at the existing `dataset/imaging/simple`**,
which `scripts/imaging/simulator.py` builds with a Sersic bulge on the lens
galaxy (L184), i.e. single-band imaging that genuinely has lens light:

- `gui/lens_light_centre.py` → `dataset_name = "simple"`, guard with
  `scripts/imaging/simulator.py`, update the L30 docstring folder reference.
- `guides/results/database/start_here.py` → **drop** the dead `lens_sersic`
  entry rather than duplicate `simple` twice (two identically-named database
  entries would defeat the guide's own point). List becomes
  `["simple", "simple__no_lens_light"]`; update the surrounding "3 dataset
  names" prose to 2 and guard both names inside the loop.
- `guides/results/aggregator/queries.py:60` → fix the stale prose to name
  `simple__no_lens_light`, matching the code directly beneath it.

## Correction to the triage note

The triage claims NEEDS_FIX markers for "several start_here scripts". In fact
`config/build/no_run.yaml` carries 6 NEEDS_FIX markers of which exactly **one**
is dataset-related: `guides/results/database/start_here` (2026-07-30,
`FileNotFoundError dataset/imaging/simple/data.fits`). `imaging/data_preparation/start_here`
and `guides/results/start_here` are NOT in `no_run` — they are unguarded and pass
only by run-ordering luck.

ALSO IN SCOPE: once `guides/results/database/start_here` is guarded, remove its
NEEDS_FIX line from `autolens_workspace/config/build/no_run.yaml`.

## Guard idiom (copy verbatim, adjusting the simulator path)

```python
"""
__Dataset Auto-Simulation__

If the dataset does not already exist on your system, it will be created by running the corresponding
simulator script. This ensures that all example scripts can be run without manually simulating data first.
"""
if al.util.dataset.should_simulate(str(dataset_path)):
    import subprocess
    import sys

    subprocess.run(
        [sys.executable, "scripts/<path>/simulator.py"],
        check=True,
    )
```

## Notes

- Notebooks must be regenerated from the scripts after the edits.
- `autolens_workspace` main is clean; the `interferometer-start-here-integrate-oom`
  claim in `active.md` is stale (PR#450 merged, `c4bd2796` on main). `HowToLens`
  is unclaimed.
