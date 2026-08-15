# Has the falsified-by checkpoint stage gone rote after ten ships

Type: research
Target: PyAutoBrain
Repos:
- PyAutoBrain
Difficulty: small
Autonomy: safe
Priority: normal
Status: formalised

## What this is

The efficacy review that `docs/agent_failure_modes.md` §9 committed to when
mitigation 6 shipped: *"trial on the next ship series, review whether it went
rote after ~10 ships."* Spun out of PyAutoBrain#130 when that issue was closed
(2026-08-15) — it was the one §9 item still genuinely open, and nothing tracked
it.

This is an investigation producing a written verdict from evidence. No code
change is committed up front; a fix may follow from the finding.

## Background

Mitigation 6 (PyAutoBrain#140, merged 2026-07-17, live) made the review faculty
lift **load-bearing empirical claims** out of a branch's commit messages into
the `ReviewSurface` as `claims to falsify` — the trigger vocabulary is `no-op`,
`byte-identical`, `does-not-affect`, `proven`, `behaviour-preserving`. `AGENTS.md`
step 2a then makes an unsupported one a FINDING of kind `unverified-claim`.

Its design was deliberately reader-enforced rather than an author checklist, and
scoped to load-bearing phrasing only, precisely so it could not decay into the
"remember-to-run checklist" the campaign's own constraints ban. It targets the
A5/F3 failure class — confident-wrong effect-claims.

## Why it needs reviewing

The doc's constraint list bans checklists as a mechanism, and a routine
adversarial pass is the single mechanism most likely to decay into one. The
worry is explicit in the shipping comment: *"the one that needs care not to
become the banned checklist."* A stage that fires on every ship and is waved
through every time is worse than no stage, because it also carries false
assurance.

## What to investigate

Over the real ship history since 2026-07-17:

1. **Firing rate** — on how many ships did `claims to falsify` populate at all,
   versus come back empty? An always-empty surface means the vocabulary is too
   narrow; an always-full one means it is too broad.
2. **Finding rate** — how many `unverified-claim` FINDINGS were actually raised,
   and what happened to each? A stage that never produces a finding across ~10
   ships is either unnecessary or being rubber-stamped; distinguish those two.
3. **Were any load-bearing?** For each finding, did falsifying the claim change
   the outcome — a correction, a held ship — or was it cosmetic? This is the
   measure of whether the stage is earning its per-ship cost.
4. **Idle-phrasing exclusion** — is the load-bearing-only scoping holding, or has
   the matcher started lifting incidental prose? Check for false positives of
   the kind that trained bypass-by-default in the guard's first hour (the F5
   cost column).
5. **Rubber-stamping** — look for the signature: claims lifted, reviewed CLEAN,
   no evidence cited in the review. That is the rote failure, and it looks
   identical to a healthy pass unless you read what the reviewer actually did.

## Deliverable

A verdict with the numbers behind it, and one of: keep as-is, narrow/broaden the
trigger vocabulary, or retire the stage. If the finding is "it went rote", say
what would fire instead — per the campaign's own ranking, deleting the
possibility beats detecting it, and detecting beats reminding.

## Method note

Validate the instrument before trusting it: check that the review faculty's
claim-lifting still runs on a branch with known load-bearing claims before
concluding anything from a low firing rate. A null result that looks like a
finding (D1) is the exact failure this campaign catalogued.

<!-- formalised by the Intake (Conception) Agent on 2026-08-15 from user-intake -->
