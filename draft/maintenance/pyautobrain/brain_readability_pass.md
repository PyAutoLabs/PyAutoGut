# PyAutoBrain readability pass — README rewrite, root declutter, ORGANISM currency

Type: maintenance
Target: pyautobrain
Repos:
- PyAutoBrain
- PyAutoMind
Difficulty: medium
Autonomy: supervised
Priority: high
Status: formalised

Third repo in the readability arc (after PyAutoMind #248 and PyAutoHeart #151).
Human-agreed scope (2026-08-19): **declutter + README clear-up only — NO Brain
dashboard** (that question stays parked in
`draft/research/pyautobrain/explore_dashboardify_the_brain_s_operational_sur.md`,
where "none" remains a valid recommendation).

Agreed scope (plan approved 2026-08-19):

- README rewritten on the Mind/Heart pattern: 4-line organ opening, a
  drive-it-in-plain-English paragraph, a sequential "How PyAutoBrain works"
  (task arrives → conductor decides+acts → faculties advise (consult DAG) →
  organs execute Brain → Heart → Hands → autonomy contract), CLI examples
  after it, closing pointers. The hand-copied organ table (drifted to 6 organs)
  and partial verb list (5 of 18) are REPLACED by links to @PyAutoBrain/ORGANISM.md
  and the generated table in AGENTS.md — no hand copies of generated surfaces.
- ORGANISM.md currency: the Nerves organ is PyAutoNerves (`autonerves`) per the
  body map, but ORGANISM.md still says PyAutoConf/`autoconf` and asserts the old
  name "remains" — fix the row, the parenthetical, and the growth-rule mention;
  also `docs/example.md` and the prose mentions in start_library / ship_library /
  repo_cleanup / sampler_pipeline skill docs. Re-run
  `PyAutoMind/scripts/repos_sync.py --check` after (the map block derives from
  ORGANISM.md) and commit any regenerated sibling blocks.
- Root declutter: `AI_POLICY.md` + `CONTRIBUTING.md` → `.github/` (Brain is the
  odd organ out; zero inbound refs; no spawn contract); delete the 14 remote
  branches already merged into origin/main (unmerged ones stay for /repo_cleanup).
- Follow-ups filed as drafts, NOT this task: functional PyAutoConf leftovers
  (policy.yaml activity gate + unit-test map, scripts, test fixture) and RTD
  organism-docs currency (nerves.md page, organ-count drift, build.md→hands.md).

Constraints honoured: AGENTS.md generated blocks (pyauto:commands, repos_sync map
+ history), skills/WORKFLOW.md repos_sync block, bare CLAUDE.md pointer, docs
warning baseline, .claude/.codex symlink farms, and all bin//agents/ paths.
