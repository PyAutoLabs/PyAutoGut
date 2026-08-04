# Database guide indexes sample 9 of a fit the weight threshold prunes to 1 sample

Type: bug
Target: autolens_workspace
Repos:
- autolens_workspace
- autogalaxy_workspace
Difficulty: small
Autonomy: supervised
Priority: high
Status: formalised

Surfaced by `/wake_up` 2026-08-04 from the overnight release-integrate run.

## Original request (verbatim)

> Can we fix this from the wake up skill: │ autolens_workspace │ FAIL (129.9s)
> IndexError: list index out of range — this is new, not in yesterday's known set.
> Smells like the aggregator │ scripts/guides/results/database/start_here.py │
> samples/weight-threshold IndexError family (prior: PyAutoFit PR#275).

## The failure

PyAutoHeart *Release Integrate* run 30880450685, job
`integrate / run_scripts (3.12, autolens, guides)` (job 91900532465). From the
run artifact `autolens__scripts__guides__script.json`:

    File ".../scripts/guides/results/database/start_here.py", line 358, in <module>
        print(samples.parameter_lists[9][2], "\n")
    IndexError: list index out of range

## Why it is new

Nothing regressed — a skip was lifted. Commit `e41b0fce` (2026-08-03, "fix: add
auto-simulate guards to unguarded dataset loads") added the auto-simulate guard
to this script and removed its `NEEDS_FIX` entry from
`config/build/no_run.yaml`. Yesterday's release-integrate run (30842349506)
executed 41 scripts in the guides shard; today's executed 42, the extra one
being this script. It ran for the first time and hit a pre-existing defect.

## Root cause (reproduced locally)

The script performs its own two Nautilus fits capped at `n_like_max=300`, then
indexes sample 9 of the samples it reads back.

`PyAutoFit/autofit/non_linear/samples/samples.py:398` applies
`config/output.yaml`'s `samples_weight_threshold: 1.0e-10` when writing
`samples.csv`. A 300-evaluation nested-sampling run is so weight-peaked that
only a single sample clears that threshold. Four lines later:

    if skip_checks():
        weight_threshold = None

and `skip_checks()` (`PyAutoNerves/autonerves/test_mode.py:75`) reads
`PYAUTO_SKIP_CHECKS`. `profile_smoke.yaml` sets it to `1`; `profile_release.yaml`
sets it to `0`.

That is the whole split:

| profile | `PYAUTO_SKIP_CHECKS` | threshold | rows in `samples.csv` | result |
|---------|----------------------|-----------|-----------------------|--------|
| smoke   | `1`                  | disabled  | 301                   | PASS   |
| release | `0`                  | 1e-10     | 1                     | FAIL   |

Verified by running the script under each profile via
`autohands.env_config.build_env_for_script` and counting rows in both written
`samples.csv` files. **The per-PR smoke gate is structurally blind to this
class of failure** — only the release profile exercises it.

Repro trap worth knowing: `output/database.sqlite` sits *beside*
`output/database/`, so `rm -rf output/database` does not clear it and the
aggregator silently reads the previous run's entries. A first "pass" was a
false negative from exactly that.

## Relationship to prior art

Same family as PyAutoFit PR#275 / `autolens_workspace#274` (release-validation
cluster E). That fix consolidated the other `guides/results` tutorials onto
`scripts/guides/results/_quick_fit.py`, which sets

    conf.instance["output"]["samples_weight_threshold"] = None

at line 57 with a comment stating precisely this reason. `database/start_here.py`
was left out of that consolidation because it must build a database from its
*own* output folder over two differently-named datasets — that is the tutorial's
subject — so it cannot resume `_quick_fit`'s results.

## Proposed fix

Set `conf.instance["output"]["samples_weight_threshold"] = None` before the fit
loop in `scripts/guides/results/database/start_here.py`, with a comment
explaining that the cap of 300 likelihood evaluations is what makes the pruning
bite, mirroring `_quick_fit.py`. Regenerate the notebook.

## Sibling — revive it (human-scoped 2026-08-04)

`autogalaxy_workspace/scripts/guides/results/database/start_here.py:315` carries
the identical `parameter_lists[9][2]` over its own capped fit. It is currently
masked because that repo still parks the script `NEEDS_FIX` in its own
`config/build/no_run.yaml:29`.

It has **two** independent defects, not one. Its parking reason
(`FileNotFoundError` in a clean checkout) stands on its own: unlike the autolens
script it has no auto-simulate guard at all — it calls `ag.Imaging.from_fits`
straight off `dataset_path` with no `should_simulate` check and no
`simulator_paths` mapping. So the weight-threshold fix alone would NOT un-park it.

Human scope decision 2026-08-04: **fully revive it** —

1. add the auto-simulate guard, mirroring autolens's `e41b0fce`, for all three
   of its datasets (`simple`, `simple__sersic`, `sersic_x2`);
2. apply the same `samples_weight_threshold = None` fix;
3. remove its `NEEDS_FIX` entry from `config/build/no_run.yaml`;
4. verify end-to-end under the release profile before un-parking.

Checked and **not** affected: `autofit_workspace/scripts/cookbooks/result.py:428`
uses the same index but after an `af.Emcee` fit, whose samples all carry weight
1.0, so the threshold never prunes.

Checked and **not** affected: `autofit_workspace/scripts/cookbooks/result.py:428`
uses the same index but after an `af.Emcee` fit, whose samples all carry weight
1.0, so the threshold never prunes.

## Release context

The overnight run that surfaced this is the nightly release-integrate leg while
a release drive is in flight (see `active.md` → `simulator-util-to-af-ex`
→ `release-resume-updated`). This failure gates that leg.
