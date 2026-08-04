## database-guide-sample-weight-threshold
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/464
- completed: 2026-08-04
- workspace-pr: https://github.com/PyAutoLabs/autolens_workspace/pull/465 (merged ec82b6ba) + https://github.com/PyAutoLabs/autogalaxy_workspace/pull/202 (merged 9eee226d)
- summary: `guides/results/database/start_here.py` ran its own Nautilus fits capped at n_like_max=300 then indexed sample 9; config/output.yaml's samples_weight_threshold=1e-10 pruned samples.csv to ONE row, so the index raised IndexError in Heart's release-integrate leg (run 30880450685). Fixed by disabling the threshold before the fits, the idiom _quick_fit.py already established for the sibling results guides in PR#275 — this script was left out of that consolidation because building a database from its OWN output folder is its subject.

  ROOT CAUSE OF THE BLIND SPOT: `samples.py` does `if skip_checks(): weight_threshold = None`, and `skip_checks()` reads PYAUTO_SKIP_CHECKS — smoke sets it to 1, release to 0. Measured 301 rows under smoke vs 1 under release on the same script. The per-PR smoke gate is STRUCTURALLY incapable of failing on this class of bug; both PR bodies say so explicitly so a green smoke run is not mistaken for evidence.

  NOT A REGRESSION: e41b0fce un-parked the script from no_run.yaml, so the guides shard ran 42 scripts vs yesterday's 41. Pre-existing defect, newly reachable. The tell was the PASS/FAIL line count between the two job logs, not a library diff.

  AUTOGALAXY SIBLING needed FOUR fixes, not one, and was un-parked: (1) same threshold bug; (2) no auto-simulate guard at all; (3) it read an info.json that NO simulator writes — only data_preparation/examples/optional/info.py does, and only for `simple`, so two of its three datasets could never have worked (its parking note blamed missing simulator output, which was wrong); (4) three uncapped Nautilus fits under real_search that would not fit the 1800s cap. Now 78s.

  EVIDENCE: control-vs-patched under profile_release.yaml (PYAUTO_SKIP_CHECKS=0, TEST_MODE and SMALL_DATASETS confirmed unset). autolens control reproduced the CI traceback line-for-line at 1 row x2; patched 300 rows x2. autogalaxy control (threshold line ALONE commented out on the branch) 1 row x3 IndexError; patched 300 rows x3 — proving the line is load-bearing there rather than defensive.

  PROCESS: shipped under the corrective-PR exception with Heart RED, human-authorized against the verbatim reason "release validation FAILED (stage integrate)" (recorded on #464 issuecomment-5177223209). Human then instructed merge. `gh pr merge --auto` MERGED BOTH IMMEDIATELY rather than waiting — neither repo configures its smoke checks as REQUIRED, so both PRs were already mergeable. autolens therefore merged with smoke mid-flight; it subsequently passed 3.12 (9m38s) + 3.13 (8m23s), as did autogalaxy. Lesson: verify required-checks configuration before relying on --auto to gate a merge.

- follow-ups: autogalaxy notebooks/README.md is stale vs scripts/README.md (typo + missing multi_galaxy/cluster entries; reverted here to keep the diff scoped); autogalaxy data_preparation/examples/optional/info.py writes LENSING keys in a galaxy workspace. Both noted on PR#202, neither fixed.

## Original prompt

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
