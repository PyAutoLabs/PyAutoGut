## interferometer-subhalo-to-advanced
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/392 (CLOSED)
- completed: 2026-07-30
- workspace-pr: https://github.com/PyAutoLabs/autolens_workspace/pull/395 (MERGED `b3e31844`)
- summary: Moved `scripts/interferometer/features/subhalo/` -> `features/advanced/subhalo/` (6 files, `git mv`, 0-line renames), matching the imaging twin. Dropped the now-false `- subhalo:` bullet from `interferometer/features/README.md` and authored the missing `interferometer/features/advanced/README.md`. Scripts are location-independent (all dataset/output paths are workspace-root-relative), so zero content change. CI green on all 8 rows (navigator paths+banner+catalogue-staleness, smoke 3.12+3.13, push+pull_request).
- FINDING-extension-filtered-grep-missed-a-real-ref: the pre-plan sweep used `--include="*.py" --include="*.md"` ... and MISSED `.navigator_check_ignore` -- a DOTFILE no `*.ext` glob matches, holding a literal path to the moved script. Only an unrestricted grep found it. CONTROL-TESTED via `check_navigator --ignore-file`: stale entry -> "Banner lint: 1 banner-style comment(s)" (CI FAILS); re-pointed -> "OK". Load-bearing because `sensitivity/start_here.py` ships FULLY COMMENTED OUT, so its `===` docstring underline reads as a `#`-banner. Entries match LITERALLY, so a stale one never errors -- it silently stops matching
- base-drift: worktree cut at `f5d03984`; #391 merged mid-task -> `9b274ff2`. Pre-merged origin/main BEFORE regenerating, so the catalogue was rebuilt on top of #391's entries instead of reverting them
- script-sizes-decision: `check_sizes.sh --update` rewrites 138/129 lines because `.script_sizes.json` is ALREADY stale repo-wide (cluster/, group/, double_einstein_ring...). Refused to bake unrelated drift into a folder-move PR; re-keyed ONLY the 6 moved entries via script. Sizes byte-identical before/after -- independent proof of a pure move
- brain-override: Brain scored large/9 + split-into-phases with a "public-API change may ripple downstream" risk -- VACUOUS, zero library code touched. Same repo-count-proxy misfire as `potential-correction-start-here` (too-large/12). Overridden to ONE phase; shipped in one
- heart-ack: human-acknowledged YELLOW (score 70, no RED) -- workspace validation not passing (0 failed, cloud#30516167217); manifest drift tenant firewall (2 mismatches); [stale] release validation stale
- parallel-claim: shipped alongside 4 concurrent autolens_workspace claims (#385/#387/#389/#390); footprints hand-checked disjoint. #389 touches `interferometer/features/advanced/potential_correction/start_here.py` -- a different file in this task's DESTINATION parent; git tracks files not directories, so the `git mv` never touched it
- no-smoke-coverage: `smoke_tests.txt` has NO interferometer subhalo entry, so the curated set never exercises these scripts. Proof was instead navigator catalogue-staleness + a real `simulator.py` run (exit 0, 7 outputs)
- follow-ups: (1) `.script_sizes.json` stale repo-wide -- deliberate reviewed refresh deserves its own task; (2) `check_sizes.sh` IGNORES stale keys silently and still exits 0, so a moved script loses truncation protection with no warning; (3) `interferometer/features/README.md` omits real folders `datacube`, `linear_light_profiles`, `multi_gaussian_expansion`; (4) interferometer subhalo has no per-folder READMEs while imaging has three; (5) `sensitivity/start_here.py` is entirely commented out

## Original prompt

# Move `interferometer/features/subhalo` into `features/advanced`

**Work type:** docs (workspace restructuring)
**Target:** @autolens_workspace
**Autonomy:** supervised

## Original request (verbatim)

> move interferometer/features/subhalo to its advanced folder

## Why

`autolens_workspace` already treats subhalo detection/sensitivity mapping as an
**advanced** feature in the imaging regime:

```
scripts/imaging/features/advanced/subhalo/{detect,sensitivity,simulator.py}
```

The interferometer regime is out of step — it keeps `subhalo/` as a top-level
`features/` folder, alongside a sibling `features/advanced/` that already holds
`shapelets/` and `potential_correction/`. Aligning the two regimes is the same
kind of placement correction that `potential-correction-start-here` (#389) is
applying in the other direction (imaging catching up to the interferometer twin).

## Scope

Move, in `autolens_workspace`:

- `scripts/interferometer/features/subhalo/` → `scripts/interferometer/features/advanced/subhalo/`
- `notebooks/interferometer/features/subhalo/` → `notebooks/interferometer/features/advanced/subhalo/`

Contents moved (6 script files, 3 notebooks):

```
__init__.py
simulator.py
detect/{__init__.py,start_here.py}
sensitivity/{__init__.py,start_here.py}
```

Then update `scripts/interferometer/features/README.md`, which currently lists
`subhalo` as a top-level folder, and regenerate the catalogue artifacts.

## Findings from pre-plan exploration

- **No hand-written cross-references exist.** Every occurrence of
  `interferometer/features/subhalo` in the repo is in a *generated* artifact:
  `llms-full.txt` (3), `workspace_index.json` (3), `.script_sizes.json` (6).
  These are regenerated, never hand-edited.
- **The scripts are location-independent.** All dataset/output paths are
  workspace-root-relative (`Path("dataset") / "interferometer" / dataset_name`),
  so no in-script path string changes.
- **No build-config entry references the interferometer subhalo scripts.**
  `config/build/no_run.yaml:41` excludes only the *imaging* twin
  (`imaging/features/advanced/subhalo/sensitivity/`); `profile_release.yaml`
  has no subhalo pattern. Confirm no config edit is needed — do not assume.
- **`scripts/interferometer/features/advanced/` has no `README.md`**, unlike
  `scripts/imaging/features/advanced/README.md` which lists its subfolders
  (including `subhalo`). After the move the folder would be undocumented.
- **`sensitivity/start_here.py` is entirely commented out** (every line, including
  the docstring, is `#`-prefixed) — a disabled placeholder. Pre-existing state;
  out of scope, but note it so the move is not mistaken for breaking it.
- Interferometer subhalo has **no README.md at any level**, while the imaging
  twin has one in `subhalo/`, `detect/` and `sensitivity/`. Pre-existing gap.

## Human decisions (2026-07-30)

1. **Add `scripts/interferometer/features/advanced/README.md`** — minimal, mirroring
   the imaging sibling (one bullet each for shapelets / potential_correction /
   subhalo). Without it the moved folder would be listed nowhere.
2. **Leave the missing per-folder subhalo READMEs alone** — separate gap,
   separate task (imaging has three: `subhalo/`, `detect/`, `sensitivity/`).
3. **Proceed in parallel** with the four sibling `autolens_workspace` claims,
   after their actual diffs were hand-checked disjoint.

## Brain override

Feature Agent scored `large` (score 9), `split-into-phases`, flagging "public-API
change may ripple to downstream repos" — **vacuous**, no library code is touched.
Same repo-count-proxy misfire recorded for `potential-correction-start-here`
(too-large/12 → one phase). **Overridden to one phase.**

## Out of scope

- Any change to the subhalo scripts' content, models or prose.
- Fixing the commented-out `sensitivity/start_here.py`.
- The autogalaxy/autocti workspaces, and the `point_source` / `multi` regimes.

## Concurrency note

Four `active.md` tasks already claim `autolens_workspace`:
`scaling-relation-bgc-anchored` (#385), `extra-galaxies-multi-galaxy-lens`
(#387), `dspl-terminology-rename` (#390), `potential-correction-start-here`
(#389). Script footprints must be hand-checked for disjointness; the known
shared surface is the regenerated catalogue (`notebooks/`, `llms-full.txt`,
`workspace_index.json`) — whichever merges last rebases and re-runs the
generator, never hand-merges.
