# Backport the per-script timeout: 6 of 10 smoke runners have no cap, and only 1 kills the process group

Type: maintenance
Target: ci
Repos:
- @PyAutoHands
- @autolens_workspace
- @autogalaxy_workspace
- @autofit_workspace
- @autofit_workspace_test
- @autogalaxy_workspace_test
- @autocti_workspace_test
Difficulty: medium
Autonomy: supervised
Priority: high
Status: formalised
Filed: 2026-08-23

Answers the blocking question left open by
[`run_smoke_copy_drift.md`](run_smoke_copy_drift.md) step 2 — *"does
`autolens_workspace_test`'s timeout/kill behaviour get promoted to everyone, or
does that repo keep a documented divergence?"* — which that prompt requires be
settled in writing **before any repo is touched**.

## Decision: promote, in two separable legs

The divergence is **not** a deliberate one worth documenting. It is the only
repo that has been bitten (issue #196) carrying the fix alone. Promote it — but
the promotion is two different changes with two different homes, and conflating
them is how a naive "make the copies identical" pass would go wrong:

- **Leg A — the kill timer.** Six runners enforce no wall-clock cap at all.
  They get one. This is a per-repo change to each runner copy.
- **Leg B — the process-group kill.** Exactly one runner in the whole
  organism kills the process group on expiry; **PyAutoHands' own authoritative
  executor does not**. This belongs in `build_util`, not in ten copies.

Leg B is the surprising half and the reason this prompt exists as its own task
rather than a bullet inside the drift prompt.

## Measured state

Measured on the checkouts below, not inferred. `run_smoke.py` in each repo's
`.github/scripts/`, plus `PyAutoHands/autohands/build_util.py`.

| Variant | Repos (HEAD) | Kill timer | Process-group kill |
|---|---|---|---|
| **workspace** (266 L) | autolens_workspace `1b24de6`, autofit_workspace `a05b431`, autogalaxy_workspace `5fdb0b2` | **none** | none |
| **workspace_test** (113 L) | autofit_workspace_test `d5d73ab`, autogalaxy_workspace_test `0a91883`, autocti_workspace_test `54aee5e` | **none** | none |
| **workspace_test + timeout** (193 L) | autolens_workspace_test `a6965a5` | yes, via `timeout_for(env)` | **yes** |
| **HowTo** (75 L delegator) | HowToLens `a3d8399`, HowToGalaxy, HowToFit | inherited from `build_util` | **none** (inherits the gap) |
| — | PyAutoHands `438d93e` `build_util.py` | yes, `timeout_for(env)` at :295 and :454 | **none** — `grep -rn 'start_new_session\|killpg\|getpgid' autohands/` returns nothing |

Two consequences the drift prompt's table did not capture:

1. **The gap is six repos wide, not three.** The drift prompt framed the
   timeout as a `workspace_test`-tier divergence. The three `workspace` copies
   (`subprocess.run(..., capture_output=True)` at `run_smoke.py:105`, script
   leg, and `:133`, notebook leg) carry **no `timeout=` argument either** —
   `grep -n timeout autolens_workspace/.github/scripts/run_smoke.py` returns
   nothing. They are as exposed as the `workspace_test` tier and are the gates
   on the three public workspaces.
2. **The group kill is missing from the authoritative executor.** `build_util`
   has the timer but uses plain `subprocess.run(timeout=...)`, which kills only
   the direct child. That is precisely the failure mode
   `autolens_workspace_test` documents in `run_one`: with output captured, the
   parent waits for the stdout pipe to reach EOF, and a grandchild that
   inherited that pipe holds it open after the child dies — so the "timeout"
   fires and the runner still hangs. The release mega-run and the entire HowTo
   tier route through `build_util` and are therefore still exposed to the hang
   that motivated the original fix.

## Why promote rather than document the divergence

The behaviour being withheld is the one that stopped smoke CI sitting at the
**6-hour GitHub Actions ceiling while reporting nothing since the last completed
script** (`autolens_workspace_test` issue #196). Every argument for the donor
repo having it applies unchanged to the other nine: same runner shape, same
captured-output pipe, same Actions ceiling, same scripts. There is no
repo-specific property that makes an uncapped run acceptable in
`autogalaxy_workspace_test` and unacceptable in `autolens_workspace_test`.

The cost of promotion is also already paid: `BUILD_SCRIPT_TIMEOUT` / 300s is
the organism-wide cap (`build_util.py:12`, `run_all.py:49`
`DEFAULT_TIMEOUT_SECS`, raised to 1800 for `mode=release` by PyAutoHeart's
`workspace-validation.yml`), and `timeout_for(env)` already exists in
`build_util` to resolve per-script profile overrides. Promotion adopts an
existing contract; it does not invent a cap.

## Task

Order matters: **Leg B first.** Landing the group kill in `build_util` means
the HowTo tier and the release run are covered without touching them, and Leg A
then has a `build_util` helper to delegate to rather than nine copies growing
their own `_kill_group`.

1. **PyAutoHands — `build_util`: add the process-group kill.** Give
   `execute_notebook` (`:292`) and `execute_script` (`:447`) the
   `start_new_session=True` + `os.killpg(os.getpgid(pid), SIGKILL)` treatment
   from `autolens_workspace_test/.github/scripts/run_smoke.py::run_one` /
   `_kill_group`. `subprocess.run(timeout=...)` cannot express this — both
   sites become `Popen` + `communicate(timeout=...)`. Preserve the existing
   report/`ScriptResult` timeout paths and `is_clean_skip_exit` handling
   exactly. Export `_kill_group` (unprefixed) so the workspace runners can
   import it instead of copying it.
2. **The three `workspace_test` copies** (autofit, autogalaxy, autocti): adopt
   the donor's `run_one` wholesale — `timeout_for(env)` with the
   `TIMEOUT_SECS` fallback shim, `Popen(start_new_session=True)`,
   `communicate(timeout=...)`, group kill, **return code 124**, and the
   `TIMEOUT (Ns)` status in both the per-entry line and the summary. These
   three are byte-identical to each other but for one docstring line, so it is
   the same patch three times. Do not "tidy" the docstring divergence in the
   same PR.
3. **The three `workspace` copies** (autolens, autofit, autogalaxy): same
   treatment for `run_script` (`:101`). The notebook leg needs it too, and
   does **not** get it from step 1: `execute_notebook` (`:120`) shells out to
   `jupyter nbconvert --execute` directly rather than delegating to
   `build_util`, so it inherits nothing. An uncapped notebook hangs the gate
   exactly as an uncapped script does. While in `autogalaxy_workspace`, drop
   the vestigial
   `_BUILD_DIR` line (`run_smoke.py:51`) — the last remaining real drift inside
   this variant, and item 4 of the drift prompt.
4. **HowTo tier: no change.** The 75-line delegators inherit both legs from
   step 1. Confirm this by inspection and record it; do not open PRs.
5. Report back into `run_smoke_copy_drift.md`: its step 2 blocking question is
   answered here, and its step 4 (`_BUILD_DIR`) is absorbed into step 3 above.

One PR per repo (7 PRs), PyAutoHands first and merged before the workspace PRs
that depend on the exported helper.

## Acceptance

- `grep -rn "start_new_session" PyAutoHands/autohands/build_util.py` is
  non-empty, and a script that forks a grandchild holding stdout is reaped at
  the cap rather than hanging to the Actions ceiling.
- Every one of the 10 `run_smoke.py` copies either enforces a per-script cap
  with a process-group kill, or delegates to a `build_util` path that does.
- A timeout is reported as `TIMEOUT (Ns)` with exit 124 and the cap actually in
  force — never as an ordinary `FAIL (exit -9)`, which would mislabel "raise
  the cap or SLOW-skip it" as "this script is broken".
- `BUILD_SCRIPT_TIMEOUT=5` against a deliberately slow script fails fast in
  each touched repo; the release profile's 1800s override still applies.
- No repo loses behaviour: `autolens_workspace_test` still enforces its cap,
  and the three `workspace` copies still run their notebook leg.

## Provenance

Spun out of `run_smoke_copy_drift.md` (filed 2026-07-25, re-scoped 2026-08-05),
whose re-scoped step 2 makes this decision a precondition for any code change.
The donor implementation's own history: `autolens_workspace_test` #196 (the
6-hour hang) and PyAutoHands #226/#227 (per-script profile cap resolution
parent-side, which is why the donor resolves `timeout_for(env)` rather than
reading the module global).
