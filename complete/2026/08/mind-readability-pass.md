- issue: https://github.com/PyAutoLabs/PyAutoMind/issues/248 (closed on ship)
- shipped: 2026-08-19 — Mind + Heart direct on main; Brain via PR
  https://github.com/PyAutoLabs/PyAutoBrain/pull/236 (squash-merged `4ff5919`)
- classification: maintenance (PyAutoMind primary; PyAutoBrain renderer; PyAutoHeart comments)
- summary: made PyAutoMind legible to an external viewer. Census (two sweeps: staleness +
  reference blast-radius) → root declutter instead of a `mind/` folder move (human-decided:
  `active.md`/`planned.md` are parsed by path from Brain, Heart, 3 workflows, ~30 skills and
  the spawn template contract — moving the ledger is a staged migration if ever wanted, not
  a tidy-up). README rewritten around a step-by-step "How PyAutoMind works"; dashboard header
  trimmed at the renderer; generated clickable contents blocks added to the long registry files.
- shipped changes:
  - README.md: 4-line opening, dashboard-in-practice paragraph, sequential capture → start →
    develop → complete guide with GitHub folder links (replaced the "What lives here" table).
  - Dashboard header (Brain `_intake.py` `render_dashboard`): one-tap-copy phone line first,
    two-sentence description, dropped the "Tasks only —" and "Live on GitHub" lines and the
    now-unused `GH_SEARCH` constant; HTML twin intro was already concise, untouched.
  - New `scripts/registry_toc.py` + 8 tests: `<!-- toc:start/end -->` contents block above the
    first `##` of planned/parked/condemned (GitHub-slug anchors, fence-aware, min 3 sections);
    self-healed by `dashboard_refresh.yml` on the dashboard contract (PR fail / main heal);
    `condemned.md` added to that workflow's path filters.
  - Root declutter: `AI_POLICY.md` + `CONTRIBUTING.md` → `.github/` (GitHub resolves
    community-health files there; spawn manifest/spec/tests updated in lockstep — Memory's
    copies deliberately stay at root); stale `overview.md` deleted; fully-consumed `queue.md`
    emptied (file kept — `/register_and_iterate` + spawn contract read it by path); the four
    uncalled `scripts/health*.sh` forwarding shims deleted after repointing Heart's three
    usage comments (`~/.bashrc` verified to source the Heart paths directly);
    `skills/OWNERSHIP.md` trimmed from a completed-migration record (dead `autoprompt/`,
    `admin_jammy/skills/` paths) to the current ownership table; `lifecycle_drift.yml`
    dropped its retired `complete.md` path filters (#81); `.pytest_cache/` gitignored;
    360 MB of untracked `tmp/` scratch removed locally.
- validation: PyAutoMind 154/154 tests; Brain `test_intake_dashboard.py` 20/20 (PR CI green
  on 3.12 + 3.13); `lifecycle.py check` OK with TOC blocks in place (parsers key on `## `
  and ignore the block); dashboard `--check` converges post-regeneration; Dashboard Refresh
  + Lifecycle Drift green on every push.
- key traps:
  - The dashboard header lives in the RENDERER (`PyAutoBrain/agents/conductors/intake/_intake.py`),
    not the page — hand-edits are reverted by the self-heal, and the Brain PR must merge
    before the Mind page is regenerated (dashboard_refresh checks against Brain main).
  - The spawn template contract lists registry files BY PATH (`scripts/spawn.py` MIND_RULES);
    any root-file move/delete must update manifest + `spawn_spec.md` + both spawn tests in
    lockstep or spawn fails UNMATCHED (by design).
  - Census follow-ups deliberately not fixed here, filed as drafts:
    `draft/refactor/pyautomind/repos_sync_check_dedup.md`,
    `draft/bug/pyautomind/status_sh_repos_missing_source.md`. The RED
    `registry_reconcile.yml` run (2026-08-19 06:23) was real drift that self-resolved —
    `lifecycle.py issues` OK by evening, no action.

## Original prompt

# PyAutoMind human-readability pass — census cleanup, dashboard/README rewrite, registry TOCs

Type: maintenance
Target: pyautomind
Repos:
- PyAutoMind
- PyAutoBrain
- PyAutoHeart
Difficulty: medium
Autonomy: supervised
Priority: high
Status: formalised

Original request (verbatim):

> Ok, lets do more work on making PyAutoMind human readable, clear an external viewer
> what it does and generally improve it. Firstly, Do a census of all code and work out
> if there are things which have not been used in a while and which could be removed,
> whether there are refactors to clear up existing souerce code. Note how many useful
> things one might want to read (dashboard.md, planned.md, ideas.md) are on the main
> repo but lumped against stuff like CODE_OF_CONDUCT.md, AI_POLICY.md. I think the core
> "mind" should be in an automind folder? Probably also the dashboard too. "automind"
> folder implies source code so maybe a different folder name? Happy for your opinion,
> but at the moment its hard to find. I want these files to be more readable, so for
> planned.md a contents at the top with all issues (which you can click to move to the
> issue in the file) would be good, same for similar files (but not dashboard, which
> already does something like this). Put this at the top of dashboard.md, "Reading on a
> phone? The one-tap copy version puts the command on your clipboard with a single tap
> of 📋.", then give the dshboard description, which is too long and has redundancy
> about the html atuff also remove this "Tasks only — the organism's health lives with
> the Heart (/health), not here.2!". Also remove this "Live on GitHub: open issues ·
> open pull requests", The opening trext on README.md is also a bit clunky so try to
> improve it -- one short paragraph like you have saying "PyAutoMind: The Mind of the
> PyAutoScientist ... " and then more human friendly literal description of how it
> works ("put tasks to develop your scientisit software ..."). Try and keep it to 4
> lines. Then have the follow up paragraph which starts "See this PyAutoMind Dashboard
> (dashboard.md / dashboard.html on mobile phone) for example of how PyAutoMind is used
> in practise, where tasks are .... [describe how tasks are listed, ready for claude
> implementaiton by a human]. I think the "What lives here:" here bit should have its
> own subheader "How PyAutoMind Works" and it should give a human friendly description
> of the process in a more sequential manner (e.g. use PyAutoBrain intake to take in a
> task which goes in draft, when ready to implement it with an AI you use a PyAutoBrain
> agent and the skill "start_dev" which makes it move to active. Then describe
> complete. Make it more of a step-by-step guide to give them the ideal including URLS
> to the existing folers on my repository to give them a better sense of how it works.

Scope agreed with the human (plan approved 2026-08-19; census evidence in the plan):

- Root declutter INSTEAD of a `mind/` folder move — active.md/planned.md are parsed by
  path from @PyAutoBrain, @PyAutoHeart, 3 workflows, ~30 skills and the spawn template
  contract, so the ledger stays at root; the clutter moves out.
- Census removals: delete stale `overview.md`; empty consumed `queue.md` (keep file);
  delete untracked `tmp/` scratch (360 MB) and `.pytest_cache/` (+ gitignore entry);
  drop the retired `complete.md` path filters from `lifecycle_drift.yml`; delete the
  four uncalled `scripts/health*.sh` forwarding shims after fixing the 3 PyAutoHeart
  usage comments that still name the Mind path; trim `skills/OWNERSHIP.md` dead paths;
  move `AI_POLICY.md` + `CONTRIBUTING.md` into `.github/` (spawn manifest, spawn_spec
  and spawn tests updated in lockstep).
- Dashboard header rewrite in the renderer
  @PyAutoBrain/agents/conductors/intake/_intake.py (phone line to top, shorter
  description, drop the "Tasks only …" and "Live on GitHub …" lines; mirror in the
  HTML twin; update renderer tests; Brain PR merges first, then the Mind dashboard is
  regenerated).
- New @PyAutoMind/scripts/registry_toc.py: self-healing clickable contents block at
  the top of `planned.md`, `parked.md`, `condemned.md`, wired into
  `dashboard_refresh.yml`; one new test.
- README.md rewrite: 4-line opening, dashboard-in-practice paragraph, and a
  step-by-step "How PyAutoMind works" section (capture → start → develop → complete)
  with GitHub folder URLs.

Follow-ups filed separately, NOT this task: registry_reconcile.yml RED triage;
status.sh --repos vestigial branch; repos_sync.py check/write_block dedup refactor.
