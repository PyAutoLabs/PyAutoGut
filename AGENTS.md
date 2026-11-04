# PyAutoCTI Workspace Test — Agent Instructions

This is the integration-test suite for **PyAutoCTI**, run in CI to verify the core library works
end-to-end. It is **not** a user-facing workspace — see `../autocti_workspace` for examples and
tutorials. These are the canonical, agent-agnostic instructions for this repo.

Dependencies: `autocti`, `autofit`, `autoarray`, and **arcticpy** (source-only C++ sdist; the
full install recipe is in `PyAutoCTI/AGENTS.md` §arcticpy, and CI runs it from
`PyAutoHeart/.github/actions/install-arcticpy`). Short form:

```bash
sudo apt-get install -y libgsl-dev
pip install --upgrade pip setuptools wheel     # setuptools is a BUILD dep; 3.12+ venvs omit it
pip install numpy cython scipy matplotlib
pip install arcticpy==2.6 --no-build-isolation --no-deps
```

## Repository Structure

```
scripts/                     Integration-test scripts run in CI
  dataset_1d/model_fit.py    1D calibration: simulate -> factor-graph fit -> aggregator round-trip
  imaging_ci/model_fit.py    2D charge injection: simulate -> factor-graph fit -> result inspection
  dataset_1d/likelihood/pins.py   Pinned log-likelihood literals (1 and 2 trap species)
  imaging_ci/likelihood/pins.py   Pinned log-likelihood literals (parallel, serial, parallel+serial)
  plot/subplots.py           Drives the autocti.plot function surface to files
legacy/                      Euclid VIS heritage (2022-2023, pre-resurrection API — not runnable;
                             see legacy/README.md)
config/                      Current PyAutoCTI config (mirrors autocti_workspace)
config/build/profile_smoke.yaml   Per-script env for smoke runs (PYAUTO_TEST_MODE=2 defaults)
smoke_tests.txt              The curated smoke list (small on purpose)
```

## Running

```bash
python .github/scripts/run_smoke.py     # the smoke list, with profile_smoke.yaml applied
python scripts/dataset_1d/model_fit.py  # one script, real search (no env applied)
```

CI runs the smoke list through PyAutoHeart's reusable smoke workflow (thin caller in
`.github/workflows/smoke_tests.yml`, chain `PyAutoNerves PyAutoFit PyAutoArray PyAutoCTI`). The
arcticpy build is **not** in `.github/scripts/smoke_install.sh` any more: the caller passes
`arcticpy: true` and Heart runs its own `install-arcticpy` action before the epilogue, so the
recipe has one owner instead of a copy per repo. `smoke_install.sh` now holds only the
workspace-specific chain install.

## Conventions

- Keep `smoke_tests.txt` a **small curated subset** — do not mass-promote scripts.
- Integration scripts are self-contained (simulate their own data, small shapes) and single-trap.
- The test-mode knob is `PYAUTO_TEST_MODE` (`2` bypasses sampling); `PYAUTOFIT_TEST_MODE`
  does not exist.
- Never edit `legacy/` — it is preserved Euclid VIS history.

## Likelihood pins

`scripts/*/likelihood/pins.py` pin the absolute value of `analysis.log_likelihood_function` at
`rtol=1e-8`, the same pattern as the `jax_likelihood/` pins in the lens and galaxy test
workspaces. A failing pin means the CTI likelihood changed value: find out why before touching it.

- A pin moves only with a dated comment above it naming the PR and the cause, for example
  `# re-pinned 2026-12-01: arcticpy 2.7 DR2 well-filling model (PyAutoCTI#NNN)`. Record the old
  and new values in the PR. Never loosen the tolerance to make a pin pass.
- The arcticpy version is part of every pin's provenance (`arcticpy 2.6` in the comment). A new
  arcticpy release is expected to move every literal, so re-pin all of them in one PR.
- The scripts print every value, so a CI log has the new numbers for a re-pin.

<!-- repos_sync:history:begin -->
## Never rewrite history

Never rewrite pushed history on any repo with a remote — no `git init` over a
tracked repo, no force-push to `main`, no fresh-start "Initial commit", no
`filter-repo` / `filter-branch` / `rebase -i` on pushed branches. To get a
clean tree: `git fetch origin && git reset --hard origin/main && git clean -fd`.
<!-- repos_sync:history:end -->

<!-- repos_sync:deliverable:begin -->
## Sessions end at their deliverable

A session ends when it reports its deliverable — never arm anything that
outlives the turn to wait for CI, a review or a merge: no `send_later`, no
`subscribe_pr_activity`, no `CronCreate`, no `ScheduleWakeup`, no `/loop`, no
`RemoteTrigger` create/update/run. Judge once, report, stop; the human re-runs
`/prm` (or the batch review) when it is green. Measured: five batch members
armed hourly check-ins on 2026-08-31, and a mobile `/prm` re-armed a 60-minute
`send_later` hourly all night on 2026-09-03 with no task active, draining usage.
<!-- repos_sync:deliverable:end -->

<!-- repos_sync:filing:begin -->
## Where to file

Questions, help with code or an analysis, ideas, bug reports and results from a
user or collaborator — or an agent acting for one — go to
<https://github.com/orgs/PyAutoLabs/discussions> in the matching category
(Help & Questions, Ideas & Proposals, Bugs & Errors, Show and tell;
Announcements is maintainers-only), never to this repo's Issues. An agent never
runs `gh issue create` for such a report: it drafts the title, category and
body and hands them to the human (sessions cannot create Discussions). Only the
development flow — Mind prompt → `/start_dev` → `/create_issue` → one issue per
task → PR — opens issues here. Why: `PyAutoMind/policy/community_surface.md`.
<!-- repos_sync:filing:end -->

<!-- repos_sync:standards:begin -->
## Shared standards

Before changing a shared interface, consult the applicable
[organism standard](https://github.com/PyAutoLabs/PyAutoBrain/blob/main/docs/standards.md)
on demand, identify affected consumers, and validate their adoption. Change
generated guidance at its canonical source and regenerate.
<!-- repos_sync:standards:end -->
