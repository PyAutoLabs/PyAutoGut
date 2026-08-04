# HST needs a DQ-bits dial — we mask every DQ-flagged pixel where STScI keeps most of them

Type: bug
Target: pyautoreduce
Repos:
- PyAutoReduce
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised

`autoreduce/drizzle/combine.py:drizzle_kwargs_for` never sets `final_bits` /
`driz_sep_bits`, and no adapter sets them either — `final_bits`,
`driz_sep_bits` and `mdriztab` appear **nowhere** in the repo (verified by grep
over `autoreduce/`, `scripts/` and `docs/design/`). So every reduction inherits
drizzlepac's package default `final_bits = "0"`
(`drizzlepac/pars/astrodrizzle.cfg:101`), which means **no DQ bit is treated as
good**: every flagged pixel is rejected, including the hot, warm and blob
pixels that calacs/calwf3 have already corrected.

That is far more aggressive than STScI's own practice, and it shows up as
structured defects in the delivered products on both HST instruments we
support.

## The two symptoms (one root cause)

**WFC3/IR — zero-coverage holes.** On snapshot data with tiny dithers,
detector-fixed DQ 512 (blob) regions produce structured zero-coverage holes in
the mosaic that the packaging guard (correctly) refuses. PJ011646 (program
14653, F160W, 5 exposures, 2–6 px dithers) failed with a single 123-px hole at
r = 5.3″, outside the 3.8″ science mask, DQ 512 at the same detector pixels in
all five exposures (validation issue #25, now closed). Aris's trusted
reduction of the same data has no hole. The slacs1430-style validation script
`reduce_pj011646.py` carries a documented monkeypatch workaround until this
ships.

**ACS/WFC — high-noise stripes through lens cores.** F814W SLACS-gold noise
maps show stripes of elevated noise, some running straight through the
deflector cores, that the legacy SLACS/Amy reductions do not have (user report
2026-08-04). Mechanism: rejecting hot (16) and warm (64) pixels on top of the
genuine bad columns (4, 128) removes pixels that are partly *column-organised*
on an aged ACS CCD (trap columns, CTE trails), so the IVM weight along those
columns is reduced rather than zeroed. Noise then rises by `sqrt(N/(N-1))` per
lost exposure — ×1.41 at N=2, ×1.22 at N=3, ×1.15 at N=4, ×1.08 at N=7 — so
few-exposure targets stripe visibly and many-exposure ones do not.

## Verified evidence — STScI's own MDRIZTAB values

Read directly out of the cached CRDS reference files under `scripts/cache/crds/`,
so these are facts about the pipeline STScI ships, not recollection:

| Detector | MDRIZTAB file | `numimages` | `driz_sep_bits` | `final_bits` |
|---|---|---|---|---|
| ACS/WFC | `acs/37g1550cj_mdz.fits` | 1 | 65535 | **65535** |
| ACS/WFC | " | ≥2 | 336 | **336** |
| WFC3/UVIS | `wfc3/2ck18260i_mdz.fits` | 1 | 65535 | **65535** |
| WFC3/UVIS | " | ≥2 | 336 | **336** |
| WFC3/IR | `wfc3/3562021pi_mdz.fits` | 1 | 65535 | **65535** |
| WFC3/IR | " | 2 | 65535 | **528** |
| WFC3/IR | " | ≥4 | 528 | **528** |

Three things fall out of that table:

1. **336 = 16 + 64 + 256.** Hot, warm and saturated pixels are treated as
   usable for multi-exposure ACS/UVIS, because the dark subtraction has
   already corrected them. We reject all three.
2. **528 = 512 + 16 for WFC3/IR.** STScI passes exactly the blob bit that
   caused the PJ011646 hole. PJ011646 had 5 exposures, so it lands on the
   `numimages ≥ 4` row — under standard practice that hole could not have
   occurred. This confirms the original prompt's guess ("standard IR practice
   passes 512") from the reference file rather than from lore.
3. **`final_bits` is exposure-count dependent, and single-exposure data uses
   65535 — every bit treated as good.** That is the SLACS SNAP regime, and it
   is an independent explanation for why the legacy SLACS maps look clean:
   with one exposure there is nothing to fill a masked pixel with, so the
   standard recipe keeps flagged pixels rather than punching holes. Any fix
   must therefore be N-aware; a flat constant is wrong.

## Leg 1 — the bits dial

- Expose the bits as an adapter default plus a `TargetSpec` override, keyed on
  exposure count, mirroring the MDRIZTAB rows above (acs_wfc and wfc3_uvis:
  65535 at N=1, 336 at N≥2; wfc3_ir: 65535 at N=1, 528 at N≥2).
- **Do not simply switch on `mdriztab=True`.** MDRIZTAB supplies the whole
  parameter set — `final_scale`, `final_pixfrac`, `final_kernel`, `final_rot`
  — and `hst_acs_pipeline.md` stage 3 deviates from those deliberately and
  with justification (0.05″/pix, pixfrac 0.8, north-up). Enabling `mdriztab`
  risks silently reverting those lensing deviations; verify the precedence
  rules before trusting it. The safer route is to read the bits columns and
  keep our own explicit kwargs.
- Record the chosen bits, and their provenance (adapter default vs user
  override), in `reduction.json`, so existing datasets stay re-derivable.
- Unit-test `drizzle_kwargs_for` across the N boundaries per adapter
  (numpy/astropy only — no drizzlepac in `test_autoreduce/`).
- Document the choice and the blob/hot-pixel physics in `docs/design/wfc3.md`
  and `docs/design/hst_acs_pipeline.md`.

**Control test before anything else:** re-drizzle one striped SLACS target at
the current `0` and at the MDRIZTAB value, and diff the weight maps and noise
maps. If the stripes do not move, the cause is elsewhere — exposure count,
dither geometry, or genuine bad columns — and leg 1 is not the fix; say so
rather than shipping the dial as though it were.

## Leg 2 — the guards are blind to partial weight deficits

Both existing guards can only see *total* coverage loss, so the ACS stripe
class ships silently:

- `autoreduce/noise/rms.py:mask_isolated_bad_pixels` tests
  `bad = ~isfinite(noise) | (noise <= 0)`. A stripe with reduced-but-nonzero
  IVM weight is finite and positive, so it passes every check — including the
  `protect_radius_arcsec` (1.5″) protection whose entire purpose is to
  guarantee that "the lens itself must be clean", and the structured-defect
  clustering check that would otherwise refuse a column.
- `autoreduce/drizzle/diagnostics.py:weight_uniformity` is a global RMS/median
  over the whole cutout against a 0.2 limit; the slacs0008 spike measured
  0.066, and a handful of degraded columns cannot move it.

Add a **local** weight-deficit diagnostic — per-column and/or
local-vs-median weight ratio, evaluated inside `protect_radius_arcsec` — that
fires when coverage in the science region is materially below the cutout
median, and record it in `reduction.json` beside the existing uniformity
number. This is *not* the same question as the already-noted "should the
packaging guard distinguish defects inside vs outside the target's science
aperture" (that one is about zero-coverage holes outside the mask); this is
about finite-but-degraded coverage *inside* it.

Leg 2 is independent of leg 1 and is the detector for it: landing it first
gives the control test above an objective pass/fail instead of an eyeball
judgement. Expect two PRs behind this one issue.

## Policy — unchanged

Mask-only stands (`hst_acs_pipeline.md:368`): bad columns are masked, never
inpainted or interpolated. Nothing in this task fabricates pixel values. If a
defect survives the bits fix, the downstream lever is masking or
`apply_noise_scaling` in the modelling workspace, not repair in the reduction.

## Coordination

- Supersedes the WFC3/IR-only framing of this prompt (originally
  `wfc3_ir_dq_bits_dial.md`, filed 2026-07-10). The ACS leg was added
  2026-08-04 after the SLACS-gold noise-map report, and the MDRIZTAB read
  showed both instruments share one root cause and one fix site.
- Related but distinct, both open on the tracker: **#61** (driz_cr erodes flux
  at steep-gradient cores → LACosmic option) and **#62** (tier-1 ePSF built
  from the CR-rejected mosaic). All three concern how DQ/CR masking degrades
  products, but they touch different stages — do not fold them in.
- `draft/research/pyautoreduce/acceptance_noise_rebaseline.md` re-baselines the
  SLACS parity numbers. A bits change moves the IVM weights and therefore the
  noise maps, so run that study *after* this lands or its numbers will need
  redoing.

<!-- formalised by the Intake (Conception) Agent on 2026-07-10 from user-intake -->
<!-- rescoped WFC3/IR -> HST-wide on 2026-08-04 from user-intake (ACS leg + MDRIZTAB evidence + guard leg) -->
