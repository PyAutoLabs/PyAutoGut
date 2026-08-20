# Numba CPU likelihood: restore legacy-class speed (adaptive-mesh transform + MGE convolution)

Type: feature
Target: autoarray
Repos:
- @PyAutoArray
- @PyAutoGalaxy
Difficulty: large
Autonomy: supervised
Priority: high
Status: formalised

## Original request (verbatim, 2026-08-20)

> ok, so this likelihood function used to have other tools in numba to do the
> slow things, this includes a Convolver object for the convolution which mapped
> out in memory the convolution and dediciated numba functions for things like
> mapping matrix construction. To be honest, I wonder if the numba function for
> the mapping matrix construction that avoids Mapper.sparse_triplets_data is
> still in the source code and its a bug or error that its not being used
> instead of it. So, do a hunt of the source code and repo history for the big
> bottlenecks, work out if simple soutions in this legacy exist and work them
> back into the source code. We may of removed some of this for the sake of a
> more concise and maintainable source code, but with AI I think we can have
> more code to make it fast and manage it without too much issue now. I am
> confident we used to have a really speedy likelihood for all of this and that
> going through history can get us back there with numerically the same
> likelihood values

> Follow-up: ok, remember that mapping matrix is made for this route but not
> blurred_mapping_matrix, which might negate the need for the Convoler (I think
> it does). So its prob just the mapping matrix construct has incorrectly gone
> via triples?

## Hunt verdict (2026-08-20, source + history archaeology)

The triplets hypothesis is **not** the story: `sparse_triplets_from` is ~12
lines of vectorized numpy (ms), and the numba `unique_mappings` compression
(`data_slim_to_pixelization_unique_from`) still drives every sparse-operator
kernel — the legacy mapper fast path was never deleted. The profiled 49%
(euclid) / 88% (hst) "sparse_triplets_data" cost is misattributed lazy-property
accounting: the real hot spot is the **RectangularAdaptDensity kernel-CDF
transform** (`autoarray/inversion/mesh/interpolator/rectangular.py:146-172`) —
an exact O(M_sub x N_data) `scipy.special.erf` sum (>1e9 erf/likelihood at
HST), pure numpy with 126 MB broadcast temporaries, rebuilt every evaluation
(traced grid changes with the mass model). This is new JAX-era adaptive-mesh
machinery; the legacy stack was fast because its rectangular mesh had trivial
uniform geometry — no deleted numba kernel computes this.

Legacy-history anchors (for reference, not restoration of the #1 lever):
tag 2026.1.21.3 / df4516e7 = last release with the intact w-tilde numba path
(`w_tilde_curvature_preload_imaging_from` etc., renamed 2026-02-03 ff1f04d9
into today's psf-precision-operator kernels); numba frame-preload Convolver
deleted 2025-10-01 aa71fb3e (not needed on this route — PSF lives in the
precision operator, per the follow-up above).

Secondary confirmed costs:
- MGE linear-func operated mapping matrices (~19% at euclid): 60 independent
  `psf.convolved_image_from` scipy convolutions
  (`autogalaxy/profiles/light/linear/abstract.py:358-382`), each re-padding and
  re-transforming the PSF. A batched exact equivalent already exists:
  `Convolver.convolved_mapping_matrix_via_real_space_np_from`
  (`autoarray/operators/convolver.py:1437`).
- `linear_func_operated_mapping_matrix_dict` is an **uncached** `@property`
  (`autoarray/inversion/inversion/imaging/abstract.py:184`) rebuilt on every
  access and consumed ~5 times per evaluation, including inside an O(60^2)
  loop with repeated `(N_pix, 60)` noise divisions
  (`imaging_numba/sparse.py:443,451`).
- `mapper_numba_util.py:74` clears an O(source_pixels) array once per data
  pixel inside `unique_mappings` (minor at <=1500 sources).

## Goal

Make the numba CPU sparse-operator likelihood (the `cpu_fast_modeling.py`
route) fast again with **unchanged likelihood values**:

1. **Kernel-CDF fast path (dominant, 49-88%)**: numba implementation of the
   adaptive-rectangular CDF transform — loop-based erf sum without broadcast
   temporaries, exploiting exact fp64 erf saturation (sorted points + +-~6h
   window; outside contributions are exactly 0/1) so results match the current
   numpy path to fp precision. Target >=5-10x on this step.
2. **Batched MGE convolution (19%)**: route the linear-func operated mapping
   matrices through the existing batched convolver call (one FFT for all 60
   columns, blurring region included); verify bit-comparability.
3. **Cache/hoist `linear_func_operated_mapping_matrix_dict`** (and the noise
   division) — exact-identical, removes pure repeated work.
4. **Validate + measure** with the new autolens_profiling numba cells
   (autolens_profiling#151/PR#152): pinned euclid/hst log-likelihoods must
   pass; re-run runtime + breakdown; update dashboards.

Estimated end state: hst 21.6 s -> ~3-5 s, euclid 2.15 s -> ~0.7 s per
evaluation. Follow-up (out of scope here): approximate interpolated-CDF mode
(config-gated) if exact saturation windowing is insufficient at scale.
