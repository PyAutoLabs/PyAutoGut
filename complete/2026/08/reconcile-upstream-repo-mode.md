Leg 3 of the draft-staleness work: `intake reconcile --repo TARGET`, an opt-in
upstream read — the only signal that reaches a prompt with **no Mind-side trace
at all**.

- issue: PyAutoBrain#223 (closed completed)
- pr: PyAutoBrain#224, MERGED as `f518b24` (squash), 467+/12- across 6 files
- split-from: `draft/feature/pyautomind/draft_staleness_detection_signals.md` —
  legs 1-2 were DELIVERED 2026-08-09 (the `lifecycle.py` gate keys and the
  reconcile re-rank); this was the remaining leg, split out rather than
  re-opening a delivered prompt.

## Why the leg existed

The 2026-08-09 `draft/` sweep confirmed five stale prompts. Legs 1-2 read only
Mind-local evidence (`complete/` records + `active/`), which is structurally
blind to two of the five: one whose evidence sat inside a sibling **prompt**
rather than a record, and one whose fix shipped as PyAutoFit#1418 with no record
ever written. The parent prompt had already measured that re-ranking cannot
reach them — every attempt cost precision without gaining truth. Only reading
the target repo can.

## What shipped

`resolve_repo` (body map `github:` + the sizing faculty's existing
`repo_aliases` — no third mapping), `_clone_upstream` (cached `--depth 1`,
records the sha), `_grep_source`, and a `source_reader` seam on `reconcile()`.
New band `needs-review`; result dict gains `upstream` (slug/sha/date) and
per-suspect `upstream_score`.

## The trap this is built around — the reason for the whole design

`draft/bug/autofit/test_mode_bypass_ordered_assertion_ties.md` names five
identifiers — `FitException`, `check_assertions`, `ignore_assertions`,
`instance_for_arguments`, `instance_from_vector` — and **all five are on
PyAutoFit `main`**. The prompt is confirmed NOT shipped: main catches
`exc.FitException` in the TEST_MODE bypass, which looks exactly like the
requested fix, but the catch wraps only the likelihood call while
`model.instance_from_vector` (where `check_assertions` raises on an ordering
tie) sits on the line **before** the `try`.

So upstream hits deliberately do **not** feed `overlap_score`. They get their own
weaker band and ordering key, which makes it structurally impossible for any
number of upstream matches to reach a Mind-local verdict. Verified against
PyAutoFit `fbe9f45d`: the prompt lands in `needs-review` at `overlap_score 0.0`
— surfaced with its evidence, never called shipped.

**Presence of a name is not presence of the fix.** That sentence is the whole
design.

## Traps and findings

- **Noise filter — two named classes, not a spread threshold.** The first real
  run matched `TypeError` (37 files in PyAutoFit) and `autofit_workspace` (26):
  builtins and repo names. Filtering by upstream file-spread was tried and
  REJECTED — the counts do not separate, because `instance_from_vector` is a
  real signal at 22 files, just under `autofit_workspace` at 26. Any threshold
  dropping the noise also drops one of the trap's own identifiers.
- **Treeless clone is a false economy here.** The parent prompt suggested
  `--depth 1 --filter=blob:none`. This leg greps source, so a treeless clone
  refetches every blob on demand. Plain `--depth 1` with
  `GIT_LFS_SKIP_SMUDGE=1`; ~3.6s warm against PyAutoFit.
- **Multi-repo targets are refused, not guessed.** `workspaces` (23 prompts
  across four work-types), `health_fixes`, `priors`, `graphical_ep` are topic
  clusters and among the largest buckets in `draft/`. `--repo` exits 5 naming
  the real candidates; guessing would be confidently wrong at scale.
- **First network access in PyAutoBrain.** Nothing under `agents/` previously
  used `urllib`, `requests`, `gh` or `git clone`. Strictly opt-in;
  `test_default_path_makes_no_network_access` monkeypatches both
  `socket.socket` and `subprocess.run` to detonate if that changes.
  `AUTONOMY.md` records the surface and that widening it is a new decision.
- **Regression caught by auditing the branch against `main` before merge.**
  Widening the band column to fit `needs-review` had changed the DEFAULT path's
  printed output too — six extra columns of indent on runs that can never emit
  that band. The suspects were unaffected (verified identical against main, 29
  of 135, no result keys removed), but the text a human reads had shifted for
  unrelated work. Fixed in `c7c8b17`: width follows the widest band actually
  present. Default output now diffs byte-identical to main.

## Process findings from this task (all three since fixed — see
## dev-workflow-helpers-laptop-paths)

- The `worktree_check_conflict` run recorded at start_dev time was **vacuous** —
  the guard read no file and returned 0. That is what motivated PyAutoBrain#225.
- The `ship_library` fallback gate went RED on two pre-existing
  `test_skill_install.py` failures unrelated to this diff; a human acknowledged
  and authorised the PR, and CI then went green on both legs, vindicating the
  call.
- `prompt_sync_push` was NOT used for this task's Mind writes: it hardcoded
  `git push origin main`, which would have violated the session's branch scope.

## GitHub markdown trap (cost two rewrites)

Both the issue and the PR were created with `<target>` in the title and body.
GitHub parsed those as unknown HTML tags and **silently deleted them**, taking
the `<details>` collapsibles with them — issue #223's title became
`--repo  —` with a hole in it. Use `TARGET` or backticked prose placeholders in
any issue/PR body written through the API.

## Verification

8 new tests, all hermetic via the injected `source_reader` — nothing under
`tests/` clones. PyAutoBrain `main` after merge: **339 passed**. Smoke-tested
from merged main: default path `29 suspect(s) of 135 scanned` with original
column widths; upstream mode reads PyAutoFit `fbe9f45d` and puts the trap in
`needs-review`.

## Follow-up left open

The parent prompt's `## Scope` / `## Acceptance` section-scoping idea was NOT
adopted: the trap prompt has neither heading, so a strictly section-scoped
extraction no-ops on exactly the prompts that matter most. Identifiers are taken
from the whole prompt body, minus the noise classes above. Revisit only with a
stated fallback.

## Original prompt

# `intake reconcile --repo <target>` — read the target repo, the only route to the findings the Mind cannot see

Type: feature
Target: PyAutoBrain
Repos:
- PyAutoBrain
- PyAutoMind
Difficulty: medium
Autonomy: supervised
Priority: high
Status: planned

Leg 3 of `draft/feature/pyautomind/draft_staleness_detection_signals.md`, split
out because that prompt's legs 1 and 2 are **delivered** and one prompt is one
task is one PR. Read the parent for the labelled set and the measurement; this
file is the remaining leg only. Do not re-open the parent.

## Why this leg exists, and why it cannot be skipped

The parent's § Hard limit is the argument. Of the five confirmed findings from
the 2026-08-09 `draft/` sweep, **two left no Mind-local evidence at all**:

- `rectangular_adapt_constant_split_guard` — its evidence sat inside a sibling
  *prompt*, not a completion record, so nothing that reads `complete/` could
  reach it.
- `latent_samples_none_on_resumed_fit` — PyAutoFit#1418 fixed it the same day it
  was filed and **no completion record was written**. There was nothing in the
  Mind to cross-reference. (A record exists now — `complete/2026/07/
  latent-samples-none-on-resumed-fit.md` — but only because a human did the
  upstream read by hand. That is precisely the work this leg mechanises, and the
  next such fix will land with no record again.)

The parent proved that no amount of re-ranking Mind-local signals reaches these:
every attempt cost precision without gaining truth. The upstream read is
load-bearing. This leg is that read.

Current state to build on: `intake reconcile` flags **29 suspects of 135
scanned** (7 `high`, 22 `medium`) — the post-re-rank numbers holding. The
ranking is not the problem any more; the missing evidence source is.

## Scope

Add an opt-in upstream mode to
`@PyAutoBrain/agents/conductors/intake/_intake.py`:

```
pyauto-brain intake reconcile --repo <target> [prefix]
```

It resolves the target to a GitHub slug, makes a cached shallow clone of that
repo's `main`, extracts the backticked identifiers each prompt names, greps the
clone, and ranks on hits — reporting `file:line` evidence a human can read.

### Target resolution

`repos.yaml` in @PyAutoMind carries the `github:` slug for every repo, and
`@PyAutoBrain/config/policy.yaml` already carries `repo_aliases`
(`pyautoarray -> autoarray`, and the sizing faculty's `PyAutoFit -> autofit`
package form). Reuse both — do not add a third mapping.

**Multi-repo pseudo-targets must be refused, not guessed.** `workspaces`,
`health_fixes`, `priors`, `graphical_ep` are not repos, and they are among the
*largest* buckets in `draft/` (`workspaces` alone spans 22 prompts across four
work-types). `--repo workspaces` must exit non-zero naming the real candidate
repos. Silently picking one would produce confident nonsense on the biggest
part of the backlog.

### Clone mechanics

Plain `--depth 1` with `GIT_LFS_SKIP_SMUDGE=1`, cached per-repo and re-fetched
on later runs. Record the resolved sha in the output so a verdict is
reproducible and re-checkable.

**Correction to the parent prompt:** it suggests `--depth 1 --filter=blob:none`.
Treeless is wrong here — grepping source refetches every blob on demand, so it
is a false economy. Use a plain shallow clone.

### The signal

Extract backticked `snake_case` / `CamelCase` identifiers from the prompt and
grep the clone for them. `_IDENT_RE` in `_intake.py` already does exactly this
extraction for the Mind-local leg; reuse it rather than writing a second regex.

The parent proposes scoping extraction to the prompt's `## Scope` /
`## Acceptance` sections, to catch "identifiers the prompt says do not exist
yet". That rule needs a stated fallback: **the trap prompt below has neither
heading** — its only heading is a dated correction block — so a strictly
section-scoped rule no-ops on exactly the prompts that matter most.

## The trap — verified, and the acceptance criterion turns on it

`draft/bug/autofit/test_mode_bypass_ordered_assertion_ties.md` names five
identifiers: `FitException`, `check_assertions`, `ignore_assertions`,
`instance_for_arguments`, `instance_from_vector`. **All five are on PyAutoFit
`main`.** The prompt is confirmed **NOT** shipped: `main` catches
`exc.FitException` in the TEST_MODE bypass, which looks exactly like the
requested fix, but the catch wraps only the likelihood call while
`model.instance_from_vector` — where `check_assertions` actually raises on an
ordering tie — sits on the line *before* the `try`.

A naive identifier-presence matcher scores this 5 of 5 and calls it shipped. It
would be wrong, and it is the single mis-grade this tool must never make.

So: **the mode reports `needs-review` with evidence, never a `shipped`
verdict.** It ranks for a human and retires nothing — which is already
reconcile's stated contract (`retiring a prompt stays human`). Keep it.

## Architectural constraint — this is the Brain's first network access

Nothing under `@PyAutoBrain/agents/` currently uses `urllib`, `requests`, `gh`
or `git clone`. Every conductor and faculty is stdlib-only and offline. This
leg breaks that invariant, so:

- the flag is **strictly opt-in**; the default `reconcile` path stays byte-for-
  byte offline and read-only;
- the upstream read sits behind an **injectable seam** (a source-reader
  callable), so `@PyAutoBrain/tests/test_intake_reconcile_ranking.py` stays
  hermetic — every fixture there is a fictional Mind tree in `tmp_path`, and
  that property is worth more than integration coverage;
- one opt-in network integration test, gated on an env var, covers the real
  clone path;
- `@PyAutoBrain/AUTONOMY.md` gets a line stating the network surface and that it
  is opt-in.

## Acceptance

- `--repo <target>` resolves via `repos.yaml` + `policy.yaml` `repo_aliases`,
  and **refuses** `workspaces` / `health_fixes` / `priors` / `graphical_ep`
  non-zero, naming the real repos.
- Run against PyAutoFit, `draft/bug/autofit/test_mode_bypass_ordered_assertion_ties.md`
  is **NOT** reported as shipped, despite all five of its identifiers being
  present upstream. Pinned by a test.
- No prompt is moved or retired by the tool. Pinned by a test (the parent
  already asserts this for the Mind-local legs).
- The default `reconcile` path performs **no** network access. Pinned by a test.
- The existing hermetic tests still pass unchanged.
- Output records the resolved upstream sha.

<!-- split 2026-08-10 from draft/feature/pyautomind/draft_staleness_detection_signals.md
     (legs 1-2 DELIVERED 2026-08-09; this is leg 3, which that prompt's own
     delivery note re-motivates as "the only route to the last two findings").
     Baselines verified at split time: reconcile 29/135 flagged, 7 high;
     no --repo flag in _intake.py argparse; no network access anywhere under
     PyAutoBrain/agents/. -->
