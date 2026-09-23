# Euclid inspection catalogue entries and metadata

This document describes the complete inspection bundle produced by
`scripts/build_inspection_bundle.sh`. It is both a data dictionary and a record
of the provenance needed to interpret the catalogue. The bundle contains master
CSV tables at its root and a self-contained product directory for every selected
lens.

## Catalogue identity and provenance

Record these values whenever a bundle is built or refreshed:

| Metadata | Meaning | DR1 `vis_lp` refresh |
|---|---|---|
| Sample | Dataset sample passed to every producer | `dr1_sep1_rest` |
| Run tag | Suffix of `inspect/<sample>_<run_tag>/` | `sersic100_20260922` |
| Lens selection | Child directory names accepted into the bundle | `output_sed/dr1_sep1_rest/` |
| Initial-model results | Tree containing the normal VIS lens model | `output/dr1_sep1_rest/` |
| Initial search | Search selected from `initial_lens_model` | `vis_lp` |
| Sérsic/SED results | Tree containing the VIS Sérsic and eight-band fits | `output_sed/dr1_sep1_rest/` |
| Completion rule | A fit is readable only after PyAutoFit writes `.completed` | Completed results only |
| Archive rule | Whether the closing tar archive is rebuilt | `CREATE_ARCHIVE=0` for an incremental refresh |

The selection tree is authoritative. A larger normal-model output tree cannot
introduce lenses that are absent from the selected SED sample. Setting
`DATASET_NAMES_PATH=all` disables the selection, and every lens in the
normal-model tree is bundled. Missing optional
result assets are reported as per-lens or per-result skips; they do not turn a
failed scientific output into a successful one and do not abort unrelated
lenses. Structural and programming errors still fail the build.

## Common CSV conventions

`id` is the PyAutoFit result identifier and `lens_name` is the Euclid dataset
directory name. Tables with one result per waveband also contain `waveband`.

Unless stated otherwise, each inferred scalar has five columns:

| Suffix | Statistic |
|---|---|
| *(none)* | posterior median |
| `_lower_1_sigma` | lower 68.3% credible bound |
| `_upper_1_sigma` | upper 68.3% credible bound |
| `_lower_3_sigma` | lower 99.7% credible bound |
| `_upper_3_sigma` | upper 99.7% credible bound |

The photometry and astrometry tables additionally use `_max_lh` for the value
at the maximum-likelihood sample. A fixed model value is repeated across the
median and interval columns, giving it zero posterior width without presenting
it as a sampled quantity. This applies to the mass centre in the current
`vis_lp` results.

Coordinates named `centre_0`, `centre_1`, `y`, and `x` are in arcseconds unless
their name explicitly ends in `_deg`. Ellipticity and shear components,
Sérsic index, and magnification are dimensionless. Flux columns are in µJy.

## `lens_mass.csv`

One row per selected lens, read from the selected `initial_lens_model` search.
The fields are:

| Field | Meaning |
|---|---|
| `id` | PyAutoFit result identifier |
| `lens_name` | Euclid lens/dataset name |
| `centre_0`, `centre_1` | mass-profile centre `(y, x)` in arcseconds |
| `ell_comps_0`, `ell_comps_1` | Isothermal mass ellipticity components |
| `einstein_radius` | Isothermal Einstein-radius parameter in arcseconds |
| `shear_gamma_1`, `shear_gamma_2` | external-shear components |
| `effective_einstein_radius` | latent effective Einstein radius in arcseconds |

Every scientific scalar expands to the five posterior columns described above,
for 42 columns including `id` and `lens_name`.

## `lens_sersic.csv`

One row per selected lens, read from `sersic_lens_model/vis`. It describes the
foreground lens light:

| Field | Meaning |
|---|---|
| `id`, `lens_name` | result and lens identifiers |
| `centre_0`, `centre_1` | lens-light centre `(y, x)` in arcseconds |
| `ell_comps_0`, `ell_comps_1` | lens-light ellipticity components |
| `effective_radius` | Sérsic effective radius in arcseconds |
| `sersic_index` | Sérsic index |

The six scientific scalars each expand to five posterior columns, for 32
columns including the identifiers. Intensity is absent because the pipeline
uses a linear light profile and solves its normalization by linear algebra.

## `source_sersic.csv`

One row per selected lens, also read from `sersic_lens_model/vis`. Its schema is
identical to `lens_sersic.csv`, but the centre, ellipticity, effective radius,
and Sérsic index describe the reconstructed source-plane light profile.

## `magnitudes.csv`

One row per selected lens and available band. A complete lens has eight rows:
VIS, DECam `g`, `r`, `i`, `z`, and NIR `Y`, `J`, `H`.

| Field | Meaning |
|---|---|
| `id`, `lens_name`, `waveband` | result, lens, and band identifiers |
| `crval_ra_deg` | WCS reference right ascension in degrees |
| `lens_flux` | total lens-light flux in µJy |
| `lens_flux_1_fwhm` | lens flux inside one PSF FWHM |
| `lens_flux_2_fwhm` | lens flux inside two PSF FWHM |
| `lens_flux_3_fwhm` | lens flux inside three PSF FWHM |
| `lens_flux_4_fwhm` | lens flux inside four PSF FWHM |
| `lensed_source_flux` | image-plane lensed-source flux in µJy |
| `source_flux` | intrinsic source-plane flux in µJy |
| `magnification` | `lensed_source_flux / source_flux` |

Each flux or magnification field expands to median, maximum likelihood, and
lower/upper 1σ and 3σ values. The table has 52 columns in total.

## `astrometric_offsets.csv`

One row per selected lens and non-VIS band. VIS defines the reference frame and
therefore has no offset row. A complete eight-band lens has seven rows.

| Field | Meaning |
|---|---|
| `id`, `lens_name`, `waveband` | result, lens, and band identifiers |
| `crval_ra_deg` | WCS reference right ascension in degrees |
| `prior_edge_y`, `prior_edge_x` | whether the 3σ interval reaches that result's offset-prior edge |
| `grid_offset_y`, `grid_offset_x` | fitted band displacement relative to VIS in arcseconds |

Each offset expands to median, maximum likelihood, and lower/upper 1σ and 3σ
values. The table has 18 columns. An edge flag is a QA signal: that component
should not be treated as a reliable measurement without a wider-prior refit.

## `witt_wynne.csv` and `witt_wynne.in`

`witt_wynne.csv` has one projected row per selected lens. The columns are:

- identifiers and status: `lens_name`, `projection`, `valid`, `reason`;
- projected lens model: `b_arcsec`, `e_gravlens`, `pa_deg_E_of_N`;
- source position and rule: `source_dx_arcsec`, `source_dy_arcsec`,
  `source_rule`;
- image multiplicity and positions: `n_images`, `image1_x` through
  `image4_x`, and `image1_y` through `image4_y`;
- signed image magnifications: `mag1` through `mag4`;
- relative time delays: `lag1_days` through `lag4_days`;
- distance metadata: `z_lens`, `z_source`, `redshift_source`,
  `d_ol_hinv_mpc`, `d_ls_hinv_mpc`, `h`;
- provenance: `mass_profile`, `search_name`.

The values are a Witt–Wynne SIEP projection of the fitted model, rather than a
new lens-model fit. `witt_wynne.in` is the corresponding zero-centred input for
the external `isit4or2or1` program.

## Per-lens image, FITS, and JSON products

| Product | Contents and metadata |
|---|---|
| `vis_lp_fit.png` | normal VIS lens-model fit diagnostic |
| `vis_lp_image_with_positions.png` | VIS image annotated with inferred positions, when written by the fit |
| `rgb.png` | fit RGB image, with dataset RGB fallback |
| `segmentation.png` | preprocessing segmentation map |
| `fit_sersic.png` | VIS Sérsic fit diagnostic |
| `fit_multi_wavelength.png` | combined eight-band Sérsic diagnostic |
| `coolest_vis_lp.json` | COOLEST representation of the normal `vis_lp` fit |
| `coolest_sersic.json` | COOLEST representation of the VIS Sérsic fit |
| `pre_psf.fits` | multi-band lens light and lensed source before PSF convolution |
| `model.fits` | the same components after PSF convolution |
| `vis_lp_pre_psf.fits` | VIS-only `vis_lp` components before PSF convolution |
| `vis_lp_model.fits` | VIS-only `vis_lp` components after PSF convolution |
| `convergence.fits` | convergence map on the fitted zoomed-mask grid |
| `potential.fits` | lensing potential on that grid |
| `deflections.fits` | y and x deflection maps on that grid |
| per-lens CSV files | the rows for this lens copied from all six master tables |

For the validated DR1 examples, each multi-band deblending FITS has 17 HDUs,
covering the primary HDU plus lens/source components for VIS, DECam `g/r/i/z`,
and NIR `Y/J/H`. Each VIS-only `vis_lp` deblending FITS has 3 HDUs. Convergence
and potential files have a primary plus one image HDU; deflections has a primary
plus y and x image HDUs. FITS headers carry the grid/WCS information needed to
interpret each image plane.

The upstream result's `files/wcs.json` supplies the maximum-likelihood lens
centre, source-plane position, image-plane solutions, RA/Dec positions, source
model, clump list, and clump-selection rule. The catalogue producers read this
metadata through the PyAutoFit aggregator. An absent optional value is an absent
JSON key, rather than a scientific zero.

## Build accounting and validation

Every producer prints `built`, `already_present`, `skipped`, and `errors`
counts. Warnings identify the affected lens and, for multi-band results, the
band or search. A skipped optional product remains absent and visible in this
accounting.

The pre-deployment real-data smoke selected these two DR1 lenses:

- `Tile102006996RA0592256569125DECNEG0665840121534`
- `Tile102006997RA0597002938257DECNEG0666012374596`

It produced 2 lens-mass rows, 2 lens-Sérsic rows, 2 source-Sérsic rows, 2
Witt–Wynne rows, 16 magnitude rows, and 14 astrometric-offset rows. Each lens
directory contained all 22 expected products. Across the smoke bundle there
were 50 files: 14 FITS, 18 CSV, 12 PNG, 4 JSON, and 2 `witt_wynne.in` files.
Every FITS verified, every PNG opened, every JSON parsed, and no mass-table cell
was blank. An identical rerun preserved the same 50 paths with zero changed
SHA-256 hashes.

The production section should be appended after the 100-lens RAL refresh with
the job ID, final master-table row counts, file counts by type, producer totals,
and the exact names of every skipped lens or band.
