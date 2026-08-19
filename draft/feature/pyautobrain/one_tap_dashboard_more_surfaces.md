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
