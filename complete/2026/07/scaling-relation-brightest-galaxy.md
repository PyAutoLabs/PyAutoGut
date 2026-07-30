## scaling-relation-brightest-galaxy
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/407
- completed: 2026-07-30
- workspace-pr: https://github.com/PyAutoLabs/autolens_workspace/pull/416 (MERGED `f2411d18`)
- summary: |
    Renamed the Faber-Jackson scaling-tier anchor from "BGC" to "the brightest galaxy" in the
    non-cluster `features/scaling_relation` packages, and added a docs note that the same anchor is
    the BCG/BGG at group and cluster scale.

    **Scope was half what the request implied.** Of the four named regimes, only `multi_galaxy`
    (all 6 files, ~135 hits) and one stray docstring line in `point_source/.../likelihood_function.py`
    carried the term. `imaging/` and `interferometer/` already used the `anchor` / "the main lens"
    idiom with zero BGC references, and their cross-refs to multi_galaxy already read "the brightest
    of several co-dominant deflectors" — verified by grep, left alone.

    **The shipped spelling was the transposed `BGC`, not `BCG`.** Future sweeps for this terminology
    must grep both.

    **`group/` deliberately excluded** — a group genuinely has a BCG/BGG; `group/.../modeling.py:256`
    correctly says "set it to the BCG/BGG magnitude". Zero diff lines over `group/`.

    Identifiers: `bgc_index` -> `brightest_index`, `bgc_key` -> `brightest_key`,
    `luminosity_bgc` -> `luminosity_brightest`, `einstein_radius_bgc` -> `einstein_radius_brightest`,
    `L_bgc` -> `L_brightest`. Chose `brightest_*` over the siblings' `anchor_*` because multi_galaxy's
    distinguishing property is that the anchor is *measured* (argmax over luminosity), and "brightest"
    carries that.

    GOTCHA — a blanket noun swap produces redundant prose the acceptance grep cannot see: "the
    brightest co-dominant deflector (the BGC)" became "...(the brightest galaxy)"; "the brighter
    co-dominant galaxy — the BGC" became "— the brightest galaxy". Three such spots, caught only by
    re-reading every inserted line. The longer noun also pushed 13 lines past the ~120-col convention.

    PRE-EXISTING FAILURES found while verifying, reproduce on pristine main, neither in
    smoke_tests.txt (so CI is green on them), NOT fixed, NOT filed:
      1. multi_galaxy/features/scaling_relation/slam.py — IndexError INT_MIN
         (-9223372036854775808) in mapper_util.adaptive_pixel_signals_from via adapt-regularization
         in source_pix_2; a NaN cast to int, consistent with skip-sampler test mode giving a
         degenerate model.
      2. point_source/features/scaling_relation/fit.py — its own astrometric-shift assertion;
         measured per-image shift 0 mas.
    Control-testing the harness on an UNEDITED script first is what prevented misattributing these.

    UNOWNED FOLLOW-UP: regenerating notebooks also rebuilt notebooks/group/start_here.ipynb, because
    scripts/group/start_here.py ("stay on Nautilus") and its committed notebook (older
    MultiStartProdigy prose) have diverged on main. Reverted and excluded here; optional-none-default-typos
    made the same exclusion, so the drift is still on main with no owner.

    Heart was YELLOW at ship (manifest drift: tenant firewall; + 2 stale reasons), human-acknowledged.
    Brain FeatureDecision said large/score-9/split-into-phases off its keyword heuristic
    ("lens", "einstein", "likelihood") — overridden to small, single phase, workspace-only.
    Local smoke 22/22; CI 5/5 across both matrix legs (3.12, 3.13).

## Original prompt

# scaling_relation: rename BGC/BCG to "brightest galaxy" outside the group/cluster regimes

Type: docs
Target: autolens_workspace
Repos:
- autolens_workspace
Difficulty: small
Autonomy: supervised
Priority: normal
Status: active — issue https://github.com/PyAutoLabs/autolens_workspace/issues/407 (2026-07-30)
Follows: draft/docs/workspaces/scaling_relation_bgc_anchored_feature_packages.md (shipped
2026-07-30, autolens_workspace PR#396 + PR#398)

## Original request (verbatim)

> In scaling_relation for multi_galaxy, imaging, interferometer, point_souce dont refer to it as
> the BCG (Brightest cluster galaxy opr _bcg) as these are not clusters, just call it the
> brightest galaxy and keep a note in the docs that for group and clusters its the BCG)

## Scope (verified by grep, 2026-07-30)

The BGC/BCG terminology is confined to two places in the four named regimes:

- `multi_galaxy/features/scaling_relation/` — all six files carry it (README.md, modeling.py,
  fit.py, simulator.py, slam.py, likelihood_function.py), in both prose ("the BGC") and
  identifiers (`bgc_index`, `bgc_key`, `luminosity_bgc`, `einstein_radius_bgc`, `L_bgc`).
- `point_source/features/scaling_relation/likelihood_function.py:4` — a single stray
  "BGC-anchored scaling tier" in the module docstring.

`imaging/features/scaling_relation/` and `interferometer/features/scaling_relation/` are already
clean — they use `anchor` / "the main lens" throughout, and their two cross-references to the
multi_galaxy package already say "the brightest of several co-dominant deflectors". No change
needed there; confirm and report rather than inventing edits.

`group/features/scaling_relation/` is **out of scope** — a group genuinely has a BCG/BGG, and
`modeling.py:256` correctly says "set it to the BCG/BGG magnitude". Leave it.

## Required changes

1. Prose: "the BGC" → "the brightest galaxy" (or "the brightest of the pair" where that reads
   better in context). Section header `__What Changes For A BGC-Anchored Tier__` and
   `__Luminosities + The BGC__` rename accordingly.
2. Identifiers: `bgc_index` → `brightest_index`, `bgc_key` → `brightest_key`,
   `luminosity_bgc` → `luminosity_brightest`, `einstein_radius_bgc` → `einstein_radius_brightest`,
   `L_bgc` → `L_brightest` (including in the `slam.py` pipeline-function keyword arguments and
   their call sites).
3. Add a short docs note — multi_galaxy README.md plus the modeling.py docstring — that in the
   group and cluster regimes this same anchor galaxy is the BCG (brightest cluster galaxy) /
   BGG, and point at `group/features/scaling_relation`.
4. Regenerate the notebook mirrors (`notebooks/multi_galaxy/features/scaling_relation/*.ipynb`,
   `notebooks/point_source/features/scaling_relation/likelihood_function.ipynb`,
   `notebooks/multi_galaxy/features/scaling_relation/README.md`) from the scripts rather than
   hand-editing them.

## Acceptance

- `grep -rin "bgc\|bcg" scripts/{imaging,interferometer,multi_galaxy,point_source}/features/scaling_relation/`
  returns nothing except deliberate "in a group or cluster this is the BCG" notes.
- Same grep over the corresponding `notebooks/` trees.
- `group/features/scaling_relation` diff is empty.
- The four scaling_relation scripts that run still run (fit.py / likelihood_function.py are the
  cheap ones; modeling.py / slam.py under test mode).
