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
