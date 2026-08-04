# The hygiene tidy pre-scan reports 0 [gone] refs unconditionally, and scans only 9 of ~28 repos

Type: bug
Target: PyAutoBrain
Repos:
- PyAutoBrain
Difficulty: small
Autonomy: supervised
Priority: normal
Status: formalised

Found during a `/repo_cleanup` sweep on 2026-08-04. `hygiene tidy` reported
"12 stale branches across 9 repos, 0 stashes, 0 [gone] refs, 0 dirty checkouts".
The real state at that moment was 91 branches across 28 repos, 4 stashes,
dozens of [gone] refs and 3 dirty checkouts.

Two independent defects produce that gap.

## Defect 1 — the `[gone]` counter can never be non-zero

`agents/conductors/hygiene/hygiene.sh:129`:

    g=$(git -C "$dir" branch -vv 2>/dev/null | grep -c '\[gone\]' || true)

`git branch -vv` prints the upstream as `[origin/<branch>: gone]`, never the
bare `[gone]`. The pattern matches nothing, in every repo, always. Proof on
PyAutoHands, which had three at the time:

    git branch -vv | grep -c '\[gone\]'                        -> 0
    for-each-ref --format='%(upstream:track)' refs/heads       -> [gone] x3

`prescan_tidy` then folds `gone` into the `total` at line 133-134, so the
conductor's prioritisable count for `tidy` is systematically understated and
`tidy` under-ranks itself against the other hygiene modes.

Fix: count via `for-each-ref '%(upstream:track)'` (already the idiom used in
`repo_cleanup`'s own audit), or match `: gone]`.

Note `enumerate_condemn_candidates` at line 419 does NOT share this bug — it
uses `for-each-ref` correctly.

## Defect 2 — the scan covers 9 repos, not the organism

`prescan_tidy` (line 121) iterates `LIB_REPOS` + `ORG_REPOS` only:

    LIB_REPOS=(PyAutoNerves PyAutoFit PyAutoArray PyAutoGalaxy PyAutoLens)
    ORG_REPOS=(PyAutoBrain PyAutoHands PyAutoHeart PyAutoMind)

That is the "9 repos" in the summary line. Invisible to it: PyAutoCTI,
PyAutoReduce, PyAutoMemory, PyAutoGut, PyAutoScientist, every workspace, every
HowTo, every assistant, autolens_profiling, admin_jammy. Both the "0 stashes"
and "0 dirty checkouts" figures were scope artifacts, not detector bugs — all 4
stashes and all 3 dirty trees lived in repos it never looks at.

Decide whether the fix is to derive the repo set from `PyAutoMind/repos.yaml`
(the body map) rather than re-listing it, which is the same hard-coding problem
`_hygiene_extras.py` was just refactored to remove in PR #193. `run_tidy` /
`enumerate_condemn_candidates` share the same two lists and the same limitation.

## Why it matters

`hygiene tidy` is the advertised front door for git debris and the thing a
human reads before deciding whether a cleanup is worth running. Under-reporting
by roughly an order of magnitude makes it read as "nothing much to do" when
there is. A wrong-but-quiet number is worse than no number.

## Control

Before the fix, `prescan_tidy` must reproduce `0 [gone] refs` on a checkout
known to have some (any repo with a merged-and-deleted upstream). After, the
count must be non-zero on that same tree and match
`for-each-ref | grep -c '\[gone\]'`. A green run on a tree with zero [gone] refs
proves nothing — pick the tree first.

<!-- raised from a /repo_cleanup sweep, 2026-08-04 -->
