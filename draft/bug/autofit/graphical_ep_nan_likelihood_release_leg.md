# `graphical/ep.py` fails the release leg with all-`nan` likelihoods

Type: bug
Target: autofit
Repos:
- PyAutoFit
- autofit_workspace_test
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised
Issue: (none yet — related parent report is https://github.com/PyAutoLabs/PyAutoFit/issues/1405)

## Symptom

The 2026-08-03 nightly stopped at Stage 3 (release-fidelity integration),
PyAutoHeart run 30788224561, job
`integrate / run_scripts (3.12, autofit_test, graphical)`:

```
Found 8 scripts
  scripts/graphical/ep.py ...              FAIL (11.4s)
      - The`log_likelihood_function`  is always returning `nan` values.
  scripts/graphical/ep_deterministic.py ...   PASS (1.5s)
  scripts/graphical/ep_exact.py ...           PASS (1.2s)
  scripts/graphical/ep_parity.py ...          PASS (7.4s)
```

Its three siblings in the same shard, same wheels, same release profile, all
pass. The message is PyAutoFit's search-initializer diagnostic: the initializer
could not find a start point with a finite likelihood.

## What is known

- **Intermittent.** The `autofit_test / graphical` shard passed on the
  2026-08-04 night with no change to `ep.py`, so this is not a deterministic
  regression against those wheels. Establish the rate before theorising about
  cause — a one-off and a one-in-three are different bugs.
- **Release-leg only so far.** The release profile runs full fidelity with
  `PYAUTO_TEST_MODE` unset, so `ep.py` runs a real capped sampler rather than
  the test-mode shortcut. Reproduce with
  `run_python.py autofit_test scripts/graphical --env-config config/build/profile_release.yaml`
  before reaching for anything else; a smoke-profile run will not show it.
- Failing at 11.4s, i.e. during initialization, not part-way through a fit.

## Relationship to the existing EP prompts

Three EP bug prompts already exist and none of them covers this:

- `draft/bug/autofit/ep_initializer_exception_should_not_abort.md` — closest
  shape (an initializer failure killing the whole fit), but it is about the
  *handling*: a bad factor should degrade to a bad projection. That change would
  convert this crash into a silently degraded fit, which is worse here, not
  better, until the `nan` itself is understood. **Do not treat that prompt as
  the fix for this one.**
- `draft/bug/autofit/ep_hierarchical_scale_collapse_moment_match.md` — parent
  scale collapse, a different failure mode.
- PyAutoFit#1405 — the parent report both of the above hang off.

Check this against #1405 first; if it is a manifestation of that, fold it in
and close this prompt rather than opening a fourth EP issue.

## Exit criteria

The `nan` source is identified (model/prior region, dataset, or an
initialization path that only runs outside test mode), and either fixed or
recorded on #1405 with the release leg green.
