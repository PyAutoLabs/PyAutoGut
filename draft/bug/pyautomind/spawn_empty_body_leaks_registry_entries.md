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
