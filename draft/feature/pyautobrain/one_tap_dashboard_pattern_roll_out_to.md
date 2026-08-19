# One-tap dashboard pattern: roll out to more organs

Type: feature
Target: PyAutoBrain
Repos:
- PyAutoBrain
- PyAutoHeart
- PyAutoMind
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised

One-tap dashboard pattern: roll out to more organs

The PyAutoMind task dashboard now ships as a generated pair: dashboard.md rendered for GitHub plus a self-contained dashboard.html twin with real copy-to-clipboard buttons, served by GitHub Pages (pages_dashboard.yml), drift-checked and self-healed together, with links and identity derived from repos.yaml. Generalize this into a reusable pattern and apply it to further surfaces across the organism.

Candidate surfaces, most valuable first:
- @PyAutoHeart health/readiness page: the /health verdict readable on a phone, with one-tap copy of the dispatch commands it recommends.
- The @PyAutoMind complete/ archive index as a browsable shipped-work page, each record one tap from a /memory recall query.
- The @PyAutoMind ideas.md inbox with one-tap /intake payloads so filing an idea from a phone is copy then paste.

Deliverable: extract the page template and Pages workflow shape into a reusable form in @PyAutoBrain (the renderer already lives with the intake conductor) and apply it to at least one new surface. Multi-organ design work: the renderer generalization needs care so each organ keeps owning its own data. Supervision required; not a quick unattended win.

<!-- formalised by the Intake (Conception) Agent on 2026-08-19 from user-intake -->
