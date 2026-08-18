Seeded the inference programme's method-card layer
(`autolens_profiling/results/notes/inference/methods/`) from the existing
benchmark record — the PROGRAMME §6 knowledge structure the future
`autolens_workspace/scripts/guides/searches/` decision tree is generated
from. Documentation only; done entirely from a mobile/cloud session.

- **PR:** autolens_profiling#141 (merged `f980a0f`, closes #140).
- **Cards:** `nautilus.md` (CPU reference engine; seeded confidence),
  `nss.md` (fork-era record + logZ-bias hypothesis; anecdote, Gate A
  pending), `multi_start_prodigy.md` (θ_E=0 basin story + p_hit reframe;
  anecdote/seeded, Gate B pending), `multi_start_adam.md` (measured
  p_hit ≈ 0.18/start precedent; seeded). Template: IDENTITY / EVIDENCE /
  STRENGTHS & WEAKNESSES / CONFIGURATION / TERMINATION / HAZARDS /
  PERFORMANCE / RECOMMENDED / REFERENCES; every claim cites a result JSON,
  notes file, or PROGRAMME section — no new claims introduced.
- Also ticked Phase 0(e) complete (PR#139) in PROGRAMME.md's phase-state
  table and stamped 0(d) with its PR numbers — closing the follow-up recorded
  in the searches-readme-dashboard completion.
- **Programme state after this:** Phase 0 remaining = (b) blackjax ≥1.6.2
  upgrade (laptop + RAL) and (c) RAL artifact harvest — both need
  laptop/SSH, not mobile. Next mobile-feasible programme work: Phase 1
  `_targets.py` registry skeleton (code, no runs — needs care around heavy
  imports) or extending method cards as new evidence lands.

## Original prompt

# Seed the inference method evidence cards from the existing benchmark record

Type: docs
Target: autolens_profiling
Repos:
- @autolens_profiling
Difficulty: small
Autonomy: supervised
Priority: medium

The inference programme's knowledge structure
(`results/notes/inference/PROGRAMME.md` §6) calls for living method cards at
`results/notes/inference/methods/<method>.md`, from which the eventual
`autolens_workspace/scripts/guides/searches/` decision tree is generated.
None exist yet, but the evidence to seed them already does: the searches
benchmark artifacts (now surfaced by the fixed dashboard, #139), the
programme's state-of-play tables, the clipper-campaign notes, and the
point-source defaults campaign.

Task: seed four cards using the PROGRAMME §6 template (IDENTITY / EVIDENCE /
STRENGTHS & WEAKNESSES / CONFIGURATION / TERMINATION / HAZARDS / PERFORMANCE /
RECOMMENDED / REFERENCES), every claim citing a result JSON, notes file, or
PROGRAMME section — no new claims:

- `methods/nautilus.md` — the CPU reference engine; truth bars on
  imaging cells; the cluster/point-source answer today.
- `methods/nss.md` — BlackJAX nested slice sampling; fork-era benchmarks,
  the +7-13 nat logZ bias hypothesis, mainline 1.6 status; Gate A pending.
- `methods/multi_start_prodigy.md` — basin-hit story (seed 0/1 split),
  clipper/step-scaling arc, auto-convergence limits; Phase 3 pending.
- `methods/multi_start_adam.md` — p_hit ≈ 0.18/start, 128-start A100
  timing, the GIGA-Lens comparison.

Also tick Phase 0(e) as complete (PR#139) in PROGRAMME.md's phase-state
table (recorded follow-up from the searches-readme-dashboard completion).

Confidence tags per the programme: anecdote / seeded / gated. Documentation
only — no runs, no scripts, no source changes; ruff untouched; do not edit
inside auto-table sentinels.
