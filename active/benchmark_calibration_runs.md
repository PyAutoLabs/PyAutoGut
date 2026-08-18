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

## 2026-08-18 — blocker cleared; rubric verdict taken early

Verified against a read-only clone of autolens_assistant main: the four frozen
cards (`benchmarks/prompts/`) and `autoassistant/benchmark.py` are present, and
`benchmarks/runs/` still holds only `.gitkeep`. The blocking condition above is
therefore **cleared** and the campaign is un-started, exactly as `parked.md`
records.

The final deliverable — the calibration verdict on the rubrics — was taken
early and filed as
`draft/bug/autolens_assistant/benchmark_rubric_freeze_and_scoring_gaps.md`
(9 findings: an unenforced prompt-freeze rule, a "machine-checkable" band the
harness never checks, gameable and double-counted rows, and several rows whose
discriminators the operator must invent).

**Resequence this prompt accordingly.** `benchmarks/README.md` makes scores
comparable only within one card `version`, so landing rubric fixes after the
campaign bumps the cards and splits the comparison tables — the runs would have
to be repeated. Land the harness fixes and the `version: 2` card bumps first,
then run the campaign once against v2. The remaining scope here is the runs
themselves.

Outstanding before the campaign can start:

- a human cost decision on which model x harness combinations to buy;
- a session with push rights to autolens_assistant, the bundled datasets and a
  GPU — a cloud Mind/Brain session cannot execute the protocol;
- an operator/judge who has **not** read the rubrics (the protocol's
  "no benchmark-aware behaviour" rule); the agent that produced the audit above
  is disqualified as an agent-under-test for these cards.
