# Fix release-profile numerical inversion failures

Type: bug
Target: health_fixes
Difficulty: too-large
Autonomy: supervised
Priority: high
Status: formalised

## Context

Two interferometer scripts fail in inversion paths with non-positive-definite matrices.
The Autolens test failure reproduces on current `main`; the Autogalaxy script passed in a
stateful local checkout and needs a clean confirmation.

Owners: @PyAutoArray, @PyAutoGalaxy, @PyAutoLens, @autogalaxy_workspace, and
@autolens_workspace_test.

## Scripts

- `autogalaxy_workspace/scripts/interferometer/features/pixelization/galaxy_reconstruction.py`
- `autolens_workspace_test/scripts/interferometer/model_fit.py`

## Required work

1. Reproduce in clean output/worktrees with deterministic seeds and release settings.
2. Capture the curvature and regularization matrix properties at failure: symmetry,
   conditioning, eigenvalue range, dtype, backend, and mapper configuration.
3. Identify whether the defect is invalid sampled parameters, regularization construction,
   numerical stabilization, or a script model that permits an undefined inversion.
4. Fix the owning library for valid inputs. Do not catch `LinAlgError` or alter the script
   to hide a genuine inversion failure.
5. Add numerical regression tests and rerun both scripts repeatedly under the profile.

<!-- formalised retroactively by the Intake (Conception) Agent on 2026-07-08 -->

## 2026-08-21 — REPRODUCTION GATE RUN: **2/2 PASS — prompt refuted**

Method (identical to the gate that closed the sibling `autofit_sampler_database`, PyAutoFit#1508):
every script run from a **cleared** `output/`, under its workspace's
`config/build/profile_release.yaml`, env resolved by `autohands.env_config.build_env_for_script`
at workspace CWD, 1800s `mode=release` cap. Libraries at `main`: PyAutoFit `248ca971f`,
PyAutoArray `b808a9b1`, PyAutoGalaxy `7e3856dd`, PyAutoLens `d8f6bb3df`, PyAutoNerves `f6d6d52`.
Three workspace checkouts were **behind `origin/main`** and were synced first.

| Script | Result | Secs |
|---|---|--:|
| `autolens_workspace_test/scripts/interferometer/model_fit.py` | PASS | 78 |
| `autogalaxy_workspace/scripts/interferometer/features/pixelization/galaxy_reconstruction.py` | PASS | 70 |

The prompt states the autolens leg "reproduces on current `main`". It does not. No
non-positive-definite failure, no `LinAlgError`, in either.

**Note which numerical path each took.** `autolens_workspace_test`'s release profile *defaults*
`PYAUTO_DISABLE_JAX="1"`, and scripts opt back in with an in-file `ENV: jax` declaration.
`model_fit.py` has no such declaration, so it ran on **numpy** — release-faithful, but worth
knowing for a claim about inversion numerics, since JAX-on and JAX-off are different code paths.

### Incidental finding — a real defect, but NOT this prompt's

`galaxy_reconstruction.py` passes while emitting 4x
`RuntimeWarning: invalid value encountered in sqrt` from
`PyAutoArray/autoarray/inversion/inversion/abstract.py:859`:

```python
def reconstruction_noise_map_with_covariance(self):
    return np.sqrt(np.linalg.inv(self.curvature_reg_matrix))
```

`sqrt` is applied **elementwise to the whole inverse matrix**, whose off-diagonal entries are
covariances and are generally negative — so those entries are NaN *by construction*, for any
matrix, however well-conditioned.

**This is not evidence of a non-positive-definite matrix** and does not rescue the prompt's
hypothesis, despite looking exactly like it would. It is a separate defect: a property whose
docstring promises a matrix that "accounts for the covariance of the noise between pixels" returns
NaN wherever that covariance is negative. The 1D `reconstruction_noise_map` is unaffected — it
takes the diagonal, and `diag(sqrt(M)) == sqrt(diag(M))` — so the science path is correct; only
the covariance-aware consumer and the warning spam are hit. Worth its own PyAutoArray prompt.
