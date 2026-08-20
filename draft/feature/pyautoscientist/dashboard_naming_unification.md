# Dashboard naming unification — every board is "<Repo> Dashboard", html primary

Difficulty: easy
Autonomy: supervised

## Original request (verbatim)

> Yesterday we did a lot of working making dashboards for all PyAutoScientists
> repos, and they are great. In PyAutoMind, we split the normal dashboard (.md)
> and the mobile phone dashboard (.html). However, the latter is superior than
> the first for user itnteract, and the same is true of all other dashboards.
> Therefore on all repos dont say "PyAutoMind Dashboard (mobile phone
> dashboard)" but just say "PyAutoMind Dashboard" with a link to the html
> (e.g. https://pyautolabs.github.io/PyAutoMind/). For PyAutoMemory dont call
> it "PyAutoMemory Knowledge Board" but just the "PyAutoMemory Dashboard",
> they are all dashboards. The PyAutoMind html dashbard has a link to the
> markdown high up with "markdown version", make sure this is high up on all
> dashboards. Make sure you do this on PyAutoScientist too.

## Scope

Follow-up polish to the closed one-tap-dashboard-rollout arc
(`complete/2026/08/one-tap-dashboard-rollout.md`). Three unifications across
the five boards (@PyAutoMind, @PyAutoHeart, @PyAutoHands, @PyAutoMemory,
@PyAutoScientist):

1. **One name: "<Repo> Dashboard".** READMEs and rendered surfaces stop saying
   "(mobile phone dashboard)", "Knowledge Board", "Release Board", "Organism
   Board" — each board is just "<Repo> Dashboard", link text pointing at the
   html Pages URL as the primary surface.
2. **Html is primary.** Where a README currently links the markdown first
   (PyAutoMind), flip it: the dashboard link goes to
   https://pyautolabs.github.io/<Repo>/.
3. **"markdown version" link high up** on every html dashboard, as the Mind
   board already has (where a markdown twin exists or can be published).

Renderers involved: Mind `dashboard.md`/`dashboard.html` generator,
`PyAutoHeart/heart/dashboard.py`, `PyAutoHands/autohands/board.py`,
`PyAutoMemory/scripts/board.py`, `PyAutoScientist/scripts/organism_board.py`,
plus the five READMEs.

**Contract guard:** `badge.json` messages and the Mind counts table are parsed
by the organism router — naming changes must not reshape badge messages or the
counts-table format (see memory: readability-dashboard-arc).
