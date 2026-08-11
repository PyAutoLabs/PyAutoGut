# Add a `human_required/` lifecycle folder for prompts an autonomous run must not pick up

Type: feature
Target: PyAutoMind
Repos:
- PyAutoMind
- PyAutoBrain
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised

## Why

`draft/` currently mixes two very different things: work an agent can pick up and
finish, and work that is **open-ended research** where the answer may not exist and
a human has to steer. Today the only way to tell them apart is to open the file and
read the `Difficulty:` header — and `too-large` is doing double duty for "big but
known" and "nobody knows if this is solvable".

That cost real time on 2026-08-11. `ep_hierarchical_scale_collapse_moment_match.md`
sat in `draft/bug/autofit/` looking like an ordinary bug. Leg 1 was genuinely
shippable and shipped (PyAutoFit#1465). Leg 2 — cure the collapse basin — is
research: every candidate lever needs a *loop* of runs to judge, each loop is
35-60 min of CPU on a toy, and a lever that worked there would still need
validating across N, across truth values, and against the near-boundary
`slope_hierarchy` case before it could change EP defaults. It was shelved on human
call after the work had already started. **A folder that said so up front would have
been read before the work began, not after.**

## The name — `human_required/`

**Recommended: `human_required/`.** It reuses the organism's existing vocabulary
exactly: `Autonomy: human-required` is already a prompt-header value and is already
defined in `PyAutoBrain/AUTONOMY.md` ("`--auto` changes nothing; today's flow"). No
new concept is introduced — the folder is the *filesystem projection* of an autonomy
level that already exists.

Rejected, with reasons worth keeping so this is not re-litigated:

| candidate | why not |
|---|---|
| `research/` | collides with the **work-type** `draft/research/`. A prompt could be `research/research/...` — and work-type is what PyAutoBrain routes on. |
| `parked/` | `parked.md` is an existing registry with a *different* meaning: started but not in flight. |
| `shelved/` | already taken by `complete/archive/shelved/`, which is **retired** material. This folder is for live work. |
| `supervised/` | `supervised` is a distinct autonomy level *between* `safe` and `human-required`; naming the folder after the wrong level would be actively misleading. |
| `deferred/`, `open_problems/` | fine English, but invent vocabulary the organism does not already have. `deferred/` is the runner-up if `human_required/` is judged too long. |

## Design question to settle FIRST (do not skip)

The `Autonomy:` header **already encodes this**. A folder duplicates that state, and
duplicated state drifts — a prompt could sit in `human_required/` with
`Autonomy: safe` in its header, and nothing today would notice.

Pick one and implement it deliberately:

- **(a) Header is authoritative, folder is derived.** `lifecycle.py check` fails if a
  file in `human_required/` does not carry `Autonomy: human-required`, and
  (optionally) if a prompt anywhere else *does*. Cheap, and kills the drift class
  outright. **Recommended.**
- **(b) Folder is authoritative**, header becomes advisory. Simpler to move files,
  but then AUTONOMY.md's level and the folder can disagree with no guard.

Whichever is chosen, say so explicitly in `REFERENCE.md` so the next reader does not
have to infer it.

## Scope

Note this is **two repos**. PyAutoMind owns the folder and the guard; PyAutoBrain
owns everything that *scans* prompts, and it hardcodes `draft/` in several places.
A PyAutoMind-only change will leave the new folder invisible to `/intake` and to the
dashboard.

### PyAutoMind

1. **Create `human_required/`** as a sibling of `draft/`, `active/`, `complete/`.
   Mirror the draft layout inside it — `human_required/<work-type>/<target>/<name>.md`
   — so routing still works if a prompt graduates back to `draft/`.
2. **`scripts/lifecycle.py`**
   - Add `HUMAN_DIR = ROOT / "human_required"` beside the existing
     `ACTIVE_DIR` / `COMPLETE_DIR` / `ARCHIVE_DIR` / `DRAFT_DIR` block (~lines 63-68).
   - Extend `cmd_check` (~line 898). Its "a file should not exist in two state dirs
     at once" test currently compares **only** `active/` against `complete/` — the
     new folder must join that invariant, or a prompt can be in `human_required/`
     and `active/` simultaneously with no complaint.
   - Add the chosen header/folder consistency check from the design question above.
   - Decide whether a `lifecycle.py` subcommand should own the move (alongside
     `move` / `record`), or whether `git mv` + `check` is enough. A subcommand is
     preferable — AGENTS.md already says `scripts/lifecycle.py` owns the moves.
3. **`tests/test_lifecycle_check.py`** — cover the new invariants. A guard with no
   test is how the F10 monotone limb ended up as dead code that still passed CI.
4. **Docs.** The canonical sections are in **`REFERENCE.md`**, not README:
   `## Repository layout` (~132), `## Prompt taxonomy` (~200), `### Prompt file
   format` (~275). Also `AGENTS.md` "Layout (operational)", and `ROUTING.md`
   "Not routed by work type" (which lists `active/` and `complete/` — the new
   folder belongs there too, since it is a *state*, not a work-type).

   **Trap:** `AGENTS.md` currently points at *README.md* for "Prompt taxonomy" and
   "Prompt file format", but README.md is a 46-line landing page and those sections
   live in `REFERENCE.md` (which says so itself at line 5). Fix those pointers while
   you are in there, or the next reader edits the wrong file.

### PyAutoBrain

5. **`agents/conductors/intake/_intake.py`** hardcodes `draft/` in at least four
   places: the proposal paths (~233-237), the census walk (~349-373), reconcile
   (~662), and repo extraction (~728). Decide and implement:
   - `intake census` / `intake dashboard` should **count `human_required/` as its own
     band**, not silently omit it and not fold it into the backlog total (the
     dashboard's headline "N filed prompts in the backlog" would otherwise quietly
     shrink, which reads as progress that did not happen).
   - `intake reconcile` should still scan it — a research prompt can be overtaken by
     upstream just like any other.
   - `intake classify` should be able to *propose* `human_required/` when it sizes
     something as open-ended, or explicitly should not. Either is defensible; pick one.
6. **`AUTONOMY.md`** — state that a prompt in `human_required/` is never eligible for
   an `--auto` run, and cross-reference the folder from the `human-required` level.
7. Check the conductors that resolve prompt paths (`bug.sh`/`_bug.py`,
   feature, `skills/WORKFLOW.md`, `skills/intake/intake.md`) so
   `/start_dev human_required/<path>` resolves rather than 404s — a human should
   still be able to start one deliberately.

## What moves in

Move these six, all currently in `draft/`:

- `draft/research/graphical_ep/ep_scoping.md` — EP scale-up; open-ended perf research
  (~86% of optimise time in Dynesty wrapper overhead), no bounded fix, and it asks
  for its own baseline to be re-derived before follow-ups are issued.
- `draft/research/graphical_ep/graphical_scoping.md` — same shape; hits a
  dimensionality wall (91 free parameters at N=30).
- `draft/research/autofit/priors_and_messages_math_audit.md` — a parked **census**
  that says of itself "not a plan to start work on now".
- `draft/bug/priors/12_single_source_density_refactor.md`
- `draft/bug/priors/13_collapse_prior_and_message.md`
- `draft/bug/priors/14_replace_transform_stack_with_bijectors.md`

  (12/13/14 are `too-large` architectural refactors of the `Prior`/`Message`
  hierarchy. The *answer* is known — it is blast radius, not uncertainty — so if the
  folder is defined strictly as "outcome unknown", these three may belong in
  `draft/` with a better difficulty signal instead. **Resolve this with the human
  before moving them**; it is the same judgement as the design question above.)

Plus today's work:

- `complete/archive/shelved/ep_scale_collapse_basin_cure_or_caveat.md` **and its
  sibling `ep_scale_collapse_leg2_assets/` directory** — move both. That prompt is
  live-but-human-gated, not retired, so `complete/archive/shelved/` (retired
  material, skipped by `lifecycle.py check`/`index`) is the wrong home for it. Keep
  the assets adjacent to the prompt; they are a working repro and the expensive part
  of that record.

## What deliberately does NOT move

- `draft/feature/autofit/ep_analytic_updates.md` — despite being `large` and
  EP-adjacent, it is the *most tractable* EP task in the backlog: a complete
  implementation plan already exists on PyAutoFit#1338, WP1 is **unblocked**
  (PyAutoFit#1334 merged) and estimated at 2-3 days, and the prompt says "rebase,
  don't wait". Moving it would hide the one EP task an agent can actually start.
- Anything whose only problem is size. `too-large` already communicates size; this
  folder is about *uncertainty of outcome* and the need for human steering.

## Acceptance

- `human_required/` exists with the six (or three, per the open question) prompts
  plus the shelved leg-2 prompt and its assets, laid out as
  `<work-type>/<target>/<name>.md`.
- `lifecycle.py check` passes, and **fails** on: a file present in both
  `human_required/` and another state dir, and a header/folder mismatch per the
  chosen design. Both cases covered by `tests/test_lifecycle_check.py`.
- `intake census` / `dashboard` report `human_required/` as its own band; the
  backlog total does not silently drop by the number of files moved.
- `REFERENCE.md`, `AGENTS.md`, `ROUTING.md` and `AUTONOMY.md` describe the folder,
  and `AGENTS.md`'s stale README pointers are corrected.
- `/start_dev human_required/<path>` still resolves for a deliberate human start.

## Traps

- **Two repos, one behaviour.** Landing only the PyAutoMind half leaves the folder
  invisible to intake and the dashboard. If they must ship as separate PRs, land
  PyAutoMind first and say in its PR body that the Brain half is owed.
- **Do not let the dashboard total silently shrink.** Moving ~7 prompts out of the
  backlog will look like progress in `dashboard.md` unless the new band is reported.
- **`git mv`, never delete-and-recreate** — these prompts carry long, valuable
  histories (the math audit has per-finding verdict blocks added over months).
- **`complete/archive/` is skipped by `lifecycle.py check`/`index`.** The leg-2
  prompt currently benefits from that exemption; once it moves into a *live* folder
  it will be checked, so make sure it satisfies whatever header rule is chosen.

<!-- filed 2026-08-11, from the session that shipped
     complete/2026/08/ep-hierarchical-scale-collapse-guard.md and then shelved its
     leg 2. The folder is the generalisation of that shelving decision. -->
