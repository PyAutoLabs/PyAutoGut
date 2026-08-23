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
Status: implemented
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
2. **The group kill is missing from the authoritative executor** — but it is a
   resource leak there, not a hang. `build_util` has the timer and uses plain
   `subprocess.run(timeout=...)`, which kills only the direct child.

   > **Corrected 2026-08-23, measured.** An earlier draft of this prompt
   > claimed the release mega-run and the HowTo tier were exposed to the same
   > unbounded hang. They are not. On POSIX `subprocess.run` handles its own
   > `TimeoutExpired` with `process.kill()` then `process.wait()` on the direct
   > child only (CPython `subprocess.py`; it does **not** re-`communicate`, so
   > it never blocks on an inherited pipe). Measured: with the cap set to 3s it
   > raised at 3.0s. What it *does* leave behind is the grandchild — measured
   > at **1 surviving process**, running on for its full lifetime. Over a
   > mega-run of hundreds of scripts those accumulate against every script that
   > follows, each holding whatever memory and GPU it had.

   So Leg B is worth doing on its own merits, but it is **not** the urgent
   half. Leg A is.

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

## Status — implemented 2026-08-23

All seven repos pushed to `claude/backport-per-script-timeout-r3w1sv`; no PRs
opened. Step 4 (HowTo) verified by inspection and correctly needed no change.

| Repo | Change |
|---|---|
| PyAutoHands | `run_capped` + public `kill_group`; both executors switched |
| autofit_workspace_test, autogalaxy_workspace_test, autocti_workspace_test | donor `run_one` adopted; imports `timeout_for`/`kill_group` |
| autolens_workspace, autogalaxy_workspace, autofit_workspace | both legs capped; `_BUILD_DIR` dropped; all three byte-identical again |
| HowToLens, HowToGalaxy, HowToFit | none needed — `run_python.py` → `execute_scripts_in_folder` → the now-capped `execute_script` |

Evidence, measured on the runner files themselves rather than argued:

- **Before**, `autofit_workspace_test`'s runner on a two-entry suite whose
  second script spawns a grandchild and exits, with `BUILD_SCRIPT_TIMEOUT=4`:
  printed `::group::hangs.py` and nothing further, still hung when the harness
  killed it at 30s. The cap was ignored because there was none. That is the
  issue #196 signature exactly.
- **After**: `[TIMEOUT (4s)] hangs.py — 4.0s`, exit 1, zero surviving
  grandchildren.
- The `workspace` variant reproduces the same on both legs, including a
  `jupyter` that hangs and forks; its jupyter-not-found path still reports 127
  unchanged.
- PyAutoHands: 354 passed (+2 new), same 14 pre-existing environment failures
  `main` has. The new test fails `assert 1 == 0` against the old code *with the
  TIMEOUT status already correct*, which isolates the group kill as the thing
  under test.

**Follow-up not done here.** `autolens_workspace_test` still carries its own
private `_kill_group` rather than importing `build_util.kill_group` like the
six adopters now do. Functionally identical; left alone rather than touch a
working production gate for consistency. Worth a one-line follow-up.

## Task

Order matters, though not for the reason the first draft gave: **Leg B first**
because it gives Leg A a `build_util` helper to import rather than six copies
each growing their own `_kill_group`. It does *not* "cover" the HowTo tier and
the release run against the hang — they were never exposed to it. **Leg A is
the one that fixes an unbounded hang, and it is the priority.**

1. ~~**PyAutoHands — `build_util`: add the process-group kill.**~~ **Done
   2026-08-23**, branch `claude/backport-per-script-timeout-r3w1sv`. Landed as
   `run_capped` + public `kill_group` — a drop-in for the module's
   `subprocess.run(..., timeout=...)` calls raising the same `TimeoutExpired`
   and `CalledProcessError` with the same captured attributes, so
   `_timeout_output`, `is_clean_skip_exit` and the `ScriptResult`/TIMEOUT
   report paths are untouched. Regression test asserts the grandchild is gone
   a second after the cap; against the old code it fails `assert 1 == 0` with
   the TIMEOUT status already correct, isolating the group kill. Suite: 354
   passed (+2), same 14 pre-existing environment failures as `main`. The
   original instruction, for the record: give
   `execute_notebook` (`:292`) and `execute_script` (`:447`) the
   `start_new_session=True` + `os.killpg(os.getpgid(pid), SIGKILL)` treatment
   from `autolens_workspace_test/.github/scripts/run_smoke.py::run_one` /
   `_kill_group`. `subprocess.run(timeout=...)` cannot express this — both
   sites become `Popen` + `communicate(timeout=...)`. Preserve the existing
   report/`ScriptResult` timeout paths and `is_clean_skip_exit` handling
   exactly. Export `_kill_group` (unprefixed) so the workspace runners can
   import it instead of copying it.
2. ~~**The three `workspace_test` copies**~~ **Done.** (autofit, autogalaxy, autocti): adopt
   the donor's `run_one` wholesale — `timeout_for(env)` with the
   `TIMEOUT_SECS` fallback shim, `Popen(start_new_session=True)`,
   `communicate(timeout=...)`, group kill, **return code 124**, and the
   `TIMEOUT (Ns)` status in both the per-entry line and the summary. These
   three are byte-identical to each other but for one docstring line, so it is
   the same patch three times. Do not "tidy" the docstring divergence in the
   same PR.
3. ~~**The three `workspace` copies**~~ **Done.** (autolens, autofit, autogalaxy): same
   treatment for `run_script` (`:101`). The notebook leg needs it too, and
   does **not** get it from step 1: `execute_notebook` (`:120`) shells out to
   `jupyter nbconvert --execute` directly rather than delegating to
   `build_util`, so it inherits nothing. An uncapped notebook hangs the gate
   exactly as an uncapped script does. While in `autogalaxy_workspace`, drop
   the vestigial
   `_BUILD_DIR` line (`run_smoke.py:51`) — the last remaining real drift inside
   this variant, and item 4 of the drift prompt.
4. ~~**HowTo tier: no change.**~~ **Confirmed.** The 75-line delegators inherit both legs from
   step 1. Confirm this by inspection and record it; do not open PRs.
5. Report back into `run_smoke_copy_drift.md`: its step 2 blocking question is
   answered here, and its step 4 (`_BUILD_DIR`) is absorbed into step 3 above.

One PR per repo (7 PRs), PyAutoHands first and merged before the workspace PRs
that depend on the exported helper.

## Acceptance

- ~~`grep -rn "start_new_session" PyAutoHands/autohands/build_util.py` is
  non-empty, and a script that forks a grandchild is reaped at the cap.~~
  **Met** — see step 1.
- ~~Every one of the 10 `run_smoke.py` copies either enforces a per-script cap
  with a process-group kill, or delegates to a `build_util` path that does.~~
  **Met.**
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
