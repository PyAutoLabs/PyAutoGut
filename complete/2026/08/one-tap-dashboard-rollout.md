- issue: (no single issue — the arc's tasks carried their own: PyAutoMind#248 dashboard
  header, PyAutoHeart#151, PyAutoHands#239, PyAutoMemory#32, PyAutoScientist#12)
- shipped: 2026-08-19 — the one-tap dashboard rollout, closed by the human's call
  ("make sure the dashboard task itself we had all those notes is moved to complete").
- classification: feature (multi-organ) — the arc record for the intake prompt
  "One-tap dashboard pattern: roll out to more organs" and its rescoped descendants.
- summary: the pattern (a generated page + one-tap 📋 copy-for-Claude payloads, phone
  first) now covers the whole organism, FIVE live boards:
  - Mind task dashboard — https://pyautolabs.github.io/PyAutoMind/ (pre-arc; header
    trimmed + registry TOCs in #248)
  - Heart health board — https://pyautolabs.github.io/PyAutoHeart/ (#151: structured
    blockers, /bug prompts, dev-box publish with age stamps)
  - Hands release board — https://pyautolabs.github.io/PyAutoHands/ (#239: past-tense
    execution record, version-scheme tags, /release chips, /bug on failed runs)
  - Memory knowledge board — https://pyautolabs.github.io/PyAutoMemory/ (#32:
    management-first work queues — reading queue with DONE read-state, citation TODOs,
    maturity — plus /memory chips)
  - PyAutoScientist organism board — https://pyautolabs.github.io/PyAutoScientist/
    (#12: the umbrella ROUTER — each board's own headline + a where-to-work-next
    banner keyed off the Heart's verdict; the human's idea "if heart is ok there
    you'd go to Mind")
- NOT pursued (deliberate, recorded here so the notes survive): the two remaining
  candidate surfaces from the original intake — a browsable Mind complete/-archive
  page (each record one tap from a /memory recall) and ideas.md with one-tap /intake
  payloads. Re-file via /intake if ever wanted. The Brain "dashboardify the
  operational surfaces" research prompt stays parked as a draft by the human's call
  (no Brain dashboard; "recommending none" remains a valid outcome there).
- pattern learnings live in the per-task records (#248/#151/#239/#32) and the
  project memories: renderer-owns-the-text, render-in-CI-when-a-lint-bans-html,
  badge.json as the cross-board headline contract the umbrella router now consumes.

## Original prompt

# One-tap dashboard pattern: remaining surfaces

Type: feature
Target: pyautobrain
Repos:
- PyAutoBrain
- PyAutoMind
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised

Split 2026-08-19 from "One-tap dashboard pattern: roll out to more organs" — the
Heart-board leg went to `draft/feature/pyautoheart/actionable_health_board.md`
(issued). Remaining candidate surfaces, most valuable first:

- The @PyAutoMind `complete/` archive index as a browsable shipped-work page, each
  record one tap from a `/memory` recall query.
- The @PyAutoMind `ideas.md` inbox with one-tap `/intake` payloads so filing an idea
  from a phone is copy then paste.

Deliverable: extract the page template + Pages workflow shape into a reusable form in
@PyAutoBrain (the Mind renderer lives with the intake conductor; the Heart board now
has its own copy-button pattern in `heart/dashboard.py` to draw on) and apply it to at
least one of the surfaces above. Multi-organ design work: the generalization needs
care so each organ keeps owning its own data. Supervised; not a quick unattended win.
