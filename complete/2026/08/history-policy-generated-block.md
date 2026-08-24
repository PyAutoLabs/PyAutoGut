# Single-source the "Never rewrite history" policy as a generated AGENTS.md block

- shipped: 2026-08-23 (Mind `18a6a82b`).
- classification: maintenance (PyAutoMind + every repo in `repos.yaml`).
- what landed, exactly as the prompt specified:
  - the canonical text lives in a file, not a code constant —
    `PyAutoMind/policy/never_rewrite_history.md` (`HISTORY_POLICY_FILE`), the
    recommendation the prompt made so a safety policy is editable without
    touching generator code;
  - `scripts/repos_sync.py` gained `load_history_policy()` +
    `HISTORY_BEGIN`/`HISTORY_END` (`<!-- repos_sync:history:begin/end -->`) and
    writes the block into every checked-out repo's `AGENTS.md` on `--write`,
    opt-in by markers and tolerant of absent repos, mirroring the `system_map`
    rollout;
  - `check_history_blocks()` is a registered check in `main()`, so a stale block
    fails the drift guard rather than rotting.
- the guardrail was not weakened: the full `## Never rewrite history` section is
  still inline and always-loaded in every `AGENTS.md` (verified in PyAutoMind and
  PyAutoBrain), and `PyAutoMind/AGENTS.md` § Hard rules keeps its one-line summary.
  The 2026-07-12 proposal to simply delete the section stays rejected.
- epic context: `complete/archive/epics/agents_md_standardization.md`, whose fourth
  generated block this was.

## Lifecycle note

Shipped without a completion record and never advanced out of `draft/`, so it kept
rendering as pickable backlog against machinery that is already on `main` and
CI-gated. Recorded here by the 2026-08-24 completed-prompt reconciliation sweep.

## Original prompt

# Single-source the "Never rewrite history" policy as a generated AGENTS.md block

Type: maintenance
Target: PyAutoMind
Repos:
- PyAutoMind
- every repo in repos.yaml (the block lands in each repo's AGENTS.md)
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised
Filed: 2026-07-12 (backfilled from git)

Single-source the "Never rewrite history" policy. The **`## Never rewrite
history`** section is necessary safety text — it guards a documented, expensive,
recurring failure (the "Initial commit — fresh start for AI workflow" pattern
that hit three workspace repos on origin *and* local, ~40 redundant commits each
time) and agents genuinely reach for `git init` / force-push / history rewrites
when disoriented. **It must stay inline in every repo's `AGENTS.md`** (a pointer
would be skipped under load, and the failure is destructive). The problem is only
that it is **verbatim-copied** across every repo — drift-prone, and against the
"duplication is a bug, drift-check it" doctrine. Fix the duplication *without*
weakening the guardrail: keep one canonical copy and **generate** the identical
block into every repo, drift-checked — exactly the `repos_sync:map` mechanism.

**This is NOT a deletion.** The safety text remains inline and always-loaded in
every `AGENTS.md`; only the manual copy-paste is removed. Do not strip the
guardrail — an earlier proposal to simply delete the section was rejected
(2026-07-12) for that reason.

**The standard:**
- One canonical copy of the policy text (preserve the current fullest wording
  verbatim — the `## Never rewrite history` block in `PyAutoMind/AGENTS.md` /
  `PyAutoBrain/AGENTS.md`; do not soften the list or the "only correct clean
  sequence").
- A generated, drift-checked `<!-- repos_sync:history:begin/end -->` block in
  **every** repo's `AGENTS.md` — *all* repos, not just organs (history policy is
  universal, unlike the organ-only map block).

**Mechanism (mirror `system_map`):**
- Add a `history_policy()` generator to `PyAutoMind/scripts/repos_sync.py`
  emitting the canonical text, plus `HISTORY_BEGIN/END` markers.
- Extend the `--write` loop to fill the history block in every checked-out repo's
  `AGENTS.md` via `write_block(..., required=False)` (opt-in by markers, tolerant
  of absent repos — same as the map rollout).
- **Migration:** in each repo, replace the hand-written `## Never rewrite history`
  section with the `## Never rewrite history` heading + the marker block, then run
  the generator. Confirm the generated text is byte-identical to what it replaced
  before committing (no silent wording change).

**Decisions to settle during intake back-and-forth:**
- **Where the canonical text lives.** In-code constant in `repos_sync.py` (matches
  how `system_map` embeds fixed prose) vs a dedicated markdown file (e.g.
  `PyAutoMind/policy/never_rewrite_history.md`) the generator reads (more
  human-editable for a policy doc). Recommend the file — a safety policy should be
  editable without touching generator code.
- **The short summary stays.** `PyAutoMind/AGENTS.md`'s `## Hard rules` item 1 is a
  one-line summary of the same rule; keep it (a summary, not a duplicate of the
  full block) — decide whether other repos want the same one-liner.
- **Scope confirmation.** All repos in `repos.yaml`, gated on the repo having an
  `AGENTS.md`; repos without one are reported, not auto-created (same rule as the
  CLAUDE.md standardization).

**Boundaries / relation to the other sweeps:** this rides the **same cross-repo
pass** as `z_features/agents_md_standardization.md` (add it as a fourth generated
block) and reuses `write_block` + the marker convention. Distinct from the map
block only in scope (all repos vs organs). Touches no git behaviour — it just
single-sources the *text* of an existing rule.

<!-- filed 2026-07-12 from a /remote-control conversation. Chosen over a straight
     deletion of the section (rejected: it's necessary safety text against a
     documented recurring incident). The real issue was verbatim duplication;
     fix = canonicalize + generate, like the organism-map block. -->
