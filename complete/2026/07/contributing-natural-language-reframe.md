# PyAutoScientist CONTRIBUTING + README — natural-language-first reframe

Type: docs
Target: PyAutoScientist
Repos:
- PyAutoScientist
- .github
- PyAutoMind
Difficulty: medium
Autonomy: human-required
Priority: high
Status: shipped

## Intent (original request, condensed)

Drop the "AI-first development workflow" framing from `PyAutoScientist/CONTRIBUTING.md`
in favour of a "fully natural-language, agentic-AI development ecosystem" — natural
language emphasised first, AI secondary — matching the register of the
PyAutoLens-Assistant paper's "Natural-language development ecosystem" section.
`README.md` to use the same framing. CONTRIBUTING.md should explain PyAutoScientist
and all the organs, and recommend contribution routes: (1) GitHub issue on the
relevant repo, picked up by James Nightingale via the Ears of PyAutoBrain and
implemented by the feature agent; (2) run the ecosystem locally for those
comfortable with agentic AI development, noting it is not yet set up for others;
(3) a "Contributing Without AI" section that still accepts traditional PRs but
notes an AI does the first review pass. Key point: written too brazenly, readers
will conclude there is too much AI to be trustworthy — so a testing section goes
high up, pointing at `autolens_workspace_test` and the other test workspaces, and
making clear that all of `autolens_workspace` is run as tests.

## What shipped

Both files were rewritten. The final text was **authored by the maintainer** and
applied verbatim (`8749d66`), superseding a first draft written in-session
(`ebf28c0`) — both commits are on the squashed PR.

- **PyAutoScientist PR #10** (squashed `6e8eb7d`) — `CONTRIBUTING.md` and `README.md`.
- **.github PR #6** (squashed `5e0a59b`) — org profile organ table regenerated.
- **PyAutoMind `59afba2`** — the seven organ `public_role` values reworded.

## The load-bearing finding: the organ table is generated, and it is a three-file move

The organ table in `PyAutoScientist/README.md` sits between the
`<!-- repos_sync:organs:begin/end -->` markers and is **generated** from the
`public_role` field of each `category: organ` entry in `PyAutoMind/repos.yaml`
(`organ_public_table()` in `scripts/repos_sync.py`, `public_role` falling back to
the terse `role`). Hand-editing it inside the markers fails
`repos_sync.py --check` ("public front-door organ tables (generated)") and is
silently overwritten by the next `--write`.

**`PUBLIC_TABLE_TARGETS` has two entries** — `.github/profile/README.md` (bold-link
style, the public GitHub organisation landing page) and `PyAutoScientist/README.md`
(plain-link style). They render the *same* generated content. So any change to
organ role copy is necessarily a **three-file move**: `repos.yaml` → both front
doors. Ship them out of step and `repos_sync --check` reports front-door drift.

Merge order used: `repos.yaml` to `main` → `.github` #6 → PyAutoScientist #10.
Verified `public front-door organ tables (generated): OK` after all three landed.

## Trap: `repos_sync.py --write` targets the main checkout, not the worktree

`PUBLIC_TABLE_TARGETS` paths resolve from the workspace root, so running
`--write` while developing in `~/Code/PyAutoLabs-wt/<task>/` writes the
regenerated table into `PyAutoLabs/PyAutoScientist/README.md` (on `main`, clean)
and leaves the worktree copy untouched. It also appends a trailing newline to
`CONTRIBUTING.md` in passing. Recovery used here: capture the generated marker
block from the main checkout, `git checkout --` to revert it, then splice the
block into the worktree file. Anyone regenerating a front-door table from a
worktree must expect this.

## Verified claims (measured, for any future reuse of the numbers)

The first draft's testing section quoted figures measured directly rather than
carried over from docs. The maintainer's final text states these qualitatively
instead, but the measurements stand:

- `PyAutoHands/autohands/config/workspaces.yaml` `run_all:` runs every
  `scripts/**/*.py` in ten repos: autolens_workspace 373, autogalaxy_workspace
  172, autofit_workspace 40, autolens_workspace_test 146, autofit_workspace_test
  63, autogalaxy_workspace_test 61, HowToLens 47, HowToGalaxy 33, HowToFit 21,
  euclid_strong_lens_modeling_pipeline 6 — ~960 scripts, reports under
  `PyAutoHands/run_logs/`.
- Unit test *functions* (more meaningful than file counts): PyAutoFit 1,261,
  PyAutoGalaxy 985, PyAutoArray 844, PyAutoLens 471, PyAutoCTI 271,
  PyAutoNerves 135 — ~3,900 total.
- Per-PR gate is the curated `smoke_tests.txt` subset via the reusable
  `PyAutoHeart/.github/workflows/smoke-tests.yml@main` workflow.
- `config/build/no_run.yaml` exists in the workspaces and its header documents
  the per-entry inline `#` reason comments the guide describes.

## Process notes

- Heart was **YELLOW** at ship time; the human acknowledged the exact reason set
  (workspace validation not passing, 13 failed 2026-07-21T19-05-22Z; 33 stale
  parked scripts; tenant-firewall manifest drift, 6 mismatches). All pre-existing
  and unrelated to PyAutoScientist, which has no scripts and is not in the
  validation matrix.
- A concurrent session was writing to PyAutoMind throughout (new draft prompts,
  an edit to `active/multistart_prodigy_in_start_here.md`). All Mind commits here
  staged **explicit paths only** — `prompt_sync_push`'s `git add -A` would have
  swept the other session's staged work.
- `PyAutoScientist` carries no CI workflows, so there were no PR checks to await.
- `.github` was 4 commits behind at branch time; stash → `pull --ff-only` →
  branch → `stash pop` applied cleanly.

## Original prompt

# PyAutoScientist CONTRIBUTING.md + README.md — natural-language-first reframe

Repo: @PyAutoScientist
Work type: docs
Difficulty: medium
Priority: high

## Original request (verbatim)

- Need to update CONTRIBUTING.md on PyAutoScientist with the following:

No longer "AI-first development workflow" but instead "fully natural-language, agentic-AI development ecosystem ",
with the emphasis on it using natural language and AI secondary in the emphasis.

The PyAutoScientist README.md should use the same natural language first framing, which I dont think it quite got there yet.

Here is how the PyautoLens-Assistant paper describes it, whcih is the tone I am going for:

# Natural-language development ecosystem

In March 2026, following more than a decade of exclusively human-led software development, `PyAutoLens` transitioned
to a fully natural-language, agentic-AI development ecosystem called
[`PyAutoScientist`](https://github.com/PyAutoLabs/PyAutoScientist). The ecosystem is organised as a software organism
whose core repositories mirror the roles of human organs:
[`PyAutoBrain`](https://github.com/PyAutoLabs/PyAutoBrain) acts as the reasoning centre, classifying, planning, and
routing tasks through specialist coding agents; [`PyAutoMind`](https://github.com/PyAutoLabs/PyAutoMind) captures
intent by recording plain-English development requirements and tracking them from initial ideas to completed
implementations; and [`PyAutoMemory`](https://github.com/PyAutoLabs/PyAutoMemory) provides long-term scientific memory
through cross-linked literature wikis and verifiable citations. Humans can therefore conduct software development
entirely through natural language.

The CONTRIBUTING.md file should explain PyAutoScientist and all the organs.

So, how do I recommend people contribute now? I guess they have the following options:

1) Submit a github issue on the repo their task is relevent too, and it will then be picked up by me (James Nightingale)
via the ears of PyAutoBrain, where we will discuss the feature before having the PyAutoBrain feature agent implement it.

2) For those comfortable with agentic AI development, they could try and setup themselves with the PyAutoScientist
ecosystem locally and contribute directly, at which point I'll just review PRs. Note however the ecosystem is not yet
really set up for others to use but I am working on it. If you want to do this, maybe reach out to me directly
so we can do the setup togerther.

What is expected of human submissions?

Paired with AI policy, but rule of thumbs are

3) ## Contributing Without AI, this section says we still accept traditional but also mention an AI will pick up the PR rathert han a human lookina t it directly.

KEY POINT: If written to brazenly people will look at this and think theres too much aI and its not trustworth.
So add a secftion high up on testing, pointing out the autolens_Workspace_test (and other test workspaces) and make it
clear that there is significant testing infrastrature to ensure new code doesnt break existing functionality. ALso explain
that all of autolens_workspace is run as tests.

## Scope

Two files, one repo (`PyAutoScientist`): `CONTRIBUTING.md` (substantial rewrite)
and `README.md` (reframe of the header/positioning prose only — the organ table
is generated from `PyAutoMind/repos.yaml` and must not be hand-edited).

## Verified grounding for the testing section

Confirmed against the live system before drafting:

- `PyAutoHands/autohands/config/workspaces.yaml` `run_all:` matrix runs **every**
  `scripts/**/*.py` in 10 repos: `autofit_workspace` (40), `autogalaxy_workspace`
  (172), `autolens_workspace` (373), `autofit_workspace_test` (63),
  `autogalaxy_workspace_test` (61), `autolens_workspace_test` (146), `HowToFit`
  (21), `HowToGalaxy` (33), `HowToLens` (47),
  `euclid_strong_lens_modeling_pipeline` (6) — ~960 scripts, run as part of
  release validation via `autohands run_all`, reports under
  `PyAutoHands/run_logs/`.
- Per-PR gate is the **curated** `smoke_tests.txt` subset in each workspace,
  run by the reusable `PyAutoHeart/.github/workflows/smoke-tests.yml@main`
  workflow (thin callers in each workspace declare their dependency chain).
- Library unit suites: PyAutoFit (190 test files), PyAutoArray (115),
  PyAutoGalaxy (113), PyAutoLens (76), PyAutoCTI (70), PyAutoNerves (19).
- `PyAutoHeart` owns the authoritative GREEN/YELLOW/RED "is it safe to release?"
  verdict; release is gated on it.

Do not invent numbers beyond these; re-verify if the draft needs others.

## Constraints

- Natural language leads; agentic AI is the mechanism, mentioned second.
- Match the tone of the PyAutoLens-Assistant paper excerpt above.
- Testing section goes **high up** in CONTRIBUTING.md, before the contribution
  routes, to answer the "too much AI to be trustworthy" reaction with evidence.
- Do not hand-edit the `repos_sync:organs` table in `README.md`.
- Cross-link `AI_POLICY.md` rather than duplicating its content.
