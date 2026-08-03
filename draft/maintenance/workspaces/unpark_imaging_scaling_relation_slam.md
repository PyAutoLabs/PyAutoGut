# Un-park imaging/features/scaling_relation/slam once PyAutoArray#431 merges

Type: maintenance
Target: autolens_workspace
Repos:
- autolens_workspace
Difficulty: small
Autonomy: supervised
Priority: normal
Status: formalised

BLOCKED until PyAutoArray PR#431 merges and reaches the installed stack. Do not
start before then — the script only passes with that loader fix in place.

## What

Remove this NEEDS_FIX line from `autolens_workspace/config/build/no_run.yaml`:

    - imaging/features/scaling_relation/slam # NEEDS_FIX 2026-07-30 - measures its
      luminosities from a preceding light stage, which under PYAUTO_TEST_MODE returns
      no usable samples, so every measured luminosity is 0.0 ...

## Why

The park's stated cause was never the script's fault. Root cause was
`cap_array_2d_for_small_datasets` keeping the caller's uncapped `pixel_scales` for
at-or-below-cap data, mislabelling the frame 6x so off-centre galaxies fell outside
it and their non-negative linear intensity solve correctly returned 0.0
(PyAutoArray#430, fixed by PR#431).

Measured 2026-08-03 against the fix, capped smoke profile, cleared dataset + output:
`scripts/imaging/features/scaling_relation/slam.py` → **exit 0**, 6 searches genuinely
run, 0 cached resumes, no `luminosity_from` raise.

## Do NOT also un-park the sibling

`multi_galaxy/features/scaling_relation/slam` must STAY parked. It clears the
0.0-luminosity cause with the same fix but then fails on a separate latent bug
(`slam.py:863` mixes the script's hardcoded `pixel_scale` with the dataset's
corrected `pixel_scales`, producing an empty mask). See
`draft/bug/autolens_workspace/script_local_pixel_scale_vs_dataset_pixel_scales.md`.
Its NEEDS_FIX reason should be UPDATED to name the real remaining cause rather than
the 0.0-luminosity one, which will no longer be true.

`interferometer/features/scaling_relation/slam` is unaffected and already runnable —
it hardcodes `luminosity_anchor` instead of measuring it. Leave it alone.

## Verify before removing

Re-run the script under the capped smoke profile with the merged loader fix and
confirm exit 0. Clear `output/test_mode/<path>` as well as `output/<path>` — output is
namespaced under `output/test_mode/` in test mode, and a stale tree reads as a pass
via "Fit Already Completed".
