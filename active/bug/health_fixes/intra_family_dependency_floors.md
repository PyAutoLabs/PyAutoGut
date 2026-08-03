# `autolens[optional]` resolves an ancient autofit — intra-family deps have no version floors

Type: bug
Target: health_fixes
Repos:
- @PyAutoNerves
- @PyAutoArray
- @PyAutoFit
- @PyAutoGalaxy
- @PyAutoLens
- @PyAutoCTI
Difficulty: low
Autonomy: supervised
Priority: high
Status: draft

## Finding (2026-08-03, PyAutoHeart readiness RED)

`pyauto-heart verify_install` Check D (`pip install "autolens[optional]"`) FAILED
in the Release Integrate run (PyAutoHeart run 30788224561, job 91606144514),
sidecar `~/.pyauto-heart/verify_install.json` `2026-08-03T06:01:09Z`,
detail `pip rc=0 import rc=1`. It is one of the two legs holding the release RED.

The install succeeds; the import does not:

    [05:58:53] -> import autolens
    Traceback (most recent call last):
        import autolens; print(autolens.__version__)
    AttributeError: module 'autofit' has no attribute 'Latent'

Check D resolved **autofit 2026.4.30.582** (an April release, pulling
`autoconf 2026.7.15.1` with it) while autoarray / autogalaxy / autonerves came
in at `2026.8.2.1`.

### Root cause

`autolens[optional]` expands to
`autolens[jax]` -> `autogalaxy[jax]` -> `autofit[jax]` -> `autonerves[jax]`.

Every intra-family dependency in the five `pyproject.toml` files is a **bare
package name with no version floor** (`"autofit"`, `"autoarray"`,
`"autogalaxy"`, `"autonerves"`). When pip backtracks anywhere in that extras
chain it may walk the entire release history back to 2022 — and pip treats
*"version X does not provide the extra 'jax'"* as a **warning, not an error**,
so an ancient `autofit` carrying no `jax` extra is a legal solution. pip settles
there after ~22,600 lines of backtracking.

The metadata itself did not regress: `requires_dist` for autonerves / autofit /
autogalaxy is identical between `2026.7.29.2` (PyPI) and `2026.8.2.1`
(TestPyPI). The whole `2026.8.2.1` family is TestPyPI-only; PyPI's newest is
still `2026.7.29.2`.

### Why it passed locally and failed in CI

Check D builds its venv with the default `python3`. The `verify_install_release`
job calls `setup-python` for 3.11, then 3.12, then 3.13 — the last wins, so CI's
`python3` is **3.13**. Locally it is 3.12. Reproduced on both, same command,
same index args:

| interpreter | resolved autofit | `import autolens` |
|---|---|---|
| 3.12 | 2026.7.29.2 | passes (still has `Latent`) |
| 3.13 | **2026.4.30.582** | `AttributeError` |

Both are backtracked; 3.12 merely stops at a version that still has `Latent`.
This is a real user-facing defect, not a CI artefact — `pip install
autolens[optional]` from live PyPI today also silently walks the family back.

### Control test — floors fix it

Same command, same python3.13, floors added:

    pip install "autolens[optional]==2026.8.3.1.dev69801" \
        autofit>=2026.7.29.2 autogalaxy>=2026.7.29.2 \
        autoarray>=2026.7.29.2 autonerves>=2026.7.29.2

    -> autoarray 2026.8.2.1  autofit 2026.8.2.1
       autogalaxy 2026.8.2.1  autonerves 2026.8.2.1
    -> import autolens: OK

Without the floors the identical command lands on autofit 2026.4.30.582 and
raises.

## Task

1. Add `>=2026.7.29.2` floors to every intra-family dependency — base
   `dependencies` **and** the `[jax]` / `[optional]` extras — in
   PyAutoNerves, PyAutoArray, PyAutoFit, PyAutoGalaxy, PyAutoLens, and
   PyAutoCTI (`autofit`, `autoarray` are bare there too).
   This is a floor, not an exact pin — consistent with the floors-not-pins
   release design (PyAutoBuild#118/#120). A floor must name an *installable*
   version, so `2026.7.29.2` (live on PyPI, not yanked) is the right value.
2. Make Check D state which interpreter it used in its sidecar `detail`
   (`PyAutoHeart/heart/checks/verify_install.sh`, `check_d`). "Default
   `python3`" silently differing between CI (3.13) and local (3.12) is what hid
   this; the evidence should name the interpreter the way Check B's details do.

## Acceptance

- `pip install "autolens[optional]"` on python3.12 **and** python3.13 resolves
  the whole PyAuto family at the newest available release, and `import autolens`
  succeeds.
- Check D's sidecar detail names the interpreter version.
- Note: the floors only take effect once new wheels are published. The RED
  `verify_install` leg does not clear until a release rehearsal republishes to
  TestPyPI and Check D re-runs against those wheels.
