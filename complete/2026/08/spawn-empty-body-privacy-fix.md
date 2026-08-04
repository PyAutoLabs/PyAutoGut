Fixed a privacy leak in `scripts/spawn.py` that was stamping live PyAutoMind
registry entries into the **public** fresh-slate template repos, and removed the
cause of the chronic `Spawn Drift` weekly failure in the same change.

## What was wrong

`empty_body()` implemented the spec's `EMPTY` action as "keep line 1 of the live
file" rather than "keep the header line" (`docs/pyautobrain/spawn_spec.md`
rule 5). Registry ledgers that carry no H1 therefore had a live entry copied
verbatim into a public repo:

- `planned.md` — a live task slug written as an H2
- `ideas.md` — a raw idea bullet

The `ideas.md` line had **already shipped** to `PyAutoMind-template` in the
2026-07-27 sync (`3424dba1`) and sat in the public repo for eight days.
`queue.md` was a near miss: a real H1, but instance-named.

The canary scan reported `clean` throughout because `CANARY_TOKENS` held science
dataset names only. The spec's own example list names `Nightingale` — a person —
but no name token was ever implemented, and the privacy test the spec mandates
(`spawn_spec.md:62`) did not exist in the repo at all.

A heading-shape test would not have caught this: a task slug written as `##` is
a structurally valid heading. Only an explicit map separates a title from a
registry entry.

## Why the scheduled leg kept failing

`spawn_drift.yml` has no trigger-dependent behaviour — no `actions/checkout`, no
`github.ref`, no `github.event_name`, no `if:`. Both legs ran identical code;
the scheduled failure reproduced locally byte for byte.

Every green run in the workflow's history was a manual dispatch fired seconds
after a human ran `spawn --apply` (2026-07-13 sync `11:08:46Z` → dispatch
`11:09:02Z`, 16 s; 2026-07-27 sync `19:30:29Z` → dispatch `19:30:48Z`, 19 s).
That leg is a post-sync confirmation and cannot fail. Meanwhile `empty_body()`
keyed the template to line 1 of `planned.md` / `ideas.md`, which ordinary prompt
work rewrites many times a day — so the weekly run went red on registry churn
alone, independently of any real template change.

## The fix (PR #119, squashed as `ebd60f3`)

- `empty_body()` never opens the source. Named ledgers take a generated title
  from `EMPTY_TITLES`, keyed by repo-relative path so a glob-matched file
  sharing a root ledger's name (`bibliography/active.md`) cannot inherit its
  title. Glob-matched bibliography files take a generated comment header (spec
  rule 2). An unmapped `EMPTY` file raises, same doctrine as `UNMATCHED`.
- `CANARY_TOKENS` gained the name tokens the spec already called for, with a
  narrow per-file, per-token `CANARY_EXEMPT` for `LICENSE` only.
- New `tests/` + spec rule 1b (`KEEP`) so the privacy test travels with the
  generator it guards. Adding `tests/` was itself a new file class requiring a
  human partition decision — the same `UNMATCHED` failure that killed scheduled
  run `30256898178`.
- `spawn_drift.yml` gained a `privacy` job gating `drift`, running on PRs that
  touch spawn; `drift` is skipped on PRs since it diffs published templates
  against `main`.

## The review round that changed the outcome

An independent Codex review found the **first pass reintroduced the exact leak
it removed**. `tests/**` and `scripts/spawn.py` are both `KEEP`-copied verbatim
into the public template; the new test quoted the real slug and idea line as
fixtures, a `spawn.py` comment quoted the slug, and the first pass had exempted
**both files wholesale** from the canary scan — so the scan reported clean while
the template still shipped the content. Confirmed by grepping the generated tree.

Fixed at the cause rather than by widening the exemption: fictional fixtures,
canary tokens derived from `CANARY_TOKENS` at run time, the wholesale exemption
removed, and `test_only_spawn_py_is_exempt_wholesale` added so the hole cannot
grow back.

The deeper gap it exposed: the original suite unit-tested `empty_body()` alone,
so flipping any rule to `KEEP` or swapping the dispatcher for `copy2` would have
left it green — the leak would simply move. There are now end-to-end tests
driving `generate_all()` over a synthetic Mind/Memory asserting no live marker
reaches the tree.

## Verification

- 52 tests pass locally and on GitHub runners (count confirmed in the CI log,
  not just the green tick); the suite fails **behaviourally** against the
  pre-fix `spawn.py`, not merely at import.
- Independent sweep of the tree before publishing: every live registry line from
  all six Mind ledgers cross-checked against every generated file — 0 hits.
- Templates regenerated and published (`PyAutoMind-template` `51f5ae5`,
  `PyAutoMemory-template` `91df3d3`), clearing the 8-day-old `ideas.md` leak.
- CI-equivalent `--check` against freshly cloned published repos: exit 0.
- **Root-cause proof (not the tautological leg):** with live `planned.md` /
  `ideas.md` line 1 rewritten to simulate ordinary prompt work, the old
  generator emits those new live lines while the new one emits stable titles —
  so registry churn no longer produces drift or a leak.

## Follow-ups filed

- `draft/maintenance/pyautomind/spawn_drift_has_no_generator.md` — the workflow
  detects drift but nothing regenerates; a self-heal should open a PR (not push,
  since these are force-synced generated views).
- `draft/bug/pyautomind/spawn_keep_rules_export_instance_state.md` — two further
  **pre-existing** holes from the same review: `.github/**` exports live incident
  history through owner-only substitution, and `SPECIAL:autonomy_log` still
  parses live bytes (the same hazard class as this bug).

## Ship notes

Heart was YELLOW at ship time on three unrelated reasons (workspace validation,
tenant-firewall manifest drift, stale release rehearsal), human-acknowledged.

## Follow-on: the sync opened a second drift loop (PR #120)

Publishing #119 exposed a latent interaction. The template ships
`lifecycle_drift.yml`, whose self-heal (#116) regenerates `complete/index.md` on
every push to the template's own `main` — but `MIND_RULES` DROPs `complete/*`,
so spawn never produced that file. The self-heal only reached the template in
this very sync (it was one of the five outstanding source drifts), and fired 21
seconds later:

```
17:28:51Z  51f5ae58  Jammy2211            spawn: regenerate from mind@ebd60f3
17:29:12Z  79864dde  github-actions[bot]  lifecycle: self-heal stale complete/index.md
```

The next dispatch (run `30934170549`) failed on
`only in published: complete/index.md`. **A local `--check` had exited 0** —
this was caught only by dispatching the real workflow, which is the lesson: the
local check and the CI check disagreed, and CI was right.

PR #120 makes spawn stamp the index by running the *generated tree's own*
`scripts/lifecycle.py index --apply` (lifecycle.py resolves its root from
`__file__`; rule 1 already KEEPs it). Byte-identical to the bot's output by
construction — verified against the bot's actual commit — so the two can never
disagree. Not held as a constant asset: lifecycle.py owns that format.

Also in #120: the privacy job named `tests/test_spawn_privacy.py` explicitly, so
the new contract test never ran in CI (52 reported vs 55 in the suite). Now runs
`tests/` whole, with the paths filter widened to `tests/**`; CI count confirmed
rising 52 → 55.

## Final verification

- `spawn --check` against freshly cloned published repos: **exit 0**, both
  templates OK, canary clean, unmatched none.
- The self-heal's own `lifecycle.py index --check` run against the published
  template: **OK** — it has nothing to regenerate, so the loop is closed at the
  source rather than papered over.
- Published: `PyAutoMind-template` `cfd6f41`, `PyAutoMemory-template` `91df3d3`.

## Known-remaining (filed, not fixed here)

The template repo's own `pyauto-morning-health` and `pyauto-update-digest`
workflow runs fail — instance automation copied in by the blanket `.github/**`
rule, which is exactly the hole described in
`draft/bug/pyautomind/spawn_keep_rules_export_instance_state.md`.

The scheduled `Spawn Drift` leg has still never passed on its own; the next
Monday 06:17 UTC run is the first real test. Everything reproducible has been
verified, but that one is genuinely pending.

## Original prompt

# spawn EMPTY leaks live registry entries into the public templates

Type: bug
Target: PyAutoMind
Repos:
- PyAutoMind
Difficulty: medium
Autonomy: supervised
Priority: high
Status: formalised

`scripts/spawn.py::empty_body()` implements the spec's `EMPTY` action as "keep
line 1 of the live file", not "keep the header line". For registry files that
have no H1, line 1 *is* instance content — so spawn stamps live registry entries
into the fresh-slate template repos, violating the hard privacy invariant in
`docs/pyautobrain/spawn_spec.md:61`.

## Evidence

`scripts/spawn.py:338`:

```python
def empty_body(src):
    try:
        first = src.read_text(errors="replace").splitlines()[0]
    except IndexError:
        first = ""
    ...
    return first + "\n\n<!-- emptied by spawn; schema: REFERENCE.md -->\n"
```

Neither `planned.md` nor `ideas.md` contains an H1 anywhere (`grep "^# "` finds
nothing in either), so this can never yield a header for them — it yields a
registry entry on every run:

| EMPTY-ruled file | live line 1 | verdict |
|---|---|---|
| `active.md` | `# Active Tasks` | header — fine |
| `parked.md` | `# Parked tasks` | header — fine |
| `condemned.md` | `# Condemned material` | header — fine |
| `queue.md` | `# Pytree variant queue` | header, but instance-flavoured |
| `planned.md` | `## rhayes-audit-validation-phases-2-4` | **registry entry — leak** |
| `ideas.md` | `- lens_calc_zero_contour_jax autolens workspace guide.` | **registry entry — leak** |

The `ideas.md` line is **already published** in `PyAutoLabs/PyAutoMind-template`
(shipped in the 2026-07-27 sync, commit `3424dba1`). Regenerating the templates
today would additionally publish the `planned.md` slug.

The canary scan reports `clean` throughout, because `CANARY_TOKENS` is
`("slacs", "b1938", "cosmos_web_ring", "smbh_binary", "arctic")` — dataset names
only. The spec's own example canary list (`spawn_spec.md:64`) includes
`Nightingale`, a person's name; no name token was ever implemented. The
spec-mandated privacy test ("The implementation must include a test asserting
the generated tree contains none of a canary list of live-content markers") does
not exist in PyAutoMind.

## Second-order effect: the chronic `Spawn Drift` red

`empty_body()` keying on line 1 couples the template to files that ordinary
daily work rewrites. Mind's `main` takes multiple pushes per hour from
concurrent agent sessions, and `planned.md` / `ideas.md` are exactly what those
pushes touch. So the weekly scheduled check goes red on registry churn alone,
independently of any real template change.

## Scope

1. `empty_body()` — emit a deterministic per-file title; never read instance
   bytes. Proposed map:

   ```python
   EMPTY_TITLES = {
       "active.md":    "# Active Tasks",
       "planned.md":   "# Planned",
       "parked.md":    "# Parked tasks",
       "condemned.md": "# Condemned material",
       "ideas.md":     "# Ideas",
       "queue.md":     "# Queue",
       "reading-queue.md": "# Reading queue",
   }
   ```

   Fail loudly on an EMPTY-ruled file with no map entry (same doctrine as
   `UNMATCHED`: a new file class is a human decision, never classified ad hoc).
   This also settles `queue.md`, whose live H1 `# Pytree variant queue` is
   instance-flavoured and would otherwise survive an "H1s are safe" heuristic.

2. `CANARY_TOKENS` — add the name tokens the spec already calls for
   (`nightingale`, `rhayes`), and keep the existing dataset tokens.

3. Add the spec-mandated privacy test: assert no generated EMPTY output
   contains any byte derived from its source beyond the mapped title, and run
   the canary scan over a generated tree.

4. Regenerate + force-sync both template repos (`/spawn --apply`, the sanctioned
   exception), clearing the `ideas.md` leak already in the published history and
   the five legitimate source drifts (`lifecycle.py`, `repos_sync.py`,
   `lifecycle_drift.yml`, Memory `validate.yml`, Memory `validate_structure.py`).

Do not change `docs/pyautobrain/spawn_spec.md`: it already specifies "header
line + schema pointer comment only". This is the implementation failing to
mirror the spec, not a spec gap.

## Out of scope (worth a follow-up prompt)

`Spawn Drift` detects drift but nothing regenerates. Every green run to date was
a manual dispatch fired seconds after a human ran `spawn --apply` (2026-07-13
sync `11:08:46Z` → dispatch `11:09:02Z`; 2026-07-27 sync `19:30:29Z` → dispatch
`19:30:48Z`), so the dispatch leg cannot fail and is not an independent check.
The workflow itself has no trigger-dependent behaviour — no `actions/checkout`,
no `github.ref`, no `github.event_name`, no `if:` — both legs run identical
code. Consider the `lifecycle_drift.yml` self-heal pattern (issue #116): on
schedule, regenerate and open a PR (not a direct push — these are force-synced
generated views).

## Original request (verbatim)

> The PyAutoMind spawn_drift scheduled workflow has failed on every
> scheduled run since 2026-07-20 and passes only on manual dispatch.
> Latest failure: PyAutoMind run 30804113655 (2026-08-03T10:05Z), step
> "Regenerate + diff", exit 1, with 6 drifts:
>
>   PyAutoMind-template:   planned.md
>                          .github/workflows/lifecycle_drift.yml
>                          scripts/lifecycle.py
>                          scripts/repos_sync.py
>   PyAutoMemory-template: .github/workflows/validate.yml
>                          scripts/validate_structure.py
>
> Canary scans were clean and "unmatched: none" on both. Regenerate the
> templates from their live sources so the drift check goes green, and say
> why the scheduled leg diverges from the manual-dispatch leg — a check
> that only passes when a human pushes the button isn't a check.
