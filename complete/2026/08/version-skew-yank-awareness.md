# version-skew-yank-awareness

**Completed:** 2026-08-18
**Type:** feature · **Target:** PyAutoHeart · **PR:** PyAutoHeart#148 (merged,
`7659f153`; branch `feature/version-skew-yank-awareness`)

## Summary

Closed the yank gap the `version_skew` Heart leg acknowledged in its own
docstring: the tick check compares floors against **local git tags**, so it
could not see the other way a floor goes bad — the release it names being
**yanked on PyPI** afterwards (the 2026-07 incident shape, where every floor
named the yanked `2026.7.6.649`). Filed as the surviving loose end when the
Phase 4 tracker retired ([[release-version-sync-back-to-main]]); shipped the
same day.

## What shipped

`python -m heart.checks.version_skew --pypi` — a deep, on-demand leg that asks
the PyPI JSON API whether each workspace floor still names an installable
(non-yanked) release and whether *any* installable release satisfies it.

- **Statuses → readiness:** `UNSATISFIABLE` (nothing installable ≥ floor —
  every candidate yanked; same defect class as the tag leg) → **RED**;
  `FLOOR_YANKED` (floor itself yanked/absent but newer installable releases
  satisfy it — floors are `>=` bounds so installs still resolve) → **YELLOW**
  "bump the floor"; `UNKNOWN` (PyPI unreachable) → **STALE**, never a false
  block; `OK`/`BAD` as in the tag leg.
- **Tick untouched:** network-bound, so never run from `tick.sh` — on-demand /
  nightly only, behind the explicit `--pypi` flag.
- **Sidecar state** (`version_skew_pypi.json`): the tick's `version_skew.json`
  rewrite can never clobber on-demand PyPI evidence, and vice versa. An absent
  slice is no signal in readiness and the dashboard.
- `run_pypi()` side-effect-free like `run()` (persistence in `main()` only);
  one PyPI fetch per distinct package, not per workspace. Wired through
  `state.py` snapshot, readiness legs + score weights, and a "Version skew
  (PyPI)" dashboard section.
- **Validated:** 484 tests pass (15 new); live probe against real PyPI
  (`autolens`, 421 releases): `2026.7.9.1 → OK`, the incident release
  `2026.7.6.649 → FLOOR_YANKED`, `2099.1.1.1 → UNSATISFIABLE`,
  `garbage → BAD`.

## Key findings / traps

- **Tenant firewall caught a real leak on the first CI round:** the
  one-fetch-per-package test named `HowToLens` — a *new* instance fact in
  organ code (`repos_sync.py --check --only "tenant firewall (organ code)"`).
  Fixed by using `autolens_assistant` (an already-present fact in that file,
  same `autolens` package mapping). When testing organ code, pick instance
  names the file already carries; the firewall treats new ones as drift even
  in tests.
- **Verdict-shape reasoning recorded in the check itself:** a yanked floor
  with newer installable releases is deliberately YELLOW, not RED — `>=`
  semantics mean installs still resolve; only "nothing installable ≥ floor"
  blocks. Offline degrades to UNKNOWN/STALE so an offline dev box can never
  produce a false RED.
- Fork (b) of the version model stands: this reads state only — no
  commit-back behaviour was added anywhere.

## Original prompt

# version_skew: flag a floor that names a PyPI-yanked release

Type: feature
Target: PyAutoHeart
Repos:
- PyAutoHeart
Difficulty: small
Autonomy: supervised
Priority: low
Status: formalised

## Why

The `version_skew` Heart leg (reworked under build-chain #155 Phase 4 task 2,
PyAutoHeart#96) enforces "a floor must name an *installable* release" only
against **local git tags**: UNSATISFIABLE fires when
`version.minimum_library_version` exceeds the newest `YYYY.M.D.B` release tag.
It cannot see the other way a floor goes bad — the release it names being
**yanked on PyPI afterwards** (as `2026.7.6.649` was; that yank is what
originally exposed the "floors named a yanked release" bug that this check now
half-guards). The gap is acknowledged in the check itself
(`heart/checks/version_skew.py:33`: "a release that was later *yanked* on PyPI —
that needs the PyPI API, not git tags") and was left unowned when the Phase 4
tracker (`complete/2026/08/release-version-sync-back-to-main.md`) retired.

## Scope

- Extend `version_skew` (or add a sibling non-tick check, if network access
  disqualifies it from the tick path — the current check is deliberately
  local-tags-only, no import/network) to query the PyPI JSON API for the
  floor's version and flag `yanked: true` per package.
- Verdict shape should mirror the existing one: a yanked floor is the same
  class of defect as UNSATISFIABLE (no installable version satisfies "exactly
  this floor"), but the floor semantics (>=) mean a yanked floor with newer
  non-yanked releases still resolves — decide whether that is RED, YELLOW, or
  informational, and record the reasoning.
- Offline/API-failure behaviour must be UNKNOWN/STALE, never a false RED —
  match how the tag-based check treats unresolvable repos.

## Constraints

- Do not slow the readiness tick: if the PyPI call cannot be cached or made
  optional, keep it out of the tick path (nightly / on-demand only).
- Fork (b) of the version model stands (mains authoritative, floors + tags +
  wheels as the live signals — see the retired tracker). This check reads
  state; it must not resurrect any commit-back behaviour.
