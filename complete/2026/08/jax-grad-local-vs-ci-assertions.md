- issue: https://github.com/PyAutoLabs/autolens_workspace_test/issues/260
- completed: 2026-08-22
- library-pr: https://github.com/PyAutoLabs/PyAutoArray/pull/471 (merged 2a6a416)
- workspace-pr: none — the workspace needed no change

Three `autolens_workspace_test` jax_grad scripts failed assertions locally that
PASS in CI on the same commit. **Verdict: not numpy, and not a source defect —
`should_simulate` reused a dataset written by an earlier capped run.** Diagnosed
and fixed entirely from a cloud session; the laptop that filed the report was
never available.

**The prime suspect was falsified, cleanly.** The prompt named numpy 2.2.6 local
vs 2.4.6 in CI. `lp.py` (the control) is **byte-identical** across numpy 2.2.6 /
2.4.6 / 2.5.2 — both log-likelihoods and all 40 gradient entries — and identical
again across 1-core vs 4-core, which also kills thread-dependent reduction order
in the XLA CPU backend. numpy was never mechanically able to cause it: the
likelihood runs through JAX/XLA and numpy only does the FD bookkeeping
afterwards. The suspect was a coincidence in a `pip freeze` diff.

**Root cause.** `PyAutoArray util/dataset_util.py should_simulate` was
existence-only and asymmetric: it force-regenerated under
`PYAUTO_SMALL_DATASETS=1` but had no check on the full-resolution path. Since
`dataset/**` is gitignored, CI clones fresh and always simulates — it **cannot**
hit this. Locally the directory persists forever, and because
`PYAUTO_SMALL_DATASETS=1` is the smoke default for nearly every OTHER script, one
earlier run rewrites the FITS at 16x16 and every later `full_datasets` run loads
them silently.

**Why "not the small-datasets cap" was ruled out wrongly.** That check verified
the *resolved env*, which was genuinely correct — `full_datasets` does unset the
var. The damage was done by an earlier run and baked into the FITS on disk. No
amount of env-resolution checking can see it. A good check pointed one layer away
from the problem.

**Reproduction, from a clean checkout.** fresh full (262080 B) -> PASS; one
`PYAUTO_SMALL_DATASETS=1` run -> 5760 B, passes; next `full_datasets` run -> all
three failures; `rm -rf` -> PASS. `pixelization.py` matched the 2026-08-04 report
to **11 significant figures** (`-8354.484097833672` vs `-8354.484097835004`) and
`regularization.py`'s tolerance vector matched **exactly** (`[0.031, 0.008,
0.003]`).

**No tolerance was changed.** All three assertions did their job on a genuinely
invalid dataset. `assert_eager_jit_consistent`'s `rtol=1e-10` looked
indefensibly tight and was the obvious thing to widen — it is *vindicated*: it is
a constant-folding detector and it correctly refused to certify gradients from a
corrupt input. Widening it would have deleted a working alarm and left the defect.

**TRAPS**
- A shape-based regime check MUST key on `data.fits` by name. PSF kernels are
  legitimately tiny at full resolution (11x11 in 49 places in autolens_workspace)
  and `dataset/cluster/test/psf.fits` is 5760 B — byte-identical in size to a
  capped `data.fits`. A "first FITS in the directory" glob would delete every
  PSF-carrying dataset on every run.
- Use `== (16,16)`, never `<=`. The cap emits *exactly* the cap shape
  (`mask_2d.py:371-373`), so widening a **destructive rmtree predicate** buys no
  detection and only risks real data.
- There is no pixel scale in these FITS headers (only
  `SIMPLE/BITPIX/NAXIS/NAXIS1/NAXIS2`) — it is supplied by the caller at load
  time. Any regime check that wants pixel scale cannot have it.
- "Unknown regime" must mean "leave it alone", never "delete".
- Adversarial review earned its keep: two of these three would have shipped a
  worse bug than the one being fixed.

**Scope shipped: imaging only.** Point-source and weak-lensing datasets are JSON
with no FITS; interferometer datasets keep their shape under the cap (visibility
count fixed by the uv file, real-space grid capped behind it) so a capped run
writes identical NAXIS with different values — and fails **silently**, with no
assertion to trip. Both regress to existence-only, stated in the docstring.

**Follow-ups filed (not absorbed)**
- PyAutoNerves#153 — stamp the regime at the single FITS writer funnel
  (`fitsable.py:89` `output_to_fits`, the only such definition in the stack, so a
  stamp there is truthful by construction and needs zero call-site changes). The
  only discriminant that can catch the silent interferometer case. Kept separate
  because it changes a header card on every FITS the stack writes.
- PyAutoArray#470 — the small-datasets branch `rmtree`s
  `dataset/point_source/simple`, which is **committed and allowlisted** at
  `.gitignore:13`, replacing it with output from a solver that short-circuits to a
  fixed position pair under the cap.
- UNFILED: `autolens_workspace_test/.github/scripts/smoke_install.sh:9`'s
  `pip install "jax<0.7" "jaxlib<0.7"` downgrades jax to 0.6.2 and conflicts with
  autonerves' `jax<0.11.0,>=0.7.0`; the install only lands on the intended 0.10.2
  because the next line's `[optional]` extras pull it back up. CI is right by
  accident — reordering those lines would silently drop smoke onto jax 0.6.2.

**Method note.** The `lp.py` CONTROL is again what made this tractable — the same
lesson the parent task (PyAutoHands#226) recorded. A control that is known-green
elsewhere converts "three mysterious failures" into "the environment is lying".

## Original prompt

# jax_grad scripts fail assertions locally that PASS in CI

Type: bug
Target: autolens_workspace_test
Repos:
- autolens_workspace_test
Difficulty: medium
Autonomy: supervised
Priority: medium
Status: formalised

Running the `jax_grad` scripts locally under the resolved smoke profile produces
deterministic assertion failures in scripts that **pass in CI on the same commit**.
Found while measuring script durations for PyAutoHands#226.

## Evidence

Run via `env_config.build_env_for_script` with the workspace root as CWD (i.e. the
exact env the runner builds — `PYAUTO_SMALL_DATASETS` unset, `PYAUTO_DISABLE_JAX`
unset, `PYAUTO_TEST_MODE=2`, verified by printing the resolved env):

| script | local | CI (run 30858578587 / 30790463134) |
|---|---|---|
| `imaging/jax_grad/lp.py` | **FAIL 41.3s** | **PASS 39.6s / 40.0s** |
| `imaging/jax_grad/knn.py` | PASS 141.6s | PASS 200.0s / 175.8s |
| `imaging/jax_grad/pixelization.py` | **FAIL 57.5s** | PASS 244.8s (06:31Z) |
| `imaging/jax_grad/regularization.py` | **FAIL 131.5s** | (import gap, then TIMEOUT) |
| `point_source/jax_grad/gradient.py` | PASS 665.9s | TIMEOUT (300s cap) |

`lp.py` is the decisive case: it **passes in CI on both runs** and fails locally.

Failures are deterministic and bit-identical across repeated runs, e.g.
`pixelization.py`:

```
AssertionError: Eager (-8354.484097835004) and jitted (-8354.55843260181) evaluations
disagree — possible pure_callback constant-folding; do not trust jitted gradients.
```

(relative difference ~8.9e-6 against `assert_eager_jit_consistent`'s `rtol=1e-10`).

`lp.py` fails with `All source-parameter gradients are ~zero — NNLS zeroed the source`;
`regularization.py` with an AD-vs-FD mismatch marginally over tolerance
(`abs_err=[0.045, 0.042, 0.057]` vs `tolerance=[0.031, 0.008, 0.003]`).

## What is ruled out

- **Not the small-datasets cap.** `full_datasets` correctly unsets
  `PYAUTO_SMALL_DATASETS`; verified by resolving the env directly rather than
  inferring from mask sizes.
- **Not a JAX version difference.** Local jax/jaxlib are 0.10.2 — identical to CI.
- **Not flake.** Repeated runs give bit-identical values.

Prime remaining suspect: **numpy 2.2.6 local vs 2.4.6 in CI**, or another local venv
package differing from the CI install set. Not yet confirmed.

## Why it matters

This is an active trap for anyone validating these scripts locally. During #226 it
looked exactly like two fresh correctness regressions on current main
(`pure_callback` constant-folding, and an FD tolerance breach). Only running a
**control** — `lp.py`, known-passing in CI — revealed that the local environment
itself produces the failures, so none of the three local failures were evidence of
source defects.

Whatever the cause, either the scripts or the documented local-run recipe should make
this reproducible, so a local FAIL means something.

## Suggested scope

1. Bisect the local-vs-CI package delta (start with numpy 2.2.6 -> 2.4.6) against
   `lp.py`, the cleanest discriminator.
2. If numpy is the cause, decide whether the tolerances are under-specified for the
   supported numpy range, or the local env should be pinned to the CI set.
3. Record the outcome in the workspace's local-run instructions.

<!-- Split out of PyAutoHands#226 on 2026-08-04; that task deliberately did not absorb
     this, and explicitly barred setting any timeout budget from local numbers. -->
