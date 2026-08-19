# PyAutoHands release board with one-tap copy-for-Claude commands

Type: feature
Target: pyautohands
Repos:
- PyAutoHands
- PyAutoMind
Difficulty: medium
Autonomy: supervised
Priority: high
Status: formalised

Original intake text (verbatim, formalised 2026-08-19 from user-intake):

> Add a new generated dashboard feature to @PyAutoHands, in the style of the Mind task
> dashboard's one-tap pattern: a phone-readable view of build and release state — recent
> build and notebook-generation runs, current version stamps and pins, the release
> train's last outcome — where each actionable item carries a one-tap copy block holding
> the command that drives it in a Claude Code chat (/build, /release rehearse, /release
> validate, a targeted re-run). Rendered as a generated markdown page plus a one-tap-copy
> HTML twin on GitHub Pages, reusing the pattern shipped for the Mind dashboard.
>
> The data comes from what Hands already knows about builds, but deciding which build
> facts are genuinely useful on a phone, where they live, and how fresh they must be is
> design work across several Hands surfaces — scope that first. Supervision required:
> the dashboard must not misreport release state, so a human should review what it
> claims before it ships. Not a quick unattended win.

Scoping done + plan approved 2026-08-19 (fourth repo of the readability arc):

- **API-first data** (the scoping question answered): `run_logs/` is gitignored,
  machine-local and currently absent, so v1 renders from verified-live cloud sources —
  release.yml run history (Hands) + nightly-release.yml outcomes (Brain) via gh, git
  tags on the 5 libraries (the authoritative version record — build-tree stamps are
  never committed), the PyPI JSON API (liveness/yanks), GitHub Releases notes links.
  A degraded API section says so honestly — never fabricated. Local run_logs
  enrichment (Heart devbox-merge style) split to a follow-up draft.
- **Boundary**: the board is a past-tense record of what was EXECUTED — versions
  shipped, tags cut, notebooks regenerated, train outcomes. Never a verdict/score/gate;
  it links the Heart board for readiness.
- New `autohands/board.py` (thin collect + pure render, Heart dashboard.py pattern;
  fmt md/md-brief/html/json/badge; 📋 chips for /release, /release rehearse,
  /release validate, /build; failed train runs copy /bug prompts with the run URL);
  `bin/autohands board` verb; `release_board.yml` publisher (workflow_run after
  "PyAuto Release" + daily cron + dispatch → Pages html + badge.json + README strip
  between hands:begin/end markers). Owner derived from git remote; repo lists from a
  declared config surface (tenant firewall).
- README rewritten on the arc pattern (stale "Formerly PyAutoBuild" banners dropped —
  the rename shipped 2026-07-23; released badge; Latest release auto-strip; How
  PyAutoHands works; CLI examples); AGENTS.md verb-list prose fixed to the real
  dispatcher registry; AI_POLICY/CONTRIBUTING → .github/.
