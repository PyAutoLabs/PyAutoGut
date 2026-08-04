Removed the last live-byte parse from `spawn.py`. `autonomy_log_body()` copied
lines from the live `autonomy_log.md` until one started with `|---` — the same
"trust the live file's shape" pattern that made `empty_body()` stamp live
registry entries into the public templates (#118). It had not fired yet.

Pre-existing; surfaced by the independent Codex review of #118. Sibling half of
#121, split from the bundled instance-state prompt.

## Both failure modes, reproduced against the real ledger

| hazard | old behaviour |
|---|---|
| a task row inserted **above** the separator | that row copied into the template |
| separator reformatted to `\| --- \|` (a cosmetic edit any markdown formatter makes) | the break never fires — **231 live task records** copied |

**The canary scan was no backstop.** A leaked row containing no dataset or
person token returns zero hits — verified directly. The full-ledger case is
caught today only because some rows happen to mention `slacs1430` / `B1938` /
`cosmos_web_ring`. That is luck, and it is exactly the reasoning that made the
#118 leak invisible.

## The fix (PR #124, squashed as `3cdc755`)

The header is now the `AUTONOMY_LOG_TEMPLATE` constant and the source is never
opened. Byte-identical to what the parse produced for the current ledger, so it
introduced **no template drift** — `autonomy_log.md` did not appear in the
publish diff at all.

Spec rule 5 was also internally contradictory: it listed `autonomy_log.md` with
the EMPTY ledgers and said each title lives in `EMPTY_TITLES`, but the ledger is
`SPECIAL`, absent from that map, and carries prose plus a table rather than a
title and schema-pointer comment. Split into rule 5 (the six EMPTY ledgers) and
rule 5b (the autonomy ledger).

## The trade-off this creates, and how it is covered

Generating instead of parsing removes the leak — but it also removes the
feedback that kept the header current. Nothing else would notice if the live
ledger grew a column and the template kept shipping the old table.

So one test reads the real file and asserts the live ledger still **starts
with** the constant. If the schema moves, that fails and says to update the
constant — explicitly *not* to re-add parsing.

## Independent review (Codex) — two findings, both fixed

1. **The tests were partly circular.** `autonomy_log_body(src) ==
   AUTONOMY_LOG_TEMPLATE` compares the helper with what the helper returns, and
   the only independent format check was `endswith("|")` — a stale or malformed
   constant would have left every test *and* `--check` green. Added the
   live-schema guard above, an assertion on the **emitted** template file rather
   than the helper's return value, and an independent shape check (H1 present,
   exactly a header row plus separator, matching column counts).
   Control-tested both ways: a stale column fails the live-schema guard; a short
   separator fails that and the shape guard.
2. **The spec contradiction** above.

Codex independently confirmed what had been audited by hand: the constant is
byte-identical to the live ledger's first 11 lines (both SHA-256 `6cad53f7…`),
the signature is safe at the single production call site, no other handler
parses live bytes with shape assumptions, and there is no feedback loop —
feeding the template back through spawn returns the same constant, and no
shipped workflow regenerates it.

## Verification

- 81 tests pass locally and on GitHub runners (count confirmed in the CI log).
- **7 fail against the old implementation** — the missing-source case, five
  hostile ledger shapes, and the end-to-end generated-tree test.
- Ledger shapes covered: well-formed, row-above-separator, reformatted
  separator, no separator, prose-then-table — plus a nonexistent source file,
  the strongest form of "never opens it".
- Published `PyAutoMind-template` `9459a4c`; Memory template already current.
  `autonomy_log.md` unchanged in the publish diff, as predicted.
- `--check` against freshly cloned published repos: **exit 0**, both OK.
- The published template's **own** copy of the suite passes when run from the
  template (81 tests) — spec rule 1b working as intended: the privacy guards
  travel with the generator they guard.

## Closes the #118 review arc

All three follow-ups from the original spawn-drift investigation are now
shipped: #120 (the self-heal drift loop), #121/#122 (`.github` instance
automation), and this. `spawn.py` no longer parses live bytes with shape
assumptions anywhere — the remaining reads are deliberate verbatim copies of
files the rules judged generic (KEEP / KEEP_SUB), plus the indent-scoped
workflow transform.

## Genuinely pending (not this task's to close)

- The scheduled `Spawn Drift` leg (Monday 06:17 UTC) has still never passed on
  its own. Every green run in its history was a manual dispatch fired seconds
  after a human `--apply`. See `spawn-empty-body-privacy-fix` and
  `draft/maintenance/pyautomind/spawn_drift_has_no_generator.md`.
- Tomorrow morning is the observable proof for #121: no
  `pyauto-morning-health` / `pyauto-update-digest` / `pyauto-arxiv-papers` runs
  should appear on the template.

## Ship notes

Heart YELLOW (score 70, `red_reasons: []`) on the same two reasons acknowledged
earlier the same day: workspace validation not passing, tenant-firewall manifest
drift. Neither related to this change.

## Original prompt (folded manually)

This task's issue (#123) was created directly rather than via `create_issue`, so the prompt never advanced `draft/` → `active/` and `lifecycle.py record --prompt` had nothing to fold. Preserved verbatim here instead:

<details>
<summary>draft/bug/pyautomind/spawn_autonomy_log_parses_live_bytes.md</summary>

# spawn's `SPECIAL:autonomy_log` still parses live bytes

Type: bug
Target: PyAutoMind
Repos:
- PyAutoMind
Difficulty: small
Autonomy: supervised
Priority: normal
Status: formalised

`autonomy_log_body()` in `scripts/spawn.py` reads the live `autonomy_log.md` and
copies lines until one starts with `|---`. That is the same "trust the live
file's shape" pattern that made `empty_body()` leak live registry entries into
the public templates (#118, fixed) — it just has not fired yet.

Pre-existing; surfaced by the independent review of #118. Split from
`spawn_keep_rules_export_instance_state.md` (the `.github/**` half is now
`spawn_github_rules_export_instance_automation.md`).

## The hazard

```python
for line in lines:
    kept.append(line)
    if line.startswith("|---"):
        break
```

Two ways this copies live task records into a public template:

1. a task row inserted **above** the separator is copied verbatim;
2. a validly reformatted separator (`| --- |`, or a leading space) never
   matches, so the loop copies the **entire ledger**.

The live `autonomy_log.md` holds real task records with real dataset names and
issue references, so a mis-fire is a substantial leak. It is caught by the
canary scan *today* only because those particular rows happen to contain canary
tokens — that is luck, not a guarantee, and exactly the reasoning that made the
#118 leak invisible.

## Fix

Same shape as the #118 fix: generate the schema header rows as a constant asset
instead of parsing them out of the live ledger. `empty_body()` and
`EMPTY_TITLES` are the precedent — no source bytes, no shape assumptions.

Extend `tests/test_spawn_privacy.py`; its `test_generated_tree_contains_no_live_content`
already plants a live marker in `autonomy_log.md`, so add a case with the
separator reformatted (`| --- |`) and one with a task row above the separator —
both should still produce a clean template.

</details>
