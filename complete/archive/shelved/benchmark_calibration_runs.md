# First benchmark calibration campaign — run the 4 assistant benchmarks across models

Type: research
Target: autolens_assistant
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: filed

Follow-up to feature/autolens_assistant assistant_benchmarks (issue
https://github.com/PyAutoLabs/autolens_assistant/issues/57): the benchmark
package ships four frozen prompt cards (`benchmarks/prompts/`) and the
run/track harness (`autoassistant/benchmark.py`), but `benchmarks/runs/` is
empty. Run the first calibration campaign so the comparison tables have real
rows and the rubrics get validated against real transcripts.

Scope:

- Run at least the two cheap benchmarks (`teacher-basic-workflow`,
  `assistant-easy-cosmos-web-ring`) on 2+ model×harness combinations (e.g.
  Claude Code with two different models; add Codex/Gemini if convenient), per
  the protocol in `benchmarks/README.md` — fresh sessions, prompts verbatim,
  operator behaves like a real user, no coaching.
- Record every run (transcript, meta.yaml with hardware/duration, artifacts),
  score with evidence, regenerate `RESULTS.md`, commit + push.
- The medium/hard benchmarks are hours-scale: run at most one of them once,
  or explicitly defer them with a runtime note.
- Deliverable beyond the run records: a short calibration verdict on the
  rubrics themselves — were any rows unscoreable, ambiguous, or trivially
  gamed? File rubric fixes as `version`-bump proposals rather than editing
  cards in place.

Blocked until the assistant-benchmarks PRs are merged (the cards/harness must
be on main so runs execute against the published, frozen prompt versions).

## SHELVED 2026-08-18 — campaign abandoned, not deferred

Author decision: the calibration campaign will not be run. Shelved here rather
than lost; pull back into `draft/research/autolens_assistant/` if that changes.

**The dedicated issue was already closed.** `autolens_assistant#59` (this
campaign) was closed on/before 2026-07-15 to release the repo claim that was
blocking the JOSS paper task — see `complete/2026/07/pyautolens-assistant-joss-paper.md`,
which flagged the discrepancy as needing a look. That question is now answered:
verified against autolens_assistant main on 2026-08-18, `benchmarks/runs/`
contains only `.gitkeep`, so **#59 closed without ever producing runs**. Nothing
is open on GitHub. Only the Mind-side residue (this prompt, the `parked.md`
entry, the dashboard row) survived, and it is removed with this commit.

**State of the benchmark package as of 2026-08-18** (in case anyone revives it):
the four frozen cards (`benchmarks/prompts/`) and the harness
(`autoassistant/benchmark.py`) are on main and working; `RESULTS.md` records
zero runs for all four benchmarks. The blocker this prompt described had
cleared — the campaign was simply never a cost the author wanted to pay.

**Pre-run rubric findings, preserved.** A read-only audit of the cards and
harness surfaced issues that would bite any future campaign — worth reading
before re-filing rather than rediscovering:

- The frozen-prompt rule is enforced by nothing.
  `autoassistant/tests/test_benchmark.py:170-176` asserts only
  `prompt.strip() in readme`, for three of the four cards; no test binds a
  card's prompt text to its `version`. A coordinated README+card edit passes CI
  with `version` unchanged, so `meta.yaml` keeps recording the same
  `prompt_version` across a changed prompt. `hard_group_multi.md` has no freeze
  check at all.
- The "Machine-checkable" band is never machine-checked. `parse_score`
  (`benchmark.py:215-244`) sums whatever the operator typed; nothing inspects
  `scripts/`, `output/` or figures, and "Machine rows (M*) need verifiable
  evidence" (`benchmark.py:151`) is prose in the generated `score.md`, not a
  check — `score_run` rejects only unfilled *Awarded* cells, never empty
  Evidence.
- Rows satisfiable without the work: `easy M4/M5` reward *showing a path*
  rather than the figure existing; `medium M4` gives 5 points for printing two
  numbers a fabricating run could invent, while `J5` separately penalises
  fabrication; `teacher M3` sets no agreement threshold, so a comparison
  showing recovery failed scores full marks.
- Evidence double-counted on the hard card: `M1`/`J1` both score the quad
  verification, and `M4`/`J4` both score the follow-up composition — a run that
  completes M4 cannot fail J4. Note `test_repo_prompt_cards_parse` asserts
  `machine + judged == 100`, so any fix needs an explicit re-split.
- Compound rows bundle orthogonal failures: `J5 "Conduct"` (10 pts, all three
  assistant cards) mixes concision, fabrication and API-gate discipline. The
  real-data gate is a 15-point row on `easy` but folded into a shared 10-point
  row on `medium`, distorting cross-card comparison of the same behaviour.
- `medium J2` (15 pts) says the HPC option may be "set up **or offered**",
  letting one sentence carry most of the row.
- Undefined discriminators: `easy M2`'s "not test-mode", `hard M3`'s proof of a
  simultaneous fit, and `teacher J4`'s Euclid tolerance (stated in card prose,
  not the rubric row).

Sequencing note for any revival: scores are comparable only within a card
`version`, so rubric fixes must land *before* a campaign — fixing them
afterwards splits the comparison tables and forces a re-run.
