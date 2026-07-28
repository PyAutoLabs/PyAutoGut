# Auto-simulate guards pointed at the wrong simulator — 6 fixed, not 2

Issue: https://github.com/PyAutoLabs/autolens_workspace/issues/359
PRs: autolens_workspace#364 (`bb272a6`), autogalaxy_workspace#175 (`f1ae4c3`) — both MERGED.

## What was wrong

The `should_simulate` migration (autolens_workspace#354) left guards whose
simulator writes a **different dataset directory** than the script then loads.
The guard fires, a simulator runs, and `from_fits` still raises
`FileNotFoundError`.

## The root-cause question, answered

#359 asked whether the guard targets were always wrong or whether
`should_simulate` itself regressed — and said to establish which **before
editing anything**. It is the former.
`PyAutoArray/autoarray/util/dataset_util.py:54` is an exact drop-in for
`not path.exists()` when the flag is off. **No wider `should_simulate` bug, no
blast radius beyond the guards.**

The amplifier: under `PYAUTO_SMALL_DATASETS=1` (set by *both*
`profile_smoke.yaml` and `profile_release.yaml`) the helper `rmtree`s the
directory **before** testing it. A mis-targeted guard therefore *destroys* a
correct dataset that was satisfying the load, then simulates a different one.
That is what turned an old latent mismatch into red CI.

## Scope: the report said 2, the audit found 6

A static resolver (evaluate each guard's `dataset_path`; evaluate each invoked
simulator's written path; diff) over both workspaces. The four the CI never
surfaced:

- `ag guides/plot/examples/{mat_plot,visuals}.py` — same crash shape, just not
  in a shard that ran.
- `al multi/features/slam/simultaneous.py` — **never raises.** Guard tested a
  doubled `multi/imaging/lens_sersic/lens_sersic` that can never exist, so it
  re-simulated on *every run, forever*. Error-driven triage cannot find this
  class; only a path-vs-path audit can.
- `ag multi/features/imaging_and_interferometer/modeling.py` — the imaging half
  had **no guard at all**.

Two of the six were **not** guard repoints, and getting this backwards would
have silently corrupted the tutorials:

- **MGE** — the guard was already right. Line 71 set
  `dataset_name = "lens_light_asymmetric"`; the next line discarded it for a
  hardcoded `"simple"`. The *path* was the bug. Repointing the guard would have
  fed `simple` to a script whose whole premise is asymmetric light a Sersic
  cannot fit.
- **pixelization** — the inverse. It builds a `lens_galaxy` with a `bulge`, so
  `simple` is correct and the guard was wrong. Repointing the *load* to
  `no_lens_light` would have been the wrong data.

Cleared as correctly wired (do not "fix"): the `samples/` guards in
`guides/modeling/advanced/{graphical,expectation_propagation,hierarchical}.py`,
the second guard in `multi/features/pixelization/modeling.py`, and the
self-guard in `group/features/multi_gaussian_expansion/simulator.py` (inline
body, not a subprocess).

A seventh case, `al guides/hpc/example_cpu.py`, **self-resolved mid-task** —
#360 replaced it with `example_cpu_and_gpu.py`, which has the local-fallback
block and a matching target.

## The smoke gate cannot verify this

None of the six scripts appear in `smoke_tests.txt` or `smoke_notebooks.txt` in
either workspace. **That is why the migration shipped green.** Verified instead
by direct runs from each repo root under `PYAUTO_TEST_MODE=2
PYAUTO_SMALL_DATASETS=1` — the second flag is the honest setting because it is
what exercises the destructive `rmtree` branch. All 6 PASS; resolver reports 0
mismatches on both merged mains. The scripts were deliberately **not** added to
the smoke list (curated subset by design).

`simultaneous.py` needed a different check — a single pass proves nothing for an
always-fires bug. Confirmed the guard path exists after one run and
`should_simulate` returns `False`, while the old doubled path never existed.

## Traps worth remembering

- **`PYAUTO_SKIP_VISUALIZATION` no-ops dataset writers**, so it must *not* be
  set when verifying an auto-simulate guard — it would invalidate the very
  thing under test.
- Running the two ag plot guides deposits an untracked, **non-gitignored**
  `notebooks/plot/plots/example.png`. Newly *surfaced*, not newly caused — the
  scripts used to crash before reaching the plot stage. Caught pre-commit;
  flagged on #175 for a `.gitignore` follow-up.
- `gh api -X PATCH .../issues/N -f 'labels[]=...'` silently no-ops; the labels
  endpoint rejects the form too. `gh issue edit N --add-label` works on PRs.

## Brain overrides (recorded)

`pyauto-brain bug` returned **`too-large` (score 13)** and **fix locus =
`config/build/*.yaml`, "never inline edits to the script body"**. Both
overridden:

- Score is driven by repo *count* (2), not complexity — this was 6 edits of 1–4
  lines.
- **The locus rule is actively wrong for this bug class.** No config knob can
  repoint a hardcoded simulator path; obeying it would make the bug unfixable.
  Worth correcting in the Bug Agent.

## Still open

**PyAutoHands#204** — nbconvert runs kernels in the notebook's own directory, so
every one of these guards still fails from a notebook. The `run_notebooks`
shards stay red until it lands; this task only made the *scripts* correct.
