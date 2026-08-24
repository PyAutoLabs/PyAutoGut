- completed: 2026-08-24
- issue: https://github.com/PyAutoLabs/autocti_assistant/issues/25
- prs:
  - https://github.com/PyAutoLabs/autocti_assistant/pull/26 (merged)
- summary: |
    CTI CI standardisation Phase 6, task 3 of 3. `--check-version` hashed the
    ENTIRE public surface of five modules against a committed baseline, so the
    check rotted on every library `main` merge that exported a name — the red it
    produced was 14 symbols, none of them cited. Chose option 1 (gate on
    removals) over option 2 (demote to informational), and the deciding fact was
    one the prompt did not have.

## The fact that decided the option

The prompt framed this as noise-reduction, where option 2 (let `--scope all` be
the only gate) is obviously leaner. What it did not know is that the baseline
stored only a **hash and a count**, never the symbol names:

```json
"autofit": { "hash": "d540d084…", "n_symbols": 160 }
```

So a red printed exactly this, and nothing more:

```
[drift] API DRIFT vs baseline (baseline generated 2026-07-23):
  - public API surface changed: autoarray, autofit
```

Undiagnosable. Working out *what* moved is what cost the previous session real
work — worktrees created at the baseline's own commits, the libraries installed
from them, the symbol sets diffed by hand. Recording the names (449 across five
modules, **12 KB**) removes the noise **and** makes every future red
self-diagnosing. That pairing is worth more than the simplification option 2
buys, so option 1 won — and it was put to the human as that trade, not as the
prompt's original framing.

## What shipped

- **Baseline records `symbols` per module** alongside `hash`/`n_symbols`.
  `_api_hash` split into `_api_hash_from_names`, so hash and names derive from
  one sorted list and cannot disagree — and a test can verify the *shipped*
  baseline is internally consistent without importing the stack.
- **The gate distinguishes additions from removals.** Additions print and pass;
  any removal fails and names the symbol. A symbol appearing cannot break a doc;
  a symbol disappearing can.
- **Deliberately not narrowed to *removals of cited symbols*.** That is exactly
  what `--scope all` already computes against the real citation set. Two
  mechanisms answering one question is how they drift apart. `--check-version`
  stays the cheap whole-surface tripwire.
- **Both backward-compatibility paths gate rather than guess.** A pre-#25
  baseline keeps the old all-or-nothing behaviour and says why (treating an
  undiagnosable change as additive would wave a real removal through). A module
  absent from the baseline entirely is reported distinctly, so adding one to
  `BASELINE_MODULES` does not read as "your baseline is old".
- No workflow edit needed: `wiki-currency.yml`'s uniform `run()` helper fails on
  any non-zero exit, so the exit code *is* the mechanism. `AGENTS.md`'s
  session-start prose updated to the narrowed meaning.

## The regenerated baseline is a pure schema upgrade

Regenerated against the real stack, then diffed against the one PR #23 wrote:

| module | hash | n_symbols | symbols recorded |
|---|---|---|---|
| autonerves | same | 32 → 32 | 32 |
| autoarray | same | 122 → 122 | 122 |
| autofit | same | 160 → 160 | 160 |
| autocti | same | 103 → 103 | 103 |
| autocti.plot | same | 32 → 32 | 32 |

Every hash and every version byte-identical — no API change is recorded, only
the names behind hashes that were already there. And `--check-version` was
already **clean** against today's `main` *before* regenerating, which
independently confirms PR #23's fix had not yet rotted.

## The skill file the task named did not exist

The prompt said to document the baseline-regeneration story in
`skills/ac_audit_skill_apis.md`. **That file was never written** — it is an
unfinished clone item in `PENDING.md` ("regenerate for this domain, reference:
`skills/al_audit_skill_apis.md`"), and `AGENTS.md` (×3), `modes/maintainer.md`
and `skills/ac_setup_environment.md` all link to it. Five broken links, in a
repo whose whole job is documentation currency.

Written here from `audit_skill_apis.py` itself rather than adapted from the
lensing sibling, so it describes this repo's actual checks. Carries the five
checks, how to read a drift report, the regenerate-or-investigate decision
procedure the task asked for, and why pinning to a released stack stays
rejected. Registered in `skills/README.md`, symlinked into `.claude/skills/`
(committed as mode `120000`, per the repo's convention), both `PENDING.md`
entries ticked.

## Verified

Against the real CTI stack — autonerves/autoarray/autofit `2026.8.17.1` from
source `main`, autocti `2024.11.13.2`, arcticpy 2.6, i.e. the same shape
`wiki-currency.yml` builds. The interpreter was the environment Heart's local
smoke runner had just built for task 2 of this phase, which is a neat
demonstration of that task's point.

| check | result |
|---|---|
| `--check-version` | exit 0 — clean |
| `--scope all` | exit 0 — 24 files, 31/31 unique symbols, 0 missing |
| `--lint-idioms` | exit 0 — 52 files, no defunct idioms (52 not 51: the new skill is scanned and clean) |
| `--check-provenance` | exit 0 — 8 pages, 0 errors, 9 warnings (pre-existing, non-gating) |
| `--check-citations` | exit 0 — 27 files, 29 citations, 0 missing |

`test_check_version.py` rewritten: 11 tests covering identical surface, version
stamp differing alone, additions-only passing *and* being named, a removal
gating, a removal alongside additions, a removal in one module while another
only gains, both legacy-baseline paths, a module absent from the baseline, a
missing baseline, and the shipped-baseline schema check.

The full-suite failure set was diffed against a clean `main` worktree rather
than eyeballed: 13 pre-existing failures (all "no installed stack" —
`test_api_gate`, `test_install_preflight`, `test_benchmark`), and this branch
adds none. CI: `wiki-currency` and `boundary` both green.

## The caveat, recorded rather than buried

This would **not** have prevented the red that started all of it.
`TransformerNUFFTPyNUFFT` and `autofit.database` were both *removed* and both
uncited, so a removals-only gate still goes red on them. What changes is that
the red arrives with the two names attached instead of "the surface changed",
and the twelve irrelevant additions no longer trigger it at all.

## Rejected, again

Pinning to a released stack. autocti's PyPI release is the pre-resurrection
`2024.11.13.2`, so pinning would grade today's docs against an API predating the
work they describe — vacuously green, worse than noisily red. The `stack_version`
input still exists for the release-time `workflow_call` path, where the released
surface really is the contract and a pin is right.

## Original prompt

# wiki-currency's --check-version gate rots on every library main merge

Type: maintenance
Target: autocti_assistant
Repos:
- @autocti_assistant
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised
Filed: 2026-08-24
Issued: 2026-08-24

`wiki-currency` went red on `autocti_assistant` main and was fixed on 2026-08-24
by regenerating `wiki/core/api_audit_baseline.json` (autocti_assistant#24, PR
#23). That fix is correct but **temporary**: the same red will return, and the
reason is structural, not incidental.

## The structural problem

`--check-version` compares a hash of the **entire public API surface** of
`autonerves`, `autoarray`, `autofit`, `autocti` and `autocti.plot` against a
committed baseline. The assistant documents almost none of that surface.

Measured at the time of the fix — the drift that turned the repo red was:

```
autoarray  120 -> 121   + InterpolatorDelaunayNN, validate   - TransformerNUFFTPyNUFFT
autofit    149 -> 159   + AbstractClipper, AbstractScaler, ApproxUpdater,
                          ClipperNone, ClipperPriorBox, DynamicUpdater,
                          FactorUpdater, NSS, ScalerNone, ScalerPriorWidth,
                          SimplerUpdater
                        - database
```

**Not one of those 14 symbols is cited anywhere in `wiki/`, `skills/` or
`modes/`.** `--scope all` — which audits exactly the symbols the docs *do* cite
— reported "All cited symbols resolve cleanly. No drift detected." throughout.
`autonerves`, `autocti` and `autocti.plot` were byte-identical.

So a check whose job is "are the docs current?" went red because eleven unrelated
sampler-clipper classes were exported from autofit.

The workflow installs the stack from the libraries' **`main` source clones** (not
a release — see the note below), so the clock is every merge into autofit or
autoarray `main` that touches an `__init__` export. That is fast. The new
baseline should be expected to rot within weeks.

A check that goes red on a schedule nobody controls, for reasons that never
affect the thing it gates, trains reviewers to ignore it — and this repo's PRs
already opened red for over a month.

## The decision to make

Two coherent options; **this task is to choose one deliberately and implement
it**, not to guess:

1. **Gate `--check-version` on removals only.** A symbol *disappearing* can break
   a doc; a symbol *appearing* cannot. Report additions as informational, fail
   only on removals from the surface. Keeps a cheap tripwire for the case that
   actually matters. Note this still would not have caught the real risk here —
   `TransformerNUFFTPyNUFFT` and `database` were both removed and neither was
   cited, so even removals produce false reds; consider gating on
   *removals of cited symbols*, which is what `--scope all` already computes.
2. **Accept that `--scope all` subsumes it as a gate.** Demote `--check-version`
   to informational (still printed, still useful context in the report), and let
   `--scope all` be the thing that can fail the workflow. Simplest, and the
   check it leaves is the one with a direct causal link to doc correctness.

Option 2 is the leaner one and is probably right; option 1 is defensible if a
whole-surface tripwire is wanted for release-time invocations
(`workflow_call` with `stack_version` set), where the surface really is the
contract. Consider keeping the strict behaviour for the pinned-release path and
relaxing only the native PR/dispatch path.

Whichever is chosen, the baseline-regeneration story should be documented in
`skills/ac_audit_skill_apis.md` so the next person hitting a red knows whether
regenerating is the right response or a papering-over.

## Do not "fix" this by pinning to a released stack

Already considered and rejected on 2026-08-24: autocti's PyPI release is the
pre-resurrection `2024.11.13.2`, so pinning would grade today's docs against an
API that predates the work they describe — vacuously green, worse than noisily
red. The workflow's own install-step comment says as much.

## Context worth reading first

`PyAutoMind/complete/2026/08/wiki-currency-baseline-drift.md` — the full
investigation, including the fact that the drift report used to print
`stack_version: latest released` when the native path actually builds from
`main` source clones. That mislabel is fixed, and the report now records each
source tree's short SHA, so a future red is diagnosable from the artifact alone.
