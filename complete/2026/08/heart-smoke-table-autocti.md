- completed: 2026-08-24
- issue: https://github.com/PyAutoLabs/PyAutoHeart/issues/172
- prs:
  - https://github.com/PyAutoLabs/PyAutoHeart/pull/173 (merged)
- summary: |
    CTI CI standardisation Phase 6, task 2 of 3. Heart's local smoke runner had
    no autocti entry and no PyAutoCTI import name, so neither CTI suite could be
    run without pushing to CI. Added both workspaces, with the arcticpy recipe
    factored into one shell script the CI action and smoke.py both execute.
    Both suites now run locally: 3/3 PASS each.

## The design question, and why two of the three options were taken

The task offered three ways to give the local runner arcticpy. Two of them turn
out to answer *different* questions, so both were taken and only one was
rejected:

| question | answer |
|---|---|
| where does the recipe live? | Extract the action's five run-steps into `.github/actions/install-arcticpy/install_arcticpy.sh`. The action calls it via `${{ github.action_path }}`; `smoke.py` calls the same file from the Heart checkout. |
| what triggers it locally? | A per-workspace `arcticpy: true` key in the `smoke:` block, mirroring the input the CTI CI callers already pass. |

Rejected: a Python leg in `smoke.py` mirroring the recipe — the divergence #170
was created to end.

The extraction is safe for the action's cross-repo reach, which was the whole
reason a composite action was the right shape: an action is downloaded with its
entire directory, so `${{ github.action_path }}/install_arcticpy.sh` resolves for
a consumer with no PyAutoHeart checkout. All three consumers (`lib-tests.yml`
twice, `smoke-tests.yml`) call it with **no `with:` block at all**, so nothing at
any call site changed.

The human was asked one question — how far the local runner should go on a
machine without arcticpy — and chose "build it, but never apt". So the local leg
proves the GSL headers are present and fails with the platform's install line
rather than reaching for sudo: a dev command must not mutate system packages, and
`apt-get` does not exist on macOS at all.

## The pin had quietly re-acquired two copies

#170 reduced four copies of the recipe to one. Extracting it surfaced that the
`2.6` **pin** had meanwhile grown back to three sites:

- `action.yml`'s `version` input `default: "2.6"`
- `.github/workflows/arcticpy-action.yml`'s `version: ${{ inputs.version || '2.6' }}`

The second is the one that bites: after a pin bump the **self-test would have
gone on building the old version** — the one workflow whose entire job is to
prove a recipe change works would have been testing the wrong thing. Both now
defer to the script's single default, so there is exactly one executable `2.6` in
the tree.

## Two defects found by running it, not reading it

**1. The GSL probe was broken in precisely the way that matters.** The first cut
used `ls a b c`, which exits non-zero when *any* operand is missing. GSL lives in
exactly one prefix on any given machine — so the check reported the headers
absent on every machine that actually has them, and refused to build. It now
tests each prefix independently, and the list is overridable via
`ARCTICPY_GSL_PREFIXES`, which also serves the no-root header workaround the CTI
library's AGENTS.md documents.

**2. `pip check` can NEVER pass in a CTI environment.** The preflight built a
perfect environment and then destroyed it:

```
arcticpy 2.6 has requirement numpy~=1.21, but you have numpy 2.5.2.
```

arcticpy declares `numpy~=1.21` and is installed with `--no-deps` **deliberately**
— honouring it downgrades numpy below 2.0 and breaks the rest of the stack. So
that metadata is permanently unsatisfied and `pip check` reports it every single
time. Without handling this, `arcticpy: true` would have been inert: the
environment builds, the preflight kills it, nothing runs.

The preflight now tolerates exactly that one line, and only for a workspace that
declared `arcticpy: true`. Any other broken requirement still fails, and the
arcticpy line is *not* tolerated for a workspace that never asked for arcticpy.

Neither defect was visible by inspection. Both came from the task's own
instruction to verify by actually running it.

## The tenant firewall caught a third, in review

CI's pytest job failed *after* all 602 tests passed, on
`repos_sync.py --check --only "tenant firewall (organ code)"`: three satellite
repo names had leaked into organ code. `tests/test_smoke.py`'s own fixture
comment states this rule, and it was still violated.

- `heart/smoke.py` and `install_arcticpy.sh` are **unlisted**, where any instance
  fact is drift. Both were prose in comments and carried no weight; reworded.
- `tests/test_repo_config.py` is allowlisted, but only for `{PyAutoCTI,
  autocti_workspace, autocti_workspace_test}`; the new chain assertion added
  `PyAutoArray` and `PyAutoFit`. Rather than grow the entry — the allowlist's own
  comment says never to do that casually — the assertion now goes through
  `import_names` and compares package names. It says the same thing and
  additionally proves every chain repo resolves in the map, so it is a better
  test than the one it replaced.

Worth recording how it was verified: the checker **silently skips an organ
directory it cannot find**, and this session's checkout is lowercase
`pyautoheart`, so running it against the working root returned a vacuous OK.
Re-run with `PyAutoHeart` symlinked at the expected casing it reported OK for
real — and still reported the mismatch when a fact was deliberately planted, so
the OK is not an artefact of the check skipping the file.

## Verified — the acceptance criterion was "run it", and it was run

Python 3.12, environments prepared from scratch by the local runner:

| suite | result |
|---|---|
| `pyauto-heart smoke autocti_test` | 3/3 PASS — `dataset_1d/model_fit.py` 12.3s, `imaging_ci/model_fit.py` 8.0s, `plot/subplots.py` 11.1s |
| `pyauto-heart smoke autocti` | 3/3 PASS — `dataset_1d/modeling/start_here.py` 30.1s, `features/species_x3.py` 27.6s, `imaging_ci/modeling/start_here.py` 159.1s |

Both cold (datasets simulated from scratch). The `autocti` suite's AGENTS.md
records 132 s in CI; 217 s here reflects a slower container, not a regression.

Unit tests: **602 pass** (587 pre-existing + 15 new). The new coverage pins the
config surface, the fingerprint's sensitivity to the shared recipe, the
before-the-epilogue ordering, and — using the *real* script — the GSL probe's
accept/refuse/never-sudo behaviour plus all four `pip check` tolerance cases.

CI: the `arcticpy-action.yml` self-test triggers on
`.github/actions/install-arcticpy/**`, so it exercised the extracted script
end-to-end on 3.12 and 3.13.

## Loose end, unchanged and still needing a normal checkout

Branch deletion is impossible from a cloud session — verified again here rather
than assumed: `git push origin --delete` dies with `send-pack: unexpected
disconnect`, then prints "Everything up-to-date" and **exits 0**, while
`git ls-remote` still shows the branch. The twelve merged branches carried into
this phase are now **fourteen** (adding
`autocti_workspace/feature/autocti-workspace-navigator-check` and
`autocti_assistant/feature/wiki-currency-check-version-gate`, plus this task's
`PyAutoHeart/feature/heart-smoke-table-autocti`, now merged — so fifteen). They need `/repo_cleanup` or a normal checkout.

## Original prompt

# Heart's local smoke runner cannot run any CTI workspace — no autocti entry

Type: maintenance
Target: pyautoheart
Repos:
- @PyAutoHeart
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised
Filed: 2026-08-24
Issued: 2026-08-24

`PyAutoHeart/heart/smoke.py` is the local smoke runner — "one isolated
environment per workspace, prepared from the workspace-owned installer", the
local mirror of what CI does. Which workspaces it can prepare is declared in
`config/repos.yaml` under the `smoke:` block, and **the CTI repos are absent
from it entirely**:

```yaml
smoke:
  import_names:
    PyAutoNerves: autonerves
    PyAutoFit: autofit
    PyAutoArray: autoarray
    PyAutoGalaxy: autogalaxy
    PyAutoLens: autolens          # <- no PyAutoCTI
  workspaces:
    autofit: {directory: autofit_workspace, chain: [...]}
    autogalaxy: {...}
    autolens: {...}
    autolens_test: {directory: autolens_workspace_test, chain: [...]}
    euclid: {...}
    howtolens: {...}              # <- no autocti, no autocti_test
```

So `pyauto-heart smoke autocti` cannot work, and neither can a local smoke run of
`autocti_workspace_test` — the only way to exercise CTI smoke is to push and let
CI do it. That is a slow loop for the repo group that has just acquired two smoke
suites.

## Why it matters now

As of 2026-08-24 there are **two** CTI smoke surfaces:

- `autocti_workspace_test` — its long-standing suite (3 scripts, ~20 s).
- `autocti_workspace` — new as of autocti_workspace#28 (3 curated scripts,
  ~132 s cold), the repo's first CI.

Both run in CI through PyAutoHeart's reusable `smoke-tests.yml`. Neither can be
run through Heart's *local* runner, so the Brain/Heart local loop has a blind
spot exactly where new coverage just landed.

## Work

1. **Add `PyAutoCTI: autocti` to `smoke.import_names`.** The block's docstring
   calls it "the repo -> import-package map the preflight proves", so the
   preflight cannot currently prove a CTI environment at all.
2. **Add the two workspace entries** with the correct chain
   (`[PyAutoNerves, PyAutoFit, PyAutoArray, PyAutoCTI]` — matching what both
   repos' CI callers declare; autocti does **not** depend on autogalaxy/autolens):
   ```yaml
   autocti:      {directory: autocti_workspace,      chain: [PyAutoNerves, PyAutoFit, PyAutoArray, PyAutoCTI]}
   autocti_test: {directory: autocti_workspace_test, chain: [PyAutoNerves, PyAutoFit, PyAutoArray, PyAutoCTI]}
   ```
3. **Handle arcticpy.** This is the real design question, and the reason this is
   not a two-line config edit. `import autocti` hard-requires arcticpy, which is
   not a pip dependency: source-only C++ sdist, needs `libgsl-dev` + a toolchain,
   and its own requirements downgrade numpy below 2.0. In CI this is solved —
   `PyAutoHeart/.github/actions/install-arcticpy` owns the canonical recipe and
   the single `arcticpy==2.6` pin, and the workspace callers pass `arcticpy: true`.
   A **composite action cannot be invoked from `heart/smoke.py`**, so the local
   runner needs an equivalent. Decide deliberately between:
   - factoring the recipe into a shell script that both the action and
     `smoke.py` call (keeps one owner, adds a file);
   - a small Python leg in `smoke.py` that mirrors it (risks the exact
     divergence the action was created to end — the recipe had drifted into four
     copies before 2026-08-24);
   - a per-workspace `arcticpy: true` flag in the `smoke:` block that
     `smoke.py` honours.

   **Whatever is chosen, there must remain exactly one place the recipe and the
   `2.6` pin live.** Re-creating a second copy would undo PyAutoHeart#170.
4. **Verify by actually running it** — prepare a CTI environment through the
   local runner and run both suites, not just "the config parses".

## The recipe, for reference (verified 2026-08-24 by building it)

```bash
sudo apt-get install -y libgsl-dev
pip install --upgrade pip setuptools wheel   # BUILD deps: --no-build-isolation
pip install numpy cython                     #   will not supply these
pip install scipy matplotlib                 # RUNTIME deps --no-deps suppresses
pip install arcticpy==2.6 --no-build-isolation --no-deps
python -c "import arcticpy; from importlib.metadata import version; print(version('arcticpy'))"
```

Two traps that cost time if rediscovered: `--no-deps` suppresses arcticpy's
*runtime* imports too (`arcticpy/read_noise.py` imports `scipy` **and**
`matplotlib`, and `__init__.py` imports it), and **arcticpy exposes no
`__version__` attribute** — `arcticpy.__version__` raises `AttributeError` on a
perfectly healthy install.

## Context

`PyAutoMind/complete/2026/08/arcticpy-install-standardisation.md` — why the
recipe has one owner and what breaks when it does not.
