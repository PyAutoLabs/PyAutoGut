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
