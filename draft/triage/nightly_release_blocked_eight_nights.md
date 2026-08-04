# Nightly release has been blocked 8 nights running — triage the streak

Type: triage
Target: pyautobrain
Repos:
- @PyAutoBrain
- @PyAutoHeart
- @PyAutoHands
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: draft

Surfaced 2026-08-04 while listing PyAutoBrain workflow runs during the
PR-test-CI ship (#195). Not a PyAutoBrain CI problem — filed here because the
driver lives in Brain.

## First finding: the red is a SIGNAL, not a broken workflow

`agents/conductors/release/nightly.sh` exits **2** when it stops
("🚨 nightly release stopped … No release was made"), so a night where the
driver *correctly* refused to release renders as a red workflow run. Every one
of these failures is the gate doing its job. That is also why nobody was
watching it: a channel that is red whenever it works properly trains its
audience to ignore it. Whether "blocked" should render as a neutral conclusion
(or a distinct notification) rather than `failure` is the first design question
this task should answer.

## Second finding: 8 consecutive blocked nights, two distinct classes

Runs 23–30, 2026-07-28 → 2026-08-04 (run 22 on 07-27 was the last success):

**Class A — stopped at step 4b, Stage 3 release-fidelity integration (6 nights).**
A single script fails the `mode=release` leg and the night stops. The script
*rotates*, which is the interesting part:

- 2026-08-04 — `autolens database/start_here.py`
- 2026-08-03 — `autofit_test graphical/ep.py`
- 2026-08-01, 07-31, 07-30, 07-28 — no script named in the summary line

**Class B — passed the readiness gate, then the LIVE release failed (2 nights).**
These are the serious ones: the gate said GREEN, step 6 dispatched a real
release, and the release run failed.

- 2026-08-02 → release 2026.8.2.1 → PyAutoHands run 30736527569 failed in
  `release_test_pypi (3.12, PyAutoLabs/PyAutoFit, main, PyAutoFit)` at step 9,
  **Tests**.
- 2026-07-29 → release 2026.7.29.1 → PyAutoHands run 30428406874 failed (no
  failing job resolvable via the API now).

A gate that passes and is then contradicted by the release run is worth more
attention than the Class A blocks: either the gate's evidence is stale relative
to what `release.yml` actually runs, or the two disagree about what "the
libraries pass" means.

## Third finding: a reporting bug in the stop summary

The 2026-08-04 line reads:

```
1 failed: autolens database/start_here.py, None verify_install
```

The count says **1** but two items are listed, and the second carries a literal
`None` where a script name belongs (the `verify_install` leg has no script). So
the summary formatter mis-counts and stringifies a null. Small, self-contained,
and it makes the nightly notification harder to read at exactly the moment it
matters.

## Suggested scope

1. Decide the exit-code / conclusion contract for "correctly blocked" vs
   "driver broke" — they should not both be red.
2. Fix the stop-summary count + `None` script name.
3. Triage the Class A rotating script failures (are they the same underlying
   env/profile issue, or genuinely different scripts each night?) and the
   Class B gate-vs-release disagreement. Related open work:
   PyAutoHands#161 (env-profile + validation-gate redesign),
   PyAutoHands#127 (nightly live releases behind an activity gate).

Do NOT convert this into a manual release drive — `AUTONOMY.md` forbids
converting a manual release into the scheduled-nightly exception, and
`active.md`'s `release-drive` entry records that a human drives releases via
`pyauto-brain release validate`.
