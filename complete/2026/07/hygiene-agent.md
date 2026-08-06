## hygiene-agent (Phases 1-3 — conductor complete)
- issues: PyAutoBrain#87 + #89 + #91 (all closed) + research/pyautobrain/hygiene_agent_decision.md (decided)
- completed: 2026-07-11
- prs: PyAutoBrain#88 (scaffold) + #90 (tidy/noise/deps/docs modes) + #92 (perf mode) — all MERGED 2026-07-11 (squash), all --auto supervised, shipped on live human sign-off
- summary: grew a new PyAutoBrain **hygiene conductor** (code-quality upkeep — dev-loop cost + repo tidiness, distinct from Heart's proof-of-works and profiling's modelling speed). DECISION: conductor, **no new paired repo** (reuse Heart for tracking; a repo is earned by a persistent artifact lifecycle, which hygiene lacks). Five modes, each a cheap read-only **pre-scan + delegate** (conductor never mutates): tidy→/repo_cleanup (debris), noise→/cli_noise_clean (advisory), deps→/dep_audit (surface), docs→/audit_docs (surface), perf→/refactor (timing — import cost in a subprocess so the conductor never imports JAX; slow tests/scripts read from Heart script_timing/test_run). Corrected the profiling `vs hygiene` boundary + moved "slow integration-fn hunting" into perf. Absorbed/repointed the scattered hygiene skills. `/hygiene` live in Claude+Codex. Traps: every public agent needs BOTH skills/<n>/SKILL.md + <n>.md (test_skill_install enforces); squash-merge → branch -D; gh pr create needs a git cwd. Deferred optional follow-up FILED: standing PyAutoHeart import_time leg (promote the import pre-scan to a tracked signal, wire perf to consult it) → PyAutoHeart#61 + issued/hygiene_import_time_leg.md (low priority, not started; crux = <30s tick budget vs multi-second cold imports; cli_noise leg likely can't fit budget). 3 calibration rows (all pr-open→merged). Design of record: issued/hygiene_agent.md.

## Original prompt

# Hygiene agent

Type: feature
Target: PyAutoBrain
Repos:
- PyAutoBrain
- PyAutoHeart
Difficulty: too-large
Autonomy: supervised
Priority: normal
Status: formalised

Hygiene agent. Grow a PyAutoBrain **conductor** — the *Hygiene Agent* foreshadowed as the "Future Cleanup Agent" in `PyAutoBrain/skills/repo_cleanup/SKILL.md` — that owns the organism's code-**quality** upkeep: the work that improves the code but is neither required to prove it works (health/PyAutoHeart) nor about the speed of modeling compute (profiling/autolens_profiling). Its charter is the *developer-loop cost and code tidiness* of the whole organism: unit-test wall-time, workspace/integration-script time in test mode (`PYAUTO_TEST_MODE` + `PYAUTO_SMALL_DATASETS`), running workspace scripts in normal mode to time slow functions (and JAX-adapting them where a quick win exists — judgement required, no forced rewrite), import-time profiling, CLI noise, dependency-cap drift, stale API docs, git debris, and adjacent standard hygiene (dead-code / unused-import detection, deprecation-warning sweeps, coverage gaps, lint/type-hint drift, flaky-test detection).

**Decision settled with the user (2026-07-11), resolving `research/pyautobrain/hygiene_agent_decision.md`: build a conductor, and it needs NO new paired repo.** Rationale grounded against how the organs are actually wired, not the metaphor: (1) the *observation/tracking* substrate hygiene needs already exists in **PyAutoHeart** — the `script_timing` and `test_run` legs already measure and track dev-loop timing; extend Heart with new legs (`import_time`, `cli_noise`) if persistent tracking is wanted, rather than minting a repo that would duplicate Heart's job. A repo is earned by a persistent reusable-artifact lifecycle (Heart: check functions + verdict history; profiling: timing tables/baselines/pins in autolens_profiling) — hygiene has none: its output is a prioritized worklist that lives in Mind issues. (2) Its *actions* are ordinary dev-flow edits that ship through `ship_library`/`ship_workspace` and delegate the actual fix to `bug` (regression-shaped) or `refactor` (restructure) — no novel function library for a repo to hold. (3) Its real value is Brain-internal orchestration: unifying the already-scattered hygiene skills (`repo_cleanup`, `cli_noise_clean`, `dep_audit`, `audit_docs`) under one prioritizing conductor and adding the perf-hygiene modes. That is exactly a conductor's shape (decide-AND-act, recurring cadence), and the "smaller than Heart" instinct is correct: it is an orchestrator, not an organ.

**First increment — a `HygieneDecision`-emitting conductor at `agents/conductors/hygiene/` with modes over the whole workspace:**
- `perf` — time unit tests / integration-mode workspace scripts / import cost; classify slow items and route them (refactor for restructure, bug for regressions, JAX-adapt only where a quick win is clear).
- `tidy` — absorb `repo_cleanup` (git debris: stale branches, stashes, `[gone]` refs, dirty checkouts) as a native mode.
- `noise` — absorb `cli_noise_clean` (warnings, stray prints, library noise).
- `deps` — consult `dep_audit` (version-cap drift vs PyPI).
- `docs` — consult `audit_docs` (stale `docs/api/*.rst` module paths).
- default (no-arg) — audit across all modes and emit one prioritized worklist.

**Boundaries (settle in the agent's AGENTS.md):**
- vs **profiling** — draw the line by *what* is measured: profiling = the product's/modeling compute speed (likelihood on the science grid, GPU tiers, vram, A100, baselines/pins); hygiene = the developer loop's cost (unit tests, TEST_MODE/SMALL_DATASETS scripts, import time). **Move** profiling's staged future mode "hunting generally-slow functions flagged by integration tests" into hygiene, and update `agents/conductors/profiling/AGENTS.md`'s `## vs hygiene` block (currently only says "Heart observes noise / Brain `repo_cleanup` mutates", stale once hygiene is a real conductor). JAX-adaptation is shared: hygiene flags a dev-loop function and delegates; a likelihood on the grid is profiling's call.
- vs **health** — Heart *observes* (add legs), the hygiene conductor *acts* — the same split the health conductor already follows. Consults the vitals faculty like every conductor; never issues health verdicts.
- vs **bug / refactor** — hygiene *finds and prioritizes* quality debt and *delegates the fix*; it does not reinvent fix machinery.
- vs **build** — hygiene is not release work; it never touches PyAutoBuild.

Implementation is ordinary feature/pyautobrain work per ROUTING.md (mirror the profiling conductor's structure: `AGENTS.md` + `hygiene.sh` + any stdlib-only helper; absorb the two skills, re-point the consulted two). Confirm the PyAutoBrain claim is free at `start_dev` branch-survey time (profiling and clone-mitosis have both shipped). Update `repo_cleanup/SKILL.md`'s "Future Cleanup Agent" note to point at the now-built conductor.

<!-- formalised 2026-07-11 from a /remote-control design conversation that settled the
     open question in research/pyautobrain/hygiene_agent_decision.md: conductor, no repo,
     reuse Heart for tracking, absorb repo_cleanup + cli_noise_clean, consult dep_audit +
     audit_docs, take over profiling's slow-integration-function future mode. -->
