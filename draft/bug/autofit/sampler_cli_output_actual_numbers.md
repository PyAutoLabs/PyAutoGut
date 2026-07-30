# Sampler CLI output should state actual numbers and real JAX compile status

## Request (verbatim)

> On-the-fly updates every iterations_per_quick_update is the command line output
> when a sampler runs, the actuallyh number should be printed to the CLI should say
> the actual number

> follow up, when JAX compiles a LH function it should say Should say "JAX jit
> compiling likelihood function, could take seconds or minutes..." in output so user
> knows why theres a small wait so a user knows they are waiting

## Problem

Two defects in what the CLI tells a user while a non-linear search runs.

### 1. Literal variable name printed instead of its value

The workspace scripts print a fixed string containing the *name* of the config
knob rather than its value, e.g. `autolens_workspace/scripts/imaging/start_here.py:340`:

```python
print(
    """
    The non-linear search has begun running.

    This Jupyter notebook cell with progress once the search has completed - this could take a few minutes!

    On-the-fly updates every iterations_per_quick_update are printed to the notebook.
    """
)
```

Occurrences: 23 `.py` scripts (autolens_workspace 14+, autogalaxy_workspace 3+,
HowToLens 1), with 23 generated `.ipynb` and 14 `.md` counterparts.

Complication: `search.iterations_per_quick_update` defaults to `1e99`
(`config/general.yaml` `updates:` block) — quick updates are effectively disabled
unless `hpc_mode` is on (250000). It is stored as a `float`
(`autofit/non_linear/search/abstract_search.py:216`). So a naive f-string would
print `1e+99`, which is worse than the placeholder. The message must branch on
whether the value is a real, finite cadence.

### 2. JAX compile message fires before compilation happens

`autofit/non_linear/fitness.py:508 / 528 / 549` log at *wrapper construction*
time, not compile time:

```python
logger.info("JAX: Applying jit to likelihood function -- may take a few seconds.")
func = jax.jit(self.call)
logger.info(f"JAX: jit applied in {time.time() - start} seconds.")
```

`jax.jit(...)` is instantaneous — it only wraps. Actual tracing/lowering/compilation
happens on the first call to the returned function (`fitness.py:310`,
`figure_of_merit = self._call(parameters)`). The user therefore sees "applied in
0.0001 seconds", then sits through an unexplained wait that can run to minutes.

## Desired behaviour

1. The search-start print states the actual iteration cadence, e.g.
   `On-the-fly updates every 250000 iterations are printed to the notebook.`
   When the value is the disabled sentinel (`1e99` / non-finite), say plainly that
   on-the-fly updates are off and name the config knob that enables them.
2. On the first likelihood evaluation under JAX, log
   `JAX jit compiling likelihood function, could take seconds or minutes...`
   before the call, and the true elapsed compile time after it. Same treatment for
   the `vmap` and `grad` variants.

## Scope

- `PyAutoFit` — `autofit/non_linear/fitness.py` (`_jit`, `_vmap`, `_grad` and the
  first-call path). Note `fitness._jit` is also consumed by
  `autofit/non_linear/search/mle/bfgs/search.py:183` (passed to scipy as `fun=`),
  so any wrapper must stay a plain callable. `__getstate__`/`__setstate__`
  (`fitness.py:474-491`) strip and rebuild these attributes — the one-shot flag
  must survive or reset cleanly across pickling.
- `autolens_workspace`, `autogalaxy_workspace`, `HowToLens` — the 23 `.py`
  scripts, then regenerate `.ipynb` and `.md`.

Library change lands first; the workspace print may want a small helper so the
disabled-vs-enabled wording is not duplicated 23 times.

## Verification

- Run a search with `iterations_per_quick_update` set to a real value and confirm
  the printed number matches the config.
- Run with the default `1e99` and confirm the "updates are off" wording.
- Run a JAX-backed fit and confirm the compile message appears *before* the wait
  and the reported elapsed time reflects the real compile, not ~0s.
- Confirm regenerated notebooks/markdown carry the new text (zero unrelated diff).
