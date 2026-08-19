# Actionable health board: one-tap prompts, links, dev-box enrichment

Type: feature
Target: pyautoheart
Repos:
- PyAutoHeart
- PyAutoMind
Difficulty: medium
Autonomy: supervised
Priority: high
Status: formalised

Rescoped 2026-08-19 from the intake prompt "One-tap dashboard pattern: roll out to
more organs" — this is its top surface (the @PyAutoHeart board), expanded with the
human's direction from the readability session. The remaining candidate surfaces
(complete/ archive page, ideas.md one-tap intake) split into
`draft/feature/pyautobrain/one_tap_dashboard_more_surfaces.md`.

Original intake text (verbatim, trimmed to the Heart leg):

> The PyAutoMind task dashboard now ships as a generated pair: dashboard.md rendered
> for GitHub plus a self-contained dashboard.html twin with real copy-to-clipboard
> buttons, served by GitHub Pages, drift-checked and self-healed together. Generalize
> this into a reusable pattern and apply it to further surfaces across the organism.
> Most valuable first: @PyAutoHeart health/readiness page — the /health verdict
> readable on a phone, with one-tap copy of the dispatch commands it recommends.

Human direction (2026-08-19 session, verbatim):

> Ok, now we will work on PyAutoHeart, noting that last night we filed an issue about
> getting its dashboard on par with autominds, which at the moment is not true. This
> would include the html for phone coping, claude prompts to work on specific tasks.
> I guess more work to make these, "not observed here (dev-box only)", actually
> useable would be good. Decluttering the repo so only the useable stuff is on the
> main page is good. The README.md should be like PyAutoMinds, a description of the
> organ, what it does and how it works, with the info to use it on a separate
> dashboard page like automind. Ok I just found the autoheart dashboardm it looks
> good and cool and I like its color and red yellow green, however the ability to
> more directly go from a green yellow or red to a copy'd claude prompt on laptop or
> mobile (mainly this) is obviously pretty damn cool. If possible, an easiest
> mechanism to go from dashboard to effected repo example, issue or script would be
> good but may not always be possible. Oh I also like the CLI examples on README.md
> which could come after how it works. section.

Agreed scope (plan approved 2026-08-19):

- Board actions: structured blockers ({text, repo, url, prompt}) from the cached
  ci_status run urls; 📋 copy buttons on the Pages html (mobile-first) copying
  `/bug …` prompts; links to repo + failing run; fix.py prompt builders extracted
  pure and reused.
- Dev-box rows: each grey family self-describes + carries a copyable observe command;
  new `pyauto-heart publish` pushes a distilled `state/devbox_board.json` (no local
  paths) so the cloud page renders real dev-box data age-stamped ("observed Nh ago on
  dev box"). Human chose commands + publish; README block becomes an md-brief strip.
- README restructured on the Mind pattern (organ description, How PyAutoHeart works,
  CLI examples after it, pointers); new REFERENCE.md consumes
  health_agent/capabilities.md; AI_POLICY/CONTRIBUTING → .github/; stale
  pyautobuild_boundary_audit.md deleted.
