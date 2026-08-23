# autolens_workspace_developer committed datasets do not reproduce from their own scripts

Type: bug
Target: autolens_workspace_developer
Repos:
- @autolens_workspace_developer
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: draft
Filed: 2026-08-23

## Provenance

Found while shipping `pynufft_removal_downstream_residue` phase 1
(@autolens_workspace_developer#129), recorded in
`complete/2026/08/pynufft-removal-residue-phase-2.md` as **"Found while
shipping, NOT filed anywhere"**. This prompt is that filing.

## The finding

Regenerating a dataset config that phase 1 did **not** touch (`sma`, a DFT
dataset) via `jax_profiling/dataset_setup/interferometer.py` yields *different
data* from what is committed, plus a differing `SMALLDAT` header stamp.

So the committed FITS in this repo are not reproducible from the scripts that
claim to generate them. Either the scripts drifted from the data, the data was
generated with different settings/seed, or the header stamp encodes something
the current code no longer writes. Which of the three it is has NOT been
established — establish it before changing anything.

## Why it matters

Every profiling result measured against these datasets is measured against
data no current script can reproduce, so a profiling regression cannot be
distinguished from a dataset difference. It also means "regenerate and
compare" is not currently a usable verification technique in this repo — the
phase-1 fix had to verify by *running* `simulate()` for every instrument
rather than by diffing output.

## Suggested approach

1. Diff a regenerated `sma` against the committed one — pixel data and the
   full FITS header, not just the `SMALLDAT` stamp.
2. Establish the cause (seed/settings drift, code drift, or a stale commit)
   before deciding whether to re-commit regenerated data or fix the scripts.
3. Decide deliberately whether committed datasets should exist here at all, or
   be generated on demand.

## Related

- `draft/maintenance/autolens_workspace_developer/stale_api_rot_audit.md`
  records the same repo's broader rot and its **absent-FITS** gap (scripts
  needing datasets that are not in the repo). That is a *different* problem
  from this one: there the data is missing, here it is present but
  irreproducible. Both share the root cause that repo names — **no smoke
  coverage / no test CI**.

## Acceptance

- The cause of the `sma` mismatch is identified and written down.
- Either the committed datasets regenerate byte-comparably (modulo a
  documented, deliberate header stamp), or the repo records why they cannot
  and what the verification technique is instead.
