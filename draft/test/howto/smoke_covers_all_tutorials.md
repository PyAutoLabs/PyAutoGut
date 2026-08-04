# HowTo smoke: cover every tutorial (invert allowlist → no_run denylist)

Type: test
Target: howto
Repos:
- HowToGalaxy
- HowToLens
- HowToFit
Difficulty: medium
Autonomy: supervised
Priority: high
Status: formalised

## Original request (verbatim)

> I think its CI should check all tutorials: That coverage gap is arguably the
> more interesting finding: a public teaching notebook was broken in three
> places and its own repo's CI could never have caught any of them.

Raised 2026-08-04 immediately after shipping HowToGalaxy#57, which fixed three
stale-API breaks in `chapter_4_pixelizations/tutorial_3_inversions` — a file no
HowToGalaxy CI job has ever executed.

## Why the current design fails

`smoke_tests.txt` is an **allowlist**: a script is tested only if someone
remembers to add it. So every new tutorial is uncovered from birth, and the
file's own header defers chapters 2+ "once we've confirmed they run green" — a
deferral never revisited. Today's coverage:

| repo | covered | total |
|------|---------|-------|
| HowToGalaxy | 4 | 26 |
| HowToLens | 6 | 40 |
| HowToFit | 10 | 15 |

The only backstop is PyAutoHeart's `workspace-smoke`, which is **weekly**
(Mondays 03:00 UTC) — and the run that caught the #57 bug was a manual
`workflow_dispatch`, not the schedule. So a broken public tutorial can sit on
`main` for up to a week.

Worse, the allowlist **concealed a false claim**. `profile_smoke.yaml` sets
`PYAUTO_SMALL_DATASETS: "1"` for every script and its comment asserts "the
chapters run correctly at 16x16". That is untrue for chapter 4, and nobody knew
because chapter 4 was never in the list.

## Measured (2026-08-04, all scripts under each repo's own smoke profile)

| repo | result | wall time |
|------|--------|-----------|
| HowToGalaxy | 25/26 → **26/26** with the mesh fix below | 3.9 min |
| HowToLens | **39/40** (the 1 is already in `no_run.yaml`) | 6.4 min |
| HowToFit | **15/15** | 0.9 min |

Cost is not the blocker: HowToGalaxy currently spends ~2m18s on 4 scripts;
running all 26 costs 3.9 min. (Full-resolution was also measured — 26/26 in
8.8 min — and **rejected** by the human on 2026-08-04 in favour of keeping the
cap.)

## Work

### 1. HowToGalaxy mesh shape — do this first, it is urgent on its own

`scripts/chapter_4_pixelizations/tutorial_3_inversions.py:82` uses
`shape=dataset.shape_native`, coupling the pixelization mesh to image
resolution: 100×100 → 10000 mesh pixels at full res, but **256** under the cap.
The tutorial's `pix_indexes = [[445], [285], [313], [132], [11]]` (line 140)
then goes out of range → `IndexError`.

The indices are not the bug — they match the 625-pixel mesh of
`HowToLens/scripts/chapter_4_pixelizations/tutorial_3_inversions.py:102`
(`shape=(25, 25)`) they were copied from. HowToGalaxy's **own** line 176 already
uses `shape=(25, 25)`. Line 82 is the anomaly.

Fix: `shape=dataset.shape_native` → `shape=(25, 25)`. Verified: passes under the
smoke profile, and **19× faster** there (8.2s vs 156.7s).

**Urgency:** PyAutoHands' notebook runner resolves the same
`config/build/profile_smoke.yaml` (`run.py` → `find_profile`), so Heart's next
weekly run will fail this notebook with `IndexError` instead of the old
`TypeError`. #57 fixed the reported error; the job stays red without this.

### 2. Invert the runner to a denylist (all three repos)

`.github/scripts/run_smoke.py` is **byte-identical** across the three
(`md5 f105e0e8`). Change `load_smoke_scripts()` to discover
`scripts/**/*.py` (excluding `__init__.py`) and subtract `config/build/no_run.yaml`
using the canonical matcher `should_skip()` from
`PyAutoHands/autohands/build_util.py:147` — do **not** reimplement the matching.
Then retire `smoke_tests.txt`.

Reusing `no_run.yaml` is the point: PyAutoHands' notebook runner already honours
it, so script-smoke and notebook-smoke end up sharing **one** exclusion list with
the existing `SLOW` / `NEEDS_FIX` conventions, instead of an allowlist and a
denylist that can disagree.

Because the runner is triplicated, consider centralising it into PyAutoHands as
a follow-up so the next change lands once (deliberately **not** folded in here —
the human scoped this to the three repos).

### 3. Exclusion hygiene

- `tutorial_searches` is excluded in **both** HowToGalaxy and HowToLens with no
  stated reason, and **passes in both** (10.4s / 10.1s). Remove it.
- HowToLens `tutorial_5_borders` is recorded as "Cant get right masks, need
  proper update". Controlled re-test on the same dataset files: **fails with the
  cap, passes without it** (`IndexError: index 371 out of bounds for axis 0 with
  size 272`). The reason is incomplete — it is cap-induced. Keep the exclusion
  under the keep-the-cap decision, but correct the reason and tag it `NEEDS_FIX`
  so it stays visible.
- HowToFit has no `no_run.yaml` and needs none (15/15). The runner must handle
  an absent file by running everything.

### 4. Reconcile the docs contradiction (HowToGalaxy)

`AGENTS.md:34` claims `PYAUTO_SMALL_DATASETS` is "deliberately **not** used in
HowToGalaxy — tutorials assume the full-resolution simulated datasets", while
`profile_smoke.yaml:16` sets it for every script. Per the human's 2026-08-04
decision the cap stays, so **AGENTS.md is what is wrong** — correct it, and drop
the now-disproven "chapters run correctly at 16x16" assertion from the profile
comment.

## Verification

Prove coverage by the **executed-script count rising**, not by a green tick —
green already passes today while testing 4 of 26 files:

- HowToGalaxy 4 → 26, HowToLens 6 → 39, HowToFit 10 → 15
- Confirm the runner's printed total matches the discovered count minus
  `no_run.yaml`, so a mis-matching pattern cannot silently shrink the suite
- Add a tutorial file and confirm it is picked up with no list edit — that is the
  property being bought
- Four scripts pass in ~0.0s (`need_for_speed`, `slam`, `model_fit`,
  HowToFit `start_here`). Verified prose-only: 0 non-docstring statements each.
  Legitimate, not vacuous — but re-check if that count ever changes.

## Watch out

Running the suite locally re-simulates datasets under the cap
(`should_simulate` deletes + rewrites), so a later full-resolution run inherits
16×16 data and reports misleading sizes. Delete `dataset/` between profile
switches when comparing.
