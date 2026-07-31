# interferometer/start_here.py OOM in nightly release-validation integrate leg

Filed 2026-07-31 from the phase-4 ship gate of point-source-chi-squared-variants
(#657): Heart RED traced to the nightly Release Integrate run.

## Symptom

Nightly `Release Integrate` run
https://github.com/PyAutoLabs/PyAutoHeart/actions/runs/30607596240
(v2026.7.31.1.dev69201, profile=release) fails in job
`integrate / run_scripts (3.12, autolens, interferometer)` — the **release-mode
leg only** (TestPyPI wheels, release profile, no source on PYTHONPATH; the
smoke-mode leg of the same job was skipped/green):

```
scripts/interferometer/start_here.py ...   FAIL (58.8s)
jax.errors.JaxRuntimeError: RESOURCE_EXHAUSTED: Out of memory allocating 85898814480 bytes.
```

~86 GB in a single JAX allocation on a CI runner. All other integrate script
jobs passed (imaging 49m green, cluster, multi_galaxy, weak, autogalaxy, autofit).

## Notes for triage

- Release profile runs full-resolution (no PYAUTO_SMALL_DATASETS) with JAX
  enabled — an ~86 GB buffer smells like a dense NUFFT/transformer matrix or a
  vmap batch materializing at full uv-resolution rather than a leak.
- Check whether this is a regression from a recent PyAutoArray/PyAutoLens main
  change (nightly wheels) vs a long-standing release-leg gap that only now runs
  this script.
- The same job's earlier `verify_install_release` step logged
  `TestPyPI install failed after 30 attempts` before succeeding on retry —
  probably unrelated flake, but confirm the wheel set installed was current.

## Exit criteria

Release-mode interferometer leg green in the nightly Release Integrate run;
root cause recorded (config/profile fix vs library fix).
