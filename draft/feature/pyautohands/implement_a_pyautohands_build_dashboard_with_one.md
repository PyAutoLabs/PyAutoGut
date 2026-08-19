# Implement a PyAutoHands build dashboard with one-tap copy-for-Claude commands

Type: feature
Target: pyautohands
Repos:
- pyautohands
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised

Implement a PyAutoHands build dashboard with one-tap copy-for-Claude commands

Add a new generated dashboard feature to @PyAutoHands, in the style of the Mind task dashboard's one-tap pattern: a phone-readable view of build and release state — recent build and notebook-generation runs, current version stamps and pins, the release train's last outcome — where each actionable item carries a one-tap copy block holding the command that drives it in a Claude Code chat (/build, /release rehearse, /release validate, a targeted re-run). Rendered as a generated markdown page plus a one-tap-copy HTML twin on GitHub Pages, reusing the pattern shipped for the Mind dashboard.

The data comes from what Hands already knows about builds, but deciding which build facts are genuinely useful on a phone, where they live, and how fresh they must be is design work across several Hands surfaces — scope that first. Supervision required: the dashboard must not misreport release state, so a human should review what it claims before it ships. Not a quick unattended win.

<!-- formalised by the Intake (Conception) Agent on 2026-08-19 from user-intake -->
