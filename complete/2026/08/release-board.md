- issue: https://github.com/PyAutoLabs/PyAutoHands/issues/239 (auto-closed on merge)
- shipped: 2026-08-19 — PyAutoHands PR https://github.com/PyAutoLabs/PyAutoHands/pull/241
  (squash `6ef5fcd`); board LIVE same evening at https://pyautolabs.github.io/PyAutoHands/
  with the badge and README strip auto-committed.
- classification: feature (PyAutoHands) — fourth repo of the readability arc; implements
  the intake prompt "PyAutoHands build dashboard with one-tap copy-for-Claude commands".
- summary: the release board — a phone-readable, PAST-TENSE record of what the Hands
  shipped. `autohands/board.py`: thin collect (GitHub REST via gh + PyPI JSON) + pure
  render (md / md-brief / html / json / badge) on the Heart dashboard.py pattern.
  Surfaces: released library versions (version-scheme-max git tag), ship dates (decoded
  from the YYYY.M.D version string), PyPI liveness/yanks, the release train's recent
  runs with durations and links (failed runs copy a `/bug … — <run url>` prompt), the
  nightly cadence strip, and one-tap chips for /release, /release rehearse,
  /release validate, /build. Readiness explicitly deferred + linked to the Heart board.
  `bin/autohands board` verb; `release_board.yml` publishes Pages + badge.json + the
  README `hands:begin/end` strip after every "PyAuto Release" run, daily, and on
  dispatch. README rewritten on the arc pattern (stale "Formerly PyAutoBuild" banners
  dropped — rename shipped 2026-07; released badge; Latest release strip; How
  PyAutoHands works; CLI examples); AGENTS.md verb-registry prose fixed;
  AI_POLICY/CONTRIBUTING → .github/ (all four organs now match).
- validation: 324/324 tests (10 new) on 3.12/3.13/3.14 + tenant firewall green; live
  render cross-checked against `gh api .../tags` and `gh run list` (all five libraries
  at 2026.8.17.1, both red train runs shown); page + badge + strip verified live.
- key traps:
  - **The tags API is NOT date-ordered** — naive `tags?per_page=1` surfaced a junk
    `pull` tag (PyAutoFit) and a 2021 `v1.15.2` (PyAutoLens). Pick the max
    version-scheme tag numerically.
  - **The tagged commit's date is not the ship date** — a quiet library's last commit
    predates the release by weeks; the `YYYY.M.D` version string IS the ship date.
  - **`configure-pages enablement: true` could NOT create the site** here ("Resource
    not accessible by integration") despite the Mind/Heart precedent — the site was
    created once out-of-band (`gh api -X POST repos/<owner>/<repo>/pages -f
    build_type=workflow`) and the workflow works from then on.
  - Run durations use `run_started_at`, not `created_at` — re-attempted runs otherwise
    report multi-day durations.
  - data-copy clipboard payloads legitimately carry URLs — the html self-containment
    test strips them before asserting every URL is an href.
- follow-up drafts filed: local run_logs enrichment of the board (Heart devbox-merge
  style) and Hands hygiene (expired ANNOUNCEMENT dead code in
  generate_release_notes.py:23-46; whether the unregistered navigator/etc. modules
  should become CLI verbs).
- affected-repos:
  - PyAutoHands

## Original prompt

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
