# Refresh the stale `.script_sizes.json` snapshot in @autolens_workspace

Difficulty: small
Autonomy: safe
Priority: low

## The problem

`.script_sizes.json` is the truncation guard described in
`autolens_workspace/AGENTS.md`: it records the byte size of every
`scripts/**/*.py`, and `scripts/check_sizes.sh` flags any script that shrank by
>50% since the snapshot. It exists because of a real incident where a
header-insert pass replaced ~80% of 17 scripts with the header alone.

**The snapshot has drifted badly enough that the guard now protects almost
nothing.** Measured on `main` at `726d060d` (2026-07-30):

| Condition | Count |
|---|---|
| Entries in snapshot | 373 |
| Entries whose recorded size ≠ actual size | **116** |
| Keys naming files that no longer exist | **3** |
| Scripts on disk absent from the snapshot entirely | **12** |
| Entries that would currently trip the >50% shrink guard | **0** |

That last row is the point. `check_sizes.sh` reports "OK: all scripts within
size tolerance" today, so the drift is invisible — but 116 baselines are wrong
and 12 scripts have *no* baseline at all, so a genuine truncation in any of them
would be measured against a stale or absent reference.

### The 3 dead keys

```
scripts/imaging/features/potential_correction/likelihood_function.py
scripts/interferometer/features/potential_correction/likelihood_function.py
scripts/interferometer/features/potential_correction/start_here.py
```

These are leftovers from the `features/potential_correction/` →
`features/advanced/potential_correction/` move.

### The 12 unsnapshotted scripts

Mostly recent `multi_galaxy` work — e.g. `scripts/multi_galaxy/source_science.py`,
`likelihood_function.py`, `simulator_sample.py`,
`features/extra_galaxies/{modeling,simulator}.py`.

## Why it drifted

`AGENTS.md` asks contributors to run `scripts/check_sizes.sh --update` in the
same diff as an intentional shrink. Nothing enforces it, and because the guard
stays green while drifting, nobody notices.

## Proposed fix

1. Run `scripts/check_sizes.sh --update` on clean `main` as a **single dedicated
   commit** that touches nothing else, so the refresh is reviewable and is not
   entangled with a feature diff.
2. Before committing, sanity-check that no entry shrank drastically —
   a >50% drop in the refresh itself would mean a real truncation is being
   blessed rather than recorded. Diff the before/after and eyeball the large
   negative deltas.
3. Consider a CI guard so this cannot silently rot again: fail if any
   `scripts/**/*.py` is missing from the snapshot, or if any key names a
   nonexistent file. That catches the two *structural* drifts (dead keys,
   unsnapshotted scripts) cheaply, without the false-positive risk of gating on
   exact size equality — sizes legitimately change on every prose edit.

Step 3 is the part worth debating; steps 1–2 are mechanical.

## Do NOT bundle this into a feature PR

This is exactly why it is filed separately. Running `--update` inside a scoped
PR sweeps all 116 unrelated entries into that diff and silently blesses other
changes' shrinkage. Discovered while shipping the DSPL rename
(autolens_workspace#394), where the 18 affected entries were instead updated by
hand for this reason.

## Verification

- `check_sizes.sh` green (it already is — that is not sufficient evidence)
- Recompute the four counts above: stale = 0, dead keys = 0, unsnapshotted = 0
- If step 3 lands, prove the new CI guard is not vacuous with a positive control
  (delete an entry, confirm CI reddens)
