- issue: https://github.com/PyAutoLabs/PyAutoBrain/issues/237 (auto-closed on merge)
- shipped: 2026-08-19 — PyAutoBrain PR https://github.com/PyAutoLabs/PyAutoBrain/pull/238
  (squash `2b714b8`); CI green on pytest 3.12/3.13 + tenant firewall + docs build.
- classification: maintenance (PyAutoBrain) — third repo in the readability arc
  (PyAutoMind #248, PyAutoHeart #151). Human-set scope: declutter + README clear-up
  only, NO Brain dashboard (parked in
  draft/research/pyautobrain/explore_dashboardify_the_brain_s_operational_sur.md,
  where "none" is a valid recommendation).
- summary: README rewritten on the established pattern — 4-line organ opening,
  drive-it-in-plain-English paragraph, sequential "How PyAutoBrain works" (task
  arrives → conductor decides+acts → faculties advise with the consult-DAG rule →
  Brain → Heart → Hands → autonomy contract), CLI examples, closing pointers. The
  drifted hand copies (a 6-organ table vs the canonical 7; 5 of 18 verbs) were
  REPLACED by links to ORGANISM.md and AGENTS.md's generated table — README carries
  no hand copies of generated surfaces any more. ORGANISM.md currency: recorded the
  Nerves rename (PyAutoConf → PyAutoNerves, autoconf → autonerves) instead of
  asserting the old name; same fix in docs/example.md and four skill-doc prose
  mentions. AI_POLICY/CONTRIBUTING → .github/ (zero inbound refs; Brain was the odd
  organ out). 13 fully-merged remote branches deleted (38 unmerged left for
  /repo_cleanup).
- validation: 361/361 Brain tests; all repos_sync --check legs green after the
  ORGANISM edit (no generated-block drift — the map derives from repos.yaml);
  `install.sh --write-agents-surface` no-diff; docs warning baseline unchanged.
- key traps:
  - README.md is the ONLY unchecked front-door surface in Brain (three generators
    guard AGENTS.md/WORKFLOW.md) — hand-copied tables there WILL drift; link to the
    generated/canonical pages instead of copying them.
  - ORGANISM.md asserted "PyAutoConf remains the Nerves repo's name" — invalidated
    by the later rename cascade and never updated; canonical prose pages need a
    currency check whenever a rename ships.
  - Functional old-name sites deliberately NOT blind-renamed — filed as
    draft/bug/pyautobrain/pyautoconf_rename_functional_leftovers.md (policy.yaml
    activity-gate list + unit-test map may silently miss PyAutoNerves activity via
    GitHub redirects; repo_cleanup/reference.md:128 owner mapping is stale beyond
    the name). RTD narrative drift (no organs/nerves.md; five/six/seven organ-count
    disagreement; build.md→hands.md URL question) filed as
    draft/docs/pyautobrain/rtd_organism_currency.md.
- affected-repos:
  - PyAutoBrain

## Original prompt

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
