#!/usr/bin/env bash
#
# Euclid Pipeline: Inspection Bundle Builder
# ==========================================
#
# Runs the ten catalogue producers in dependency order and assembles a
# per-lens inspection bundle for one sample. Idempotent: safe to re-run as more
# results land — already-built lenses are skipped by each stage.
#
# Output layout (inspect/<sample>[_<run_tag>]/):
#
#   lens_mass.csv                        # master CSVs, one row per lens
#   lens_sersic.csv
#   source_sersic.csv
#   witt_wynne.csv                       # one row per lens: the SIEP projection
#   magnitudes.csv                       # one row per (lens, waveband)
#   astrometric_offsets.csv              # one row per (lens, non-VIS waveband)
#   <dataset_name>/
#       vis_lp_fit.png                   # collected by build_inspect.py
#       vis_pix_fit.png
#       vis_lp_image_with_positions.png
#       rgb.png
#       segmentation.png
#       fit_sersic.png
#       coolest.json                     # COOLEST template of the vis_pix fit
#       coolest_sersic.json              # COOLEST template of the sersic fit
#       pre_psf.fits                     # lens light + lensed source, pre-PSF
#       model.fits                       # the same, post-PSF convolution
#       convergence.fits                 # mass model maps, on the zoomed mask grid
#       potential.fits
#       deflections.fits                 # DEFLECTIONS_Y, DEFLECTIONS_X
#       fit_multi_wavelength.png
#       lens_mass.csv                    # this lens's row of each master CSV
#       lens_sersic.csv
#       source_sersic.csv
#       witt_wynne.csv
#       witt_wynne.in                    # isit4or2or1 input, zero-centred
#       magnitudes.csv
#       astrometric_offsets.csv
#
# Stages 8-10 read a separate results tree (default `output_sed`) holding the
# multi-band SED fits produced by running the waveband scripts with
# PYAUTO_OUTPUT_DIR=output_sed. They are skipped when that tree has no directory
# for the sample.
#
# Usage:
#   bash scripts/build_inspection_bundle.sh [sample] [run_tag]
#   bash scripts/build_inspection_bundle.sh q1_walsmley
#   bash scripts/build_inspection_bundle.sh dr1_prelim_grade_ab run250
#
# Environment:
#   OUTPUT_DIR        initial-model results tree       (default: output)
#   SED_OUTPUT_DIR    multi-band SED results tree      (default: output_sed)
#   SERSIC_OUTPUT_DIR Sersic results tree; defaults to SED_OUTPUT_DIR when its
#                     sample exists, otherwise OUTPUT_DIR
#   INITIAL_SEARCH_NAME initial-model search to bundle (default: vis_pix)
#   DATASET_NAMES_PATH directory whose child names select the exact lenses;
#                     defaults to SERSIC_OUTPUT_DIR/<sample> when unset. Set it
#                     to `all` (or `none`, or an explicit empty value) to
#                     disable the selection and bundle every lens under
#                     OUTPUT_DIR/<sample> — e.g. a full vis_lp-only build while
#                     output_sed/<sample> holds only a Sersic subset.
#   TAR_TO            when non-empty, stage 1 (build_inspect.py) also writes an
#                     uncompressed tar of the bundle's collected PNGs +
#                     COOLEST templates here, so they come back in one stream
#                     (default: empty, no tar)
#   SKIP_SED=1        skip stages 8-10 even if present (default: 0)
#   CREATE_ARCHIVE=0  do not tar the bundle at the end (default: 1)
#   DATASET_PREFIX    only collect datasets with this name prefix (default: all)

set -euo pipefail

SAMPLE="${1:-q1_walsmley}"
RUN_TAG="${2:-}"
if [ -n "$RUN_TAG" ]; then
    INSPECT_DIR="inspect/${SAMPLE}_${RUN_TAG}"
else
    INSPECT_DIR="inspect/${SAMPLE}"
fi

SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd -- "$SCRIPT_DIR/.." && pwd )"

# On HPC, activate.sh activates the shared PyAuto venv under PYAUTO_HPC_BASE and
# puts its checkouts on PYTHONPATH. It is HPC-only — sourcing it elsewhere fails
# — so it is used only when that venv is actually present and the caller has not
# already set up an environment (PYAUTO_ROOT is exported by a worktree
# activate.sh). Everywhere else the ambient install is used. Export
# PYAUTO_HPC_BASE to point at your shared PyAuto checkout.
HPC_BASE="${PYAUTO_HPC_BASE:-/path/to/large/storage/your_username/PyAuto}"
if [ -z "${PYAUTO_ROOT:-}" ] && [ -d "$HPC_BASE" ] && [ -f "$PROJECT_ROOT/activate.sh" ]; then
    # shellcheck disable=SC1091
    source "$PROJECT_ROOT/activate.sh"
fi

# Writable caches for numba and matplotlib (see AGENTS.md).
export NUMBA_CACHE_DIR="${NUMBA_CACHE_DIR:-/tmp/numba_cache}"
export MPLCONFIGDIR="${MPLCONFIGDIR:-/tmp/matplotlib}"

OUTPUT_DIR="${OUTPUT_DIR:-output}"
SED_OUTPUT_DIR="${SED_OUTPUT_DIR:-output_sed}"
DATASET_PREFIX="${DATASET_PREFIX:-}"
INITIAL_SEARCH_NAME="${INITIAL_SEARCH_NAME:-vis_pix}"

cd "$PROJECT_ROOT"

sample_path() {
    if [[ "$1" = /* ]]; then
        printf '%s/%s\n' "$1" "$SAMPLE"
    else
        printf '%s/%s/%s\n' "$PROJECT_ROOT" "$1" "$SAMPLE"
    fi
}

if [ -n "${SERSIC_OUTPUT_DIR:-}" ]; then
    SERSIC_OUTPUT_DIR="$SERSIC_OUTPUT_DIR"
elif [ -d "$(sample_path "$SED_OUTPUT_DIR")" ]; then
    SERSIC_OUTPUT_DIR="$SED_OUTPUT_DIR"
else
    SERSIC_OUTPUT_DIR="$OUTPUT_DIR"
fi

# `-` (not `:-`): an explicitly empty DATASET_NAMES_PATH disables the default
# selection rather than falling back to it. `all` / `none` do the same and
# survive `sbatch --export`, which is the safer way to ask for every lens.
DATASET_NAMES_PATH="${DATASET_NAMES_PATH-$(sample_path "$SERSIC_OUTPUT_DIR")}"
case "$DATASET_NAMES_PATH" in
    all|none) DATASET_NAMES_PATH="" ;;
esac
SELECTION_ARGS=()
if [ -n "$DATASET_NAMES_PATH" ]; then
    SELECTION_ARGS+=("--dataset_names_path=$DATASET_NAMES_PATH")
    echo "==> lens selection: child directories of $DATASET_NAMES_PATH"
else
    echo "==> lens selection: every lens under $OUTPUT_DIR/$SAMPLE"
fi

TAR_TO="${TAR_TO:-}"
TAR_ARGS=()
if [ -n "$TAR_TO" ]; then
    TAR_ARGS+=("--tar_to=$TAR_TO")
fi

mkdir -p "$INSPECT_DIR"

echo "==> [1/10] inspection PNGs (scripts/tools/build_inspect.py)"
python "$PROJECT_ROOT/scripts/tools/build_inspect.py" \
    --sample="$SAMPLE" \
    --output_path="$OUTPUT_DIR" \
    --sersic_output_path="$SERSIC_OUTPUT_DIR" \
    --initial_search_name="$INITIAL_SEARCH_NAME" \
    --inspect_dir="$INSPECT_DIR" \
    --dataset_prefix="$DATASET_PREFIX" \
    "${SELECTION_ARGS[@]}" \
    "${TAR_ARGS[@]}"

echo "==> [2/10] Sersic multi-band deblended FITS (catalogue/scripts/deblending.py)"
python "$PROJECT_ROOT/catalogue/scripts/deblending.py" \
    --sample="$SAMPLE" \
    --output_path="$SERSIC_OUTPUT_DIR" \
    --inspect_dir="$INSPECT_DIR" \
    "${SELECTION_ARGS[@]}"

echo "==> [2/10] $INITIAL_SEARCH_NAME deblended FITS (catalogue/scripts/deblending.py)"
python "$PROJECT_ROOT/catalogue/scripts/deblending.py" \
    --sample="$SAMPLE" \
    --output_path="$OUTPUT_DIR" \
    --inspect_dir="$INSPECT_DIR" \
    --unique_tag=initial_lens_model \
    --search_name="$INITIAL_SEARCH_NAME" \
    --product_prefix="${INITIAL_SEARCH_NAME}_" \
    "${SELECTION_ARGS[@]}"

echo "==> [3/10] lens mass maps (catalogue/scripts/lens_mass_maps.py)"
python "$PROJECT_ROOT/catalogue/scripts/lens_mass_maps.py" \
    --sample="$SAMPLE" \
    --output_path="$OUTPUT_DIR" \
    --inspect_dir="$INSPECT_DIR" \
    --search_name="$INITIAL_SEARCH_NAME" \
    "${SELECTION_ARGS[@]}"

echo "==> [4/10] lens mass CSV (catalogue/scripts/lens_mass.py)"
python "$PROJECT_ROOT/catalogue/scripts/lens_mass.py" \
    --sample="$SAMPLE" \
    --output_path="$OUTPUT_DIR" \
    --inspect_dir="$INSPECT_DIR" \
    --search_name="$INITIAL_SEARCH_NAME" \
    "${SELECTION_ARGS[@]}"

echo "==> [5/10] lens Sersic CSV (catalogue/scripts/lens_sersic.py)"
python "$PROJECT_ROOT/catalogue/scripts/lens_sersic.py" \
    --sample="$SAMPLE" \
    --output_path="$SERSIC_OUTPUT_DIR" \
    --inspect_dir="$INSPECT_DIR" \
    "${SELECTION_ARGS[@]}"

echo "==> [6/10] source Sersic CSV (catalogue/scripts/source_sersic.py)"
python "$PROJECT_ROOT/catalogue/scripts/source_sersic.py" \
    --sample="$SAMPLE" \
    --output_path="$SERSIC_OUTPUT_DIR" \
    --inspect_dir="$INSPECT_DIR" \
    "${SELECTION_ARGS[@]}"

echo "==> [7/10] Witt-Wynne SIEP projection (catalogue/scripts/witt_wynne.py)"
python "$PROJECT_ROOT/catalogue/scripts/witt_wynne.py" \
    --sample="$SAMPLE" \
    --output_path="$OUTPUT_DIR" \
    --inspect_dir="$INSPECT_DIR" \
    --search_name="$INITIAL_SEARCH_NAME" \
    "${SELECTION_ARGS[@]}"

# Stages 8-10 read the multi-band SED tree. Set SKIP_SED=1 to refresh only the
# stable products while SED jobs are still running.
SED_OUTPUT_PATH="${PROJECT_ROOT}/${SED_OUTPUT_DIR}"
if [ "${SKIP_SED:-0}" = "1" ]; then
    echo "==> [8/10,9/10,10/10] skipped — SKIP_SED=1"
elif [ -d "$SED_OUTPUT_PATH/$SAMPLE" ]; then
    echo "==> [8/10] multi-wavelength PNG (catalogue/scripts/multi_wavelength.py)"
    python "$PROJECT_ROOT/catalogue/scripts/multi_wavelength.py" \
        --sample="$SAMPLE" \
        --output_path="$SED_OUTPUT_DIR" \
        --inspect_dir="$INSPECT_DIR" \
        "${SELECTION_ARGS[@]}"

    echo "==> [9/10] magnitudes CSV (catalogue/scripts/magnitudes.py)"
    python "$PROJECT_ROOT/catalogue/scripts/magnitudes.py" \
        --sample="$SAMPLE" \
        --output_path="$SED_OUTPUT_DIR" \
        --inspect_dir="$INSPECT_DIR" \
        "${SELECTION_ARGS[@]}"

    echo "==> [10/10] astrometric offsets CSV (catalogue/scripts/astrometric_offsets.py)"
    python "$PROJECT_ROOT/catalogue/scripts/astrometric_offsets.py" \
        --sample="$SAMPLE" \
        --output_path="$SED_OUTPUT_DIR" \
        --inspect_dir="$INSPECT_DIR" \
        "${SELECTION_ARGS[@]}"
else
    echo "==> [8/10,9/10,10/10] skipped — no $SED_OUTPUT_PATH/$SAMPLE/ (no SED runs yet)"
fi

echo ""
echo "Done. Bundle at: $INSPECT_DIR"
echo "  $(ls "$INSPECT_DIR" | wc -l) entries"

# Archive only when explicitly enabled — a full DR1 bundle is tens of GB, so an
# incremental refresh should not rebuild the tarball.
if [ "${CREATE_ARCHIVE:-1}" = "1" ]; then
    TAR_NAME="${INSPECT_DIR//\//_}.tar.gz"
    echo "==> Archiving -> $TAR_NAME"
    tar czf "$TAR_NAME" "$INSPECT_DIR/"
    echo "  $(ls -lh "$TAR_NAME" | awk '{print $5}')  $TAR_NAME"
else
    echo "==> Archive skipped — CREATE_ARCHIVE=0"
fi
