# spawn's KEEP_SUB and autonomy_log rules still export instance state

Type: bug
Target: PyAutoMind
Repos:
- PyAutoMind
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised

Two privacy holes in `scripts/spawn.py` that are **pre-existing** — neither was
introduced by #118, and both survive that fix. Found by an independent review
of the #118 branch. The canary scan cannot see either, because neither carries
a `CANARY_TOKENS` term.

The invariant they violate is the same absolute one (`spawn_spec.md:61`): *no
live wiki page, bibliography entry, reading-queue line, prompt, or registry
entry may ever appear in a template output.*

## 1. `.github/**` exports live instance behaviour through owner-only substitution

`MIND_RULES` maps `.github/*` to `KEEP_SUB`, which only replaces `PyAutoLabs`
with `YOURORG`. Everything else passes through verbatim. Currently that ships,
into a public fresh-slate template:

- `.github/scripts/arxiv_fetch.py` — dated incident history, live paper
  identifiers, and Mind issue references (~lines 30, 257)
- `.github/workflows/arxiv_papers.yml` — recorded user decisions and
  Slack-specific automation (~line 3)

That is live task history and instance behaviour, not fresh-slate machinery. A
fresh Mind spawned for another org inherits somebody else's incident log.

Decide per file, not per directory: the workflows a fresh org genuinely needs
(lifecycle drift, spawn drift, validate) versus instance automation that should
be DROP or replaced with a generated skeleton.

## 2. `SPECIAL:autonomy_log` parses live bytes — the same hazard #118 fixed

`autonomy_log_body()` reads the live `autonomy_log.md` and copies lines until
one starts with `|---`. That is the same "trust the live file's shape" pattern
that made `empty_body()` leak:

- a task row inserted above the separator is copied verbatim;
- a validly reformatted separator (`| --- |`) never matches, so the loop copies
  the entire ledger.

The live `autonomy_log.md` contains real task records with real dataset names,
so a mis-fire here would be a substantial leak. It happens to be caught by the
canary scan *today* only because those particular rows contain canary tokens —
that is luck, not a guarantee.

Fix the same way #118 fixed EMPTY: generate the schema header rows as a
constant asset rather than parsing them out of the live ledger.

## Scope

1. Replace `autonomy_log_body()` with a generated constant header (no source
   read), mirroring the `EMPTY_TITLES` approach.
2. Audit `.github/**` file by file; split the blanket `KEEP_SUB` into explicit
   KEEP / DROP / GENERATE rules. Update `spawn_spec.md` rule 9 first, then
   mirror in `MIND_RULES`.
3. Extend `tests/test_spawn_privacy.py` — its `test_generated_tree_contains_no_live_content`
   already plants a marker in `autonomy_log.md` and `.github/`, so tightening
   these rules should be provable there.

## Depends on

Issue #118 must land first — it adds the end-to-end generated-tree test this
work should extend rather than duplicate.
