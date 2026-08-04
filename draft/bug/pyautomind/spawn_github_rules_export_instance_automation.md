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
