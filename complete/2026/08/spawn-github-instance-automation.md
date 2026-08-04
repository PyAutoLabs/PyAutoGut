Stopped spawn shipping instance automation into the public fresh-slate
templates. `MIND_RULES` mapped `.github/*` to `KEEP_SUB`, which only replaces
`PyAutoLabs` with `YOURORG` — everything else passed through verbatim, so the
template arrived carrying workflows that cannot run in the org it was spawned
for. `PyAutoMind-template` had **13 failing runs** from them.

Pre-existing; surfaced by the independent Codex review of #118.

## The key finding

Owner substitution does not make a cross-repo workflow work. `YOURORG` is a
literal placeholder, so the template's own `spawn_drift` run failed with
`repository 'https://github.com/YOURORG/PyAutoMind/' not found`. Anything that
clones or queries a sibling repo is broken on arrival — secrets or not. The
problem was never "some workflows need secrets"; it was that a blanket rule
cannot tell machinery from instance automation.

## The rule adopted (spec rule 9)

> No workflow shipped into a template may **fail unattended** on a
> freshly-spawned repo.

Two conditions: no unattended trigger it cannot satisfy, and no configured
secret (`GITHUB_TOKEN` is auto-provided and allowed). Evidence-backed by the
template's own run history — `lifecycle_drift.yml` was the one green workflow,
and it is the one that clears the bar.

| rule | file | action |
|---|---|---|
| 9a | `lifecycle_drift.yml` | KEEP — self-contained, no owner reference at all |
| 9b | `spawn_drift.yml` | keep, `schedule:` stripped |
| 9c | `morning_status`, `morning_health`, `arxiv_papers`, `.github/scripts/**` | DROP |
| 9d | anything else under `.github` | no catch-all — UNMATCHED by design |

`MEMORY_RULES` got the same treatment; `validate.yml` is self-contained and
still ships byte-identical, so no Memory drift.

## 9d is the part that matters

A catch-all is fail-**open**: a workflow added to Mind later rides it into the
template with whatever schedule and secrets it has. The tripwire test caught
exactly that against an earlier draft of this change that kept the fallback, so
the fallback was removed entirely. A new `.github` file now fails the run and
gets an explicit human decision, like every other new file class.

## Three defects found by testing, not by reading

All in the `SPECIAL:unscheduled` transform, all fixed and pinned:

1. a `schedule:` line inside a `run: |` shell block was rewritten into comments,
   silently mangling the script;
2. `on.workflow_call.inputs.schedule` — a legitimate input, not a trigger — was
   deleted, because the match was "anywhere under `on:`" rather than "direct
   child of `on:`";
3. a comment at the **same indent** as `schedule:` ended block consumption
   early, orphaning the `- cron` line and emitting **invalid YAML**.

Flow style and a schedule-less workflow both fail loudly rather than being
guessed at, so the rule cannot rot into a silent no-op.

## Independent review (Codex) — five findings, all real

Two were defects 2 and 3 above. Also:

- **`pip install pytest` only, but the contract tests import PyYAML.** The CI
  log confirms PyYAML was *downloaded*, not preinstalled — so this would have
  failed at **collection** on the next run, taking the whole suite with it.
- **Memory's fail-closed rule was untested** — every workflow fixture drove
  `generate_mind`. Now covered, and control-tested by reverting the rule and
  confirming the new test fails.
- **The spec overclaimed.** It said shipped workflows "must be able to succeed"
  and mandated a test asserting no `YOURORG/` reference — but rule 9b
  deliberately ships `spawn_drift.yml`, which clones `<owner>/*-template` and
  *will* fail on manual dispatch until the org publishes templates. The rule
  being protected is "nothing fails unattended", not "every human-invoked path
  succeeds"; asserting no `YOURORG/` would forbid shipping the generator at all.
  The invariant now states both conditions precisely **and records what it does
  not require**, so the next reader does not "fix" the gap by breaking 9b.

## Verification

- 72 tests pass locally and on GitHub runners (count confirmed in the CI log).
- Generated output byte-identical before and after the review fixes — the
  shipped `.github` tree and `spawn_drift` triggers/jobs unchanged.
- Published `PyAutoMind-template` `f3ae22b`; Memory template already current.
- `--check` against freshly cloned published repos: **exit 0**, both OK.
- The four instance files are **deleted from the published template**, not
  merely disabled, and no remaining shipped workflow carries a `schedule:`
  (`lifecycle_drift`: push/PR/dispatch; `spawn_drift`: PR/dispatch).

## Genuinely pending

Every failing run in the template predates the publish (newest 17:29:01Z vs
publish 19:00:52Z). The daily jobs last fired at ~04:53 / 07:43 / 08:19 UTC and
their workflow files are now gone, so **tomorrow morning is the observable
proof** — no `pyauto-morning-health`, `pyauto-update-digest` or
`pyauto-arxiv-papers` runs should appear. Not yet confirmable.

Separately, the scheduled `Spawn Drift` leg (Monday 06:17 UTC) still has never
passed on its own — see `spawn-empty-body-privacy-fix`.

## Sibling work

Split from the bundled instance-state prompt filed during the #118 review. The
other half — `SPECIAL:autonomy_log` still parsing live bytes, the same hazard
class as the #118 bug — remains open as
`draft/bug/pyautomind/spawn_autonomy_log_parses_live_bytes.md`.

## Ship notes

Heart YELLOW at ship time (score 70, `red_reasons: []`) on a subset of the
reason set acknowledged earlier the same day: workspace validation not passing,
tenant-firewall manifest drift. Neither related to this change.

## Original prompt

# spawn's blanket `.github/**` rule ships broken instance automation

Type: bug
Target: PyAutoMind
Repos:
- PyAutoMind
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised

`MIND_RULES` maps `.github/*` to `KEEP_SUB`, which only replaces `PyAutoLabs`
with `YOURORG`. Everything else passes through verbatim. The result is a
fresh-slate template that arrives with somebody else's automation, most of which
**cannot succeed** in the org it was spawned for.

Pre-existing; surfaced by the independent review of #118. Split from
`spawn_keep_rules_export_instance_state.md` (the `autonomy_log` half is now
`spawn_autonomy_log_parses_live_bytes.md`).

## Evidence — the template's own run history

`PyAutoLabs/PyAutoMind-template` currently has **13 failing runs** from
workflows it inherited:

| workflow | reaches outside its own repo? | template result |
|---|---|---|
| `lifecycle_drift.yml` | no — checkout + local scripts | **success** |
| `spawn_drift.yml` | clones `YOURORG/*` | fail: `repository 'https://github.com/YOURORG/PyAutoMind/' not found` |
| `morning_status.yml` | 8 hardcoded sibling repos | fail ×5 |
| `morning_health.yml` | `PyAutoHeart` / `PyAutoBrain` / `PyAutoHands` workflow names | fail ×5 |
| `arxiv_papers.yml` + `.github/scripts/arxiv_fetch.py` | `PYAUTO_PAPERS_WEBHOOK_URL`, `CLAUDE_CODE_OAUTH_TOKEN` | fail ×3 |

The `spawn_drift` failure is the key one: it proves **owner substitution does
not make a cross-repo workflow work**. `YOURORG` is a literal placeholder, so
every workflow that clones or queries a sibling repo is broken on arrival until
the user hand-edits it.

## Also instance content, not just broken

- `arxiv_fetch.py` hardcodes strong-lensing search vocabulary (`lens`,
  `lensed quasar`, …) and a Claude-summarisation prompt shaped for that domain.
  A template spawned for a non-lensing org inherits a strong-lensing arXiv
  query.
- `arxiv_papers.yml` and `arxiv_fetch.py` carry dated design decisions and
  incident notes in their comment headers — live task history.

## The rule to adopt

> A template workflow must be able to succeed on a freshly-spawned repo with
> **no secrets and no sibling repos**.

Only `lifecycle_drift.yml` clears that bar today, and the template's run history
proves it (the one green workflow).

## Scope

1. Update `spawn_spec.md` rule 9 first: replace the blanket `.github/**`
   `KEEP_SUB` with explicit per-file rules, stating the succeed-on-a-fresh-repo
   principle above.
2. Mirror in `MIND_RULES`:
   - `.github/workflows/lifecycle_drift.yml` → KEEP (operates only on its own
     repo; no owner references at all, so no substitution needed)
   - `.github/workflows/spawn_drift.yml` → SPECIAL: keep, but **strip the
     `schedule:` trigger** so it never auto-fails on an org with no published
     `*-template` repos. Leave `pull_request` + `workflow_dispatch`, and leave a
     comment saying to re-add the schedule once templates are published.
   - `.github/workflows/{morning_status,morning_health,arxiv_papers}.yml` and
     `.github/scripts/arxiv_fetch.py` → DROP (instance automation: live repo
     lists, organ-specific workflow names, org secrets, domain vocabulary)
3. Extend `tests/test_spawn_template_contract.py`: assert the generated
   template ships no workflow carrying a `secrets.` reference or a `YOURORG/`
   cross-repo reference, and that no shipped workflow has a `schedule:` trigger
   that would fail on a fresh org. This is the guard that keeps rule 9 honest as
   new workflows land in Mind.

## Note

Dropping these is not a loss of capability — a spawned org that later builds the
same organs can copy the workflows across deliberately. Shipping them
pre-broken, failing weekly and emailing the new owner, is strictly worse than
not shipping them.
