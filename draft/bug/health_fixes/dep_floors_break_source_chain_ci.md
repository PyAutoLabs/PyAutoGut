# Intra-family dep floors break every workspace's source-chain smoke CI

Type: bug
Target: health_fixes
Repos:
- autolens_workspace
- HowToLens
- autogalaxy_workspace
- autofit_workspace
- autolens_workspace_test
- autogalaxy_workspace_test
- autofit_workspace_test
- autocti_workspace_test
- HowToFit
- HowToGalaxy
- PyAutoHeart
Difficulty: small
Autonomy: supervised
Priority: URGENT — main is broken
Status: formalised

## The break

The six `intra-family-dep-floors` PRs (PyAutoLens#687) merged in a 15-second
burst on 2026-08-03:

| PR | merged |
|---|---|
| PyAutoArray#432 | 18:08:00Z |
| PyAutoFit#1446 | 18:08:03Z |
| PyAutoGalaxy#547 | 18:08:06Z |
| PyAutoLens#688 | 18:08:09Z |
| PyAutoCTI#104 | 18:08:12Z |
| PyAutoHeart#133 | 18:08:15Z |

Every workspace smoke job has failed at the **install** step since. Smoke never
runs — the job dies before it. Observed on autolens_workspace#460 and
HowToLens#65 at 18:20Z:

```
ERROR: Cannot install autofit==1.0.dev0 and autonerves 1.0.dev0
       (from /home/runner/work/.../PyAutoNerves)
       because these package versions have conflicting dependencies.

The conflict is caused by:
    The user requested autonerves 1.0.dev0 (from .../PyAutoNerves)
    autofit 1.0.dev0 depends on autonerves>=2026.7.29.2

ERROR: ResolutionImpossible
```

Proof it is the floors and not the workspace PRs: autolens_workspace#459 and
#453 both show **green** smoke — their runs are timestamped BEFORE 18:08. Re-run
either and it should go red. Confirm this before doing anything else (control
test).

## Mechanism

`<workspace>/.github/scripts/smoke_install.sh` installs the whole chain from
LOCAL SOURCE in one resolver pass:

```bash
pip install ./PyAutoNerves ./PyAutoFit ./PyAutoArray ./PyAutoGalaxy ./PyAutoLens
```

Each builds via `setup.py`, which reads:

```python
version = os.environ.get("VERSION", "1.0.dev0")
```

CI sets no `VERSION`, so every local package is `1.0.dev0`. PyAutoFit's
pyproject now declares `autonerves>=2026.7.29.2` (line 31, plus
`autonerves[jax]>=2026.7.29.2` at line 71). `1.0.dev0` cannot satisfy
`>=2026.7.29.2`, and pip has both constraints in one pass → ResolutionImpossible.

## Blast radius — 10 repos carry an affected `smoke_install.sh`

`HowToFit`, `HowToGalaxy`, `HowToLens`, `autocti_workspace_test`,
`autofit_workspace`, `autofit_workspace_test`, `autogalaxy_workspace`,
`autogalaxy_workspace_test`, `autolens_workspace`, `autolens_workspace_test`.

The shared runner is `PyAutoHeart/.github/workflows/smoke-tests.yml`
(step "Install (base + the workspace's own epilogue)", line 120), which calls
each workspace's epilogue. So the fix may belong in the shared workflow rather
than in 10 copies — check before fanning out.

## Do NOT loosen or revert the floors

They fixed a real Heart RED (`install verification FAILED (testpypi; checks D)`)
with a proven control test: without floors pip backtracks to autofit
2026.4.30.582 and raises `AttributeError: module 'autofit' has no attribute
'Latent'`. The floors are correct for PUBLISHED wheels. The gap is that they
were verified against built wheels + `--find-links` + published versions, which
never exercised the local-source `1.0.dev0` install path that CI uses.

Note #687's own `do-not` warned that a floor "makes a local 1.0.dev0 wheel build
unsatisfiable" — but scoped that to SELF-referential extras. This is a
CROSS-package floor hitting local source installs; the same failure mode, a case
the task did not anticipate.

## Fix hypothesis — VERIFY IT, do not just apply it

Export a `VERSION` at or above the floor for the source installs, so local
builds satisfy the cross-package floors:

```bash
VERSION=2026.7.29.2 pip install ./PyAutoNerves ./PyAutoFit ./PyAutoArray ...
```

Open questions the investigation must settle:

1. Does one `VERSION` for the whole chain work, or does each package need
   stamping separately? They are built in one pip invocation.
2. Pick the value deliberately. Exactly `2026.7.29.2` satisfies the floors but
   is a lie about what the code is. A high sentinel (`9999.1.1`) is honestly
   "not a release" but could mask a genuine floor violation later. Decide and
   record why.
3. `VERSION` also stamps `*.egg-info` in the checkout — #687 hit this locally
   ("restore with `python3 setup.py egg_info`"). Confirm CI's ephemeral
   checkouts make that irrelevant.
4. Does `pip install --no-deps` for the local chain plus a separate third-party
   pass work better? It sidesteps the resolver entirely but risks dropping real
   transitive deps — measure, don't assume.

## Verification required

- Reproduce RED first on an unchanged workspace branch (control test). A fix
  "verified" without first seeing the failure proves nothing.
- Green smoke on BOTH matrix legs (3.12 AND 3.13) — the epilogue branches on
  `PYTHON_VERSION` and the legs install different extras.
- Confirm the installed chain is the LOCAL source, not PyPI wheels: assert
  `autofit.__file__` resolves under the checkout. A fix that silently switches
  CI to released wheels would go green while destroying what smoke tests.
- Re-run smoke on autolens_workspace#459 and #453 and confirm they return green.

## Blocked on this

- autolens_workspace#460 + HowToLens#65 (`missing-auto-simulate-guards`, #455) —
  both red solely from this; their scripts are verified green locally under real
  smoke envs. Merge once CI is fixed.
- Any workspace PR opened after 18:08Z on 2026-08-03.
