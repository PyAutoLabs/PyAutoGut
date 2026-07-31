# LACosmic per-frame CR masking option + decouple PSF-star pass from the science CR pass

Type: feature
Target: PyAutoReduce
Difficulty: medium
Autonomy: supervised
Priority: high
Status: draft

Community-reported (@samlange04, PyAutoReduce#61 + #62, measured on SLACS
ACS/WFC F814W): the unconditional `driz_cr=median=blot` route in
`autoreduce/drizzle/combine.py::drizzle_kwargs_for` systematically erodes flux
at steep gradients — the blotted-median reference reads low at any sub-pixel-
shifted peak, so genuine core flux is flagged as CR. Reporter measured ~37%
deflector-core flux loss, worse with looser thresholds (the reference model is
the fault, not the cut), and full core preservation (peak 1.000, 1" 0.979)
with LACosmic per-frame masking + plain weighted-mean drizzle. The same
mechanism holes field-star cores before `psf/stars.py::find_stars` ever sees
them (#62): rebuilding from a no-CR pass took their usable star count
344 → 599 (+74%) and rescued 4 lens/filter pairs from model-PSF fallback.

Scope (one task — the halves are coupled through the no-CR pass):

1. **CR-method dial** on `TargetSpec` (sibling of `final_pixfrac` /
   `final_kernel`): `cr_method: "driz_cr" | "lacosmic"`. LACosmic route =
   per-frame Laplacian masking (van Dokkum 2001; `astroscrappy` or deepCR —
   `frame_products` already runs deepCR per-frame, so there may be a lever to
   reuse) written into the DQ array, then plain weighted-mean drizzle
   (`median=False, blot=False, driz_cr=False`).
   **Trap (reporter hit it, verify with a test):** the LACosmic drizzle pass
   must set `resetbits=0` — the AstroDrizzle default 4096 clears exactly the
   DQ bit the CR mask lives in, silently producing an unmasked drizzle.
2. **Decouple star-finding from the science pass**: `pipeline.py::_psf`
   currently measures stars on whatever `_combine` produced. Tier-1/1b star
   extraction should draw from the least-CR-rejected pass available,
   independent of which pass ships as the science mosaic (kernel shape is
   pass-independent). Provenance records which pass fed the stars.
3. **Default decision is human-gated**: whether `lacosmic` becomes the
   default (reporter suggests so) is a documented deviation from STScI
   defaults — justify against the SLACS reference-quality bar
   (`docs/design/hst_acs_pipeline.md`) and validate on the
   slacs1430+4105 comparison task (`active/pyautoreduce_slacs1430_acs_comparison.md`)
   before flipping; landing it as an option first is acceptable.

Validation: unit tests for the pure kwargs/decision functions (house style);
real-data before/after on a SLACS ACS target measuring core-flux retention
and usable-star count, mirroring the reporter's numbers. Include a tuned
`driz_cr` comparison arm: our adapters set no `driz_cr_snr`/`driz_cr_scale`,
so we run AstroDrizzle's aggressive pipeline defaults (scale 1.2/0.7) — the
STScI-documented mitigation for bright-source flagging is raising
`driz_cr_scale` (published reprocessing used 1.5/1.2), and the default-flip
decision should compare LACosmic against *tuned* driz_cr, not only against
our current untuned defaults.

<!-- filed from /community triage of PyAutoReduce#61 + #62 (2026-07-31) -->
