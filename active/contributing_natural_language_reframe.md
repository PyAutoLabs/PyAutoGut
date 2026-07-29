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
