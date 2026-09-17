"""
Euclid Pipeline: The Four Sersic Variants, Compared
===================================================

Read the four ``lens_sersic_<variant>.csv`` scrapes that the ``euclid_sersics``
re-fit produced and lay the lens-light Sersic index ``n`` of each variant beside
the others, so a human can see which variant moved it and by how much.

The question behind the whole exercise is the June DR1 catalogue's: the lens
Sersic index piles up at the prior's upper edge. 67 % of the core 100 lenses came
back with ``n > 4.5`` against a ``Uniform(0.8, 5.0)`` prior, which is the shape a
posterior has when the prior stopped it rather than the data did — but it is also
the shape a posterior has when the lens light genuinely is a de Vaucouleurs-like
cusp that a single Sersic can only reach by running ``n`` up. Those two readings
have the same catalogue, so the catalogue cannot separate them; four re-fits of
the same 100 lenses can.

__The Four Variants, And What Each One Asks__

``scripts/sersic_lens_model.py --variant <name>`` runs the Sersic stage four ways
over the same data:

**baseline** — the unmodified model on the new data. It asks nothing new: it is
the control that says whether this re-fit reproduces June at all. If baseline's
own ``n`` distribution does not look like June's, every other variant is being
compared against a moved goalpost and the run is a re-fit of a different thing.

**wide_n** — the lens Sersic-index prior widened from the configured
``Uniform(0.8, 5.0)`` (``config/priors/light/linear/sersic.yaml``) to
``Uniform(0.5, 10.0)``. This is the separating experiment. If the pile-up was the
prior edge, the posteriors walk straight past 5.0 when the fence is moved; if the
data wanted ``n`` near 5, they stay near 5 with the fence nowhere near them. The
reading is therefore the *fraction past the old edge*, and it comes with its own
control — the fraction piled at the **new** edge (``n > 9.5``), because a
distribution that simply re-piles at 10 has told you the prior is still the thing
holding the parameter, just further out.

**central_noise** — the same data and the same model as baseline, with the noise
map inflated in a Gaussian bowl at the lens centre,
``1 + 9 exp(-r² / 2 (0.17″)²)``. Nothing about the model changes; the fit is
simply told to stop believing the innermost pixels. A Sersic index is most
strongly constrained by exactly those pixels, so if a handful of central pixels
are driving ``n`` up, de-weighting them brings it down. This is the "is it a few
pixels?" reading, and it is a *paired* one: the same lens, fitted twice, is a far
sharper instrument than two population medians.

**sersic_point** — the lens gains a compact 5-Gaussian MGE ``point`` component,
so an unresolved nucleus has somewhere to go other than the Sersic cusp. If the
high indices are a single Sersic doing a nucleus's job, giving the nucleus its own
component should release the Sersic back down.

__What A Reading Here Is, And What It Is Not__

This script prints numbers beside thresholds. It does not print a verdict, and
that is deliberate rather than an omission. Each of the four questions above is a
science judgement about whether a shift is the shift that was predicted, over a
sample of 100 lenses with real scatter; a single word printed by a CSV reader
would be read as that judgement having been made. So the witness table carries
the reading, the threshold it is to be read against, and nothing else — the human
does the comparison.

The four thresholds themselves are **transcribed here for this script** from the
plan; they are to be confirmed against the plan page "Euclid Sersics Plan" rev 3
before a reading is quoted anywhere. They live in one constant (``WITNESSES``) so
that confirming or changing one is a one-line edit.

__What The Scrape Does Not Carry__

``catalogue/scripts/lens_sersic.py`` writes the **six** free parameters of the
lens's ``lp_linear.Sersic`` — ``centre_0``, ``centre_1``, ``ell_comps_0``,
``ell_comps_1``, ``effective_radius``, ``sersic_index`` — each in five flavours
(median, lower/upper 1σ, lower/upper 3σ). It writes no ``intensity``, because a
linear light profile's intensity is solved by linear algebra at every likelihood
evaluation and never enters the non-linear samples.

So the one number the ``sersic_point`` variant most obviously wants — the
fraction of the lens flux that landed in the nucleus component rather than in the
Sersic — **is not in these CSVs and is not computed here**. The report says so
rather than approximating it. Getting it means a separate scrape of the
``point`` component's flux, or the calibrated per-band fluxes in
``magnitudes.csv``; it is out of scope for this comparison.

__The Inner Join, And Why Losses Are Named__

A variant can be short of lenses: a search that did not write a ``.completed``
marker never reaches the CSV, and a cell whose ``add_variable`` argument missed is
written *blank* rather than raised. Paired deltas are therefore computed over the
**inner join** — the lenses every requested variant has a parseable row for — so
that a median Δn is 100 lenses fitted twice and not 100 lenses against 93.

Every lens the join loses is named in the report, per variant, together with every
row whose ``sersic_index`` or ``effective_radius`` cell would not parse. A
silently smaller sample is the one way all four readings come out looking
tidier than they are.

The per-variant *summary* numbers (median, fractions above the thresholds) are
deliberately computed over **all** parseable rows of that variant, not over the
join: they are that variant's own distribution, and clipping them to the join
would hide the very shortfall the dropped-lens section reports.

No fit is run and no PyAuto library is imported: this reads CSVs.

Usage
-----
Produce the four inputs first — one scrape per variant, each writing a
``lens_sersic.csv`` that you copy to a per-variant name in one directory::

    for v in baseline wide_n central_noise sersic_point; do
        python scripts/sersic_lens_model.py --sample=euclid_sersics --variant=$v
        python catalogue/scripts/lens_sersic.py \
            --sample=euclid_sersics \
            --unique_tag=sersic_lens_model_$v \
            --inspect_dir=inspect/euclid_sersics_$v
        cp inspect/euclid_sersics_$v/lens_sersic.csv \
           inspect/sersic_variants_in/lens_sersic_$v.csv
    done

Then compare them::

    python scripts/analysis/sersic_variants.py inspect/sersic_variants_in

    python scripts/analysis/sersic_variants.py inspect/sersic_variants_in \
        --lens-map ../euclid_sersics/sample/lens_map.csv \
        --out inspect/sersic_variants

    python scripts/analysis/sersic_variants.py DIR --variants baseline,wide_n
"""

import argparse
import csv
import math
import statistics
import sys
from pathlib import Path

import numpy as np

# The four Sersic-stage variants of `scripts/sersic_lens_model.py --variant`
# (PR #75), in the order every table and every histogram panel uses.
VARIANTS = ("baseline", "wide_n", "central_noise", "sersic_point")

# The control every paired delta is taken against.
BASELINE = "baseline"

# The configured lens Sersic-index prior: `Uniform(0.8, 5.0)` from
# `config/priors/light/linear/sersic.yaml` (`Sersic.sersic_index`).
CONFIG_N_LOWER = 0.8
CONFIG_N_UPPER = 5.0

# The widened prior the `wide_n` variant substitutes:
# `Uniform(0.5, 10.0)` in `scripts/sersic_lens_model.py`.
WIDE_N_LOWER = 0.5
WIDE_N_UPPER = 10.0

# Where the `n` distribution is counted. 4.5 is the June pile-up threshold,
# 4.9 is "hard against the configured edge", 9.5 is "hard against the widened
# edge" and is the control on `wide_n` re-piling at its new fence.
N_THRESHOLDS = (4.5, 4.9, 9.5)

# Reported for `wide_n` alone: the old prior edge, which is an interior point of
# that variant's prior and a boundary of nobody else's, so `n > 5.0` is only a
# meaningful count where the fence has moved.
WIDE_N_EXTRA_THRESHOLD = 5.0

# The June DR1 reference quoted in the plan: 67 % of the core 100 lenses came
# back above `n = 4.5`. Printed beside baseline's own fraction, never subtracted
# from it — the two are different sample selections.
JUNE_FRACTION_ABOVE_4P5 = 0.67

# Histogram bins shared by every panel, so the four distributions are read
# against one another and not against four different binnings: 0.5 to 10.0 (the
# widened prior's full support) in steps of 0.25.
HISTOGRAM_BINS = np.linspace(0.5, 10.0, 39)

# The four readings, each `(id, question, threshold_text)`.
#
# THE THRESHOLDS BELOW ARE TRANSCRIBED for this script and are to be CONFIRMED
# against the plan page "Euclid Sersics Plan" rev 3 before any reading is quoted.
# They are gathered here so that confirming or revising one is a one-line edit,
# and they are rendered as *text beside a number* — this module prints no verdict
# word, see "__What A Reading Here Is__" in the module docstring.
WITNESSES = (
    (
        "W1",
        "Does baseline reproduce June? median(baseline n − June n) over the "
        "joined lenses carrying a lens_map row",
        "|Δn| ≤ 0.5",
    ),
    (
        "W2",
        "Does the prior edge cause the pile-up? wide_n fraction with n > 5.0 "
        "(past the configured edge)",
        "≥ 0.5",
    ),
    (
        "W3",
        "Do the central pixels drive it? median paired Δn "
        "(central_noise − baseline)",
        "≤ −0.5",
    ),
    (
        "W4",
        "Does a nucleus component absorb it? median paired Δn "
        "(sersic_point − baseline)",
        "≤ −0.5",
    ),
)

# The two columns every reading is built from. A row missing either is
# unparseable and is named in the report rather than dropped.
REQUIRED_COLUMNS = ("sersic_index", "effective_radius")

# The row-identity column `catalogue/scripts/lens_sersic.py` writes.
LENS_NAME_COLUMN = "lens_name"

# The `sample/lens_map.csv` columns this script needs. `sep1_tile` is the tile
# name, which is what `lens_sersic.csv` carries as `lens_name`.
LENS_MAP_KEY_COLUMN = "sep1_tile"
LENS_MAP_VALUE_COLUMN = "june_sersic_index"

# The percentile band every paired delta is reported with: the 16th and 84th,
# which is the 1σ-equivalent spread of the *population* of deltas (not of any
# one lens's posterior).
DELTA_PERCENTILES = (16, 84)


def as_float(value):
    """
    ``float(value)`` or ``None`` for a blank, non-numeric or NaN cell.

    A blank cell in a catalogue scrape is the shape of the ``latent.`` prefix
    regression, so it is never silently a zero: ``None`` propagates up to
    ``read_scrape``, which names the row.
    """
    if value is None:
        return None
    text = str(value).strip()
    if text == "":
        return None
    try:
        result = float(text)
    except ValueError:
        return None
    return None if math.isnan(result) else result


def read_scrape(path):
    """
    One ``lens_sersic_<variant>.csv``, read as ``(rows, unparseable)``.

    ``rows`` is ``{lens_name: {"lens_name": str, "sersic_index": float,
    "effective_radius": float}}`` — only the two columns every reading here is
    built from are coerced, because those are the only ones compared and a
    surprise in any other column is `scripts/tools/compare_catalogues.py`'s
    business, not this script's.

    ``unparseable`` is the sorted list of ``lens_name``s whose ``sersic_index``
    or ``effective_radius`` cell was blank or non-numeric. Those rows are
    **returned, not dropped**: the report names them, because a variant that
    quietly shrank is the one way all four readings come out tidier than the data
    are.

    A repeated ``lens_name`` raises ``ValueError`` naming it. The producer writes
    one row per lens, so a duplicate means two results trees were concatenated or
    a tile was scraped twice, and silently keeping the last would make the two
    runs indistinguishable.
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"no such scrape: {path}")

    rows = {}
    unparseable = []

    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for raw in reader:
            lens_name = (raw.get(LENS_NAME_COLUMN) or "").strip()
            if lens_name == "":
                continue

            if lens_name in rows or lens_name in unparseable:
                raise ValueError(
                    f"duplicate lens_name '{lens_name}' in {path}: a scrape holds "
                    "one row per lens, so two results trees were concatenated or "
                    "a tile was scraped twice"
                )

            values = {column: as_float(raw.get(column)) for column in REQUIRED_COLUMNS}
            if any(value is None for value in values.values()):
                unparseable.append(lens_name)
                continue

            values[LENS_NAME_COLUMN] = lens_name
            rows[lens_name] = values

    return rows, sorted(unparseable)


def summarise(rows, thresholds=N_THRESHOLDS, extra_thresholds=()):
    """
    One variant's own distribution: ``{"n", "median_n", "median_r_eff",
    "fraction_above"}``.

    ``fraction_above`` is keyed by threshold and counts **strictly** above it
    (``n > t``), over every parseable row of that variant rather than over the
    inner join — see "__The Inner Join__" in the module docstring for why.
    ``extra_thresholds`` adds thresholds that are meaningful for this variant
    only (``5.0`` for ``wide_n``, whose prior edge moved).

    An empty variant gives ``n = 0`` and ``None`` medians rather than raising:
    a scrape of nothing is a finding the report should print.
    """
    indices = [row["sersic_index"] for row in rows.values()]
    radii = [row["effective_radius"] for row in rows.values()]

    all_thresholds = tuple(thresholds) + tuple(extra_thresholds)

    return {
        "n": len(indices),
        "median_n": statistics.median(indices) if indices else None,
        "median_r_eff": statistics.median(radii) if radii else None,
        "fraction_above": {
            threshold: (
                sum(1 for value in indices if value > threshold) / len(indices)
                if indices
                else None
            )
            for threshold in all_thresholds
        },
    }


def paired_deltas(rows_a, rows_b, lenses, column):
    """
    ``rows_a[lens][column] - rows_b[lens][column]`` over ``lenses``, summarised
    as ``{"n", "median", "p16", "p84"}``.

    Paired, per lens, because the same lens fitted twice is a far sharper
    instrument than two population medians: the lens-to-lens scatter in ``n`` is
    large and cancels in the difference. ``lenses`` is the inner join, so both
    sides are guaranteed present.

    The band is the 16th/84th percentile of the *population of deltas* under
    numpy's default linear interpolation — the spread of how differently the
    lenses responded, not any one lens's posterior width.
    """
    deltas = [
        rows_a[lens][column] - rows_b[lens][column]
        for lens in lenses
        if lens in rows_a and lens in rows_b
    ]

    if not deltas:
        return {"n": 0, "median": None, "p16": None, "p84": None}

    array = np.asarray(deltas, dtype=float)
    p16, p84 = np.percentile(array, list(DELTA_PERCENTILES))

    return {
        "n": int(array.size),
        "median": float(np.median(array)),
        "p16": float(p16),
        "p84": float(p84),
    }


def load_variants(directory, variants=VARIANTS):
    """
    Every requested variant's scrape, as one dict.

    Keys:

    ``directory``     the directory the scrapes were read from (``Path``)
    ``variants``      the variant names, in the order given
    ``paths``         ``{variant: Path}`` of the file each was read from
    ``rows``          ``{variant: read_scrape's rows}``
    ``row_counts``    ``{variant: number of rows in the file}`` — parseable plus
                      unparseable, so the report can show the shortfall
    ``unparseable``   ``{variant: [lens_name, ...]}``
    ``summaries``     ``{variant: summarise(...)}``, with ``5.0`` added for
                      ``wide_n``
    ``joined``        the inner join: lenses every requested variant has a
                      parseable row for, sorted
    ``union``         every lens any requested variant has a parseable row for,
                      sorted
    ``dropped``       ``{variant: [lens_name, ...]}`` — in the union, absent from
                      this variant

    A missing ``lens_sersic_<variant>.csv`` raises ``FileNotFoundError`` naming
    the path it looked for *and* listing the variant files that are present,
    because the ordinary cause is a scrape copied under the wrong name and the
    listing is the answer to "then what did I copy?".

    ``baseline`` must be among the variants: every paired delta and the June
    comparison are taken against it, so a set without it is not this comparison.
    """
    directory = Path(directory)
    variants = tuple(variants)

    if BASELINE not in variants:
        raise ValueError(
            f"'{BASELINE}' must be among the variants (got {', '.join(variants)}): "
            "every paired delta and the June comparison are taken against it"
        )

    present = sorted(path.name for path in directory.glob("lens_sersic_*.csv"))

    paths = {}
    for variant in variants:
        path = directory / f"lens_sersic_{variant}.csv"
        if not path.is_file():
            raise FileNotFoundError(
                f"no scrape for variant '{variant}' at {path}; "
                f"present in {directory}: "
                + (", ".join(present) if present else "no lens_sersic_*.csv at all")
            )
        paths[variant] = path

    rows = {}
    unparseable = {}
    row_counts = {}
    for variant, path in paths.items():
        variant_rows, variant_unparseable = read_scrape(path)
        rows[variant] = variant_rows
        unparseable[variant] = variant_unparseable
        row_counts[variant] = len(variant_rows) + len(variant_unparseable)

    summaries = {
        variant: summarise(
            rows[variant],
            extra_thresholds=(
                (WIDE_N_EXTRA_THRESHOLD,) if variant == "wide_n" else ()
            ),
        )
        for variant in variants
    }

    keysets = [set(rows[variant]) for variant in variants]
    joined = sorted(set.intersection(*keysets)) if keysets else []
    union = sorted(set.union(*keysets)) if keysets else []

    dropped = {
        variant: sorted(set(union) - set(rows[variant])) for variant in variants
    }

    return {
        "directory": directory,
        "variants": variants,
        "paths": paths,
        "rows": rows,
        "row_counts": row_counts,
        "unparseable": unparseable,
        "summaries": summaries,
        "joined": joined,
        "union": union,
        "dropped": dropped,
    }


def load_lens_map(path):
    """
    ``{sep1_tile: june_sersic_index}`` from the science clone's
    ``sample/lens_map.csv``.

    That file is the sample definition — ``euclid_object_id``, ``sep1_tile``,
    ``batch_zip``, ``offset_arcsec``, ``total_valid_votes``,
    ``june_sersic_index`` — and ``sep1_tile`` is the tile name, which is exactly
    what ``lens_sersic.csv`` carries as ``lens_name``. That is the join.

    A row whose ``june_sersic_index`` will not parse is simply not in the map, so
    it lands in the report's "joined lenses with no lens_map row" list rather
    than in a comparison against a blank.
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"no such lens map: {path}")

    mapping = {}
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for raw in reader:
            tile = (raw.get(LENS_MAP_KEY_COLUMN) or "").strip()
            june = as_float(raw.get(LENS_MAP_VALUE_COLUMN))
            if tile == "" or june is None:
                continue
            mapping[tile] = june

    return mapping


def june_comparison(variants_data, lens_map):
    """
    ``baseline n − June n`` over the joined lenses that carry a ``lens_map`` row.

    Returns ``{"n", "median", "p16", "p84", "missing"}`` where ``missing`` is the
    sorted joined lenses the map has never heard of — named in the report,
    because a shrinking overlap quietly changes what W1 is a median of.
    """
    joined = variants_data["joined"]
    baseline_rows = variants_data["rows"][BASELINE]

    matched = [lens for lens in joined if lens in lens_map]
    missing = [lens for lens in joined if lens not in lens_map]

    june_rows = {lens: {"sersic_index": lens_map[lens]} for lens in matched}
    result = paired_deltas(baseline_rows, june_rows, matched, "sersic_index")
    result["missing"] = missing
    return result


def witness_table(variants_data, lens_map=None):
    """
    The four readings W1–W4 as ``[(id, question, reading, threshold_text)]``.

    ``reading`` is a **number** (or ``"n/a (no --lens-map)"`` for W1 when no map
    was given), and ``threshold_text`` is the text it is to be read against. No
    verdict is formed here and none is printed: see "__What A Reading Here Is__"
    in the module docstring. The questions and the thresholds come from
    ``WITNESSES``, one edit per revision.
    """
    questions = {identifier: (question, threshold) for identifier, question, threshold in WITNESSES}

    joined = variants_data["joined"]
    rows = variants_data["rows"]
    summaries = variants_data["summaries"]

    def reading_w1():
        if lens_map is None:
            return "n/a (no --lens-map)"
        return june_comparison(variants_data, lens_map)["median"]

    def reading_w2():
        if "wide_n" not in rows:
            return None
        return summaries["wide_n"]["fraction_above"].get(WIDE_N_EXTRA_THRESHOLD)

    def paired_median(variant):
        if variant not in rows:
            return None
        return paired_deltas(rows[variant], rows[BASELINE], joined, "sersic_index")["median"]

    readings = {
        "W1": reading_w1(),
        "W2": reading_w2(),
        "W3": paired_median("central_noise"),
        "W4": paired_median("sersic_point"),
    }

    return [
        (identifier, questions[identifier][0], readings[identifier], questions[identifier][1])
        for identifier, _question, _threshold in WITNESSES
    ]


def witness_notes(variants_data, lens_map=None):
    """
    The two second readings that belong beside a witness but are not themselves
    witnesses, rendered as sub-lines under the table.

    W1's is baseline's own fraction above 4.5 beside the June reference
    ``JUNE_FRACTION_ABOVE_4P5`` — the population-level version of the same
    question, which the paired median cannot see. W2's is the fraction piled at
    the *new* edge: a ``wide_n`` distribution that simply re-piles at 10 has told
    you the prior is still what holds ``n``.
    """
    summaries = variants_data["summaries"]
    notes = []

    baseline_fraction = summaries[BASELINE]["fraction_above"].get(4.5)
    notes.append(
        f"_W1, second reading: baseline fraction n > 4.5 = "
        f"{format_number(baseline_fraction)}, beside the June reference "
        f"{format_number(JUNE_FRACTION_ABOVE_4P5)} "
        f"({'lens_map joined' if lens_map is not None else 'no --lens-map given'})._"
    )

    if "wide_n" in summaries:
        # A blank line between them, or markdown runs the two italic sub-lines
        # together into one paragraph.
        notes.append("")
        notes.append(
            "_W2, second reading: wide_n fraction n > 9.5 = "
            f"{format_number(summaries['wide_n']['fraction_above'].get(9.5))} "
            "— the pile-up at the widened prior's own edge._"
        )

    return notes


def markdown_table(header, rows):
    """
    A markdown table, or a single italic line when there are no rows — an empty
    table renders as a header with nothing under it, which reads as a bug.
    """
    if not rows:
        return ["_no rows_"]

    def cell(value):
        # A bare `|` in a cell splits the row into extra columns; the W1
        # threshold is literally `|Δn| ≤ 0.5`, so escaping is not optional.
        return str(value).replace("|", "\\|")

    lines = [
        "| " + " | ".join(cell(name) for name in header) + " |",
        "|" + "|".join("---" for _ in header) + "|",
    ]
    for row in rows:
        lines.append("| " + " | ".join(cell(value) for value in row) + " |")
    return lines


def format_number(value, digits=4):
    """
    A number for a report cell; ``n/a`` for a missing one. A string is returned
    unchanged, so a reading that is deliberately textual (``"n/a (no
    --lens-map)"``) renders as written.
    """
    if value is None:
        return "n/a"
    if isinstance(value, str):
        return value
    return f"{value:.{digits}g}"


def _threshold_label(threshold):
    """
    ``n>4.5`` for a table header cell.
    """
    return f"n>{threshold:.1f}"


def render_report(variants_data, lens_map=None, out_dir=None):
    """
    The whole markdown report, as one string.

    Order is the order the questions are asked in: what was read, what each
    variant's own distribution looks like, how each variant moved each lens
    against baseline, how baseline sits against June, the four readings, what the
    inner join cost, and what the scrape does not carry.
    """
    variants = variants_data["variants"]
    rows = variants_data["rows"]
    summaries = variants_data["summaries"]
    joined = variants_data["joined"]

    lines = [
        "# Sersic variants: the four re-fits compared",
        "",
        "The lens-light Sersic index `n` under the four variants of "
        "`scripts/sersic_lens_model.py --variant`. Readings are numbers beside "
        "the threshold they are to be read against; no verdict is formed here.",
        "",
        "## Inputs",
        "",
        f"- **Directory**: `{variants_data['directory']}`",
        f"- **Variants**: {', '.join(variants)}",
        f"- **Lens map**: "
        + (f"{len(lens_map)} rows" if lens_map is not None else "not given (`--lens-map`)"),
        f"- **Inner join**: {len(joined)} lenses present in every variant",
        "",
    ]
    lines += markdown_table(
        ["variant", "file", "rows in file", "parseable rows", "unparseable rows"],
        [
            [
                variant,
                f"`{variants_data['paths'][variant].name}`",
                variants_data["row_counts"][variant],
                len(rows[variant]),
                len(variants_data["unparseable"][variant]),
            ]
            for variant in variants
        ],
    )

    lines += [
        "",
        "## Per-variant summary",
        "",
        "Each variant's own distribution, over **all** its parseable rows rather "
        "than over the inner join — clipping these to the join would hide the "
        "shortfall the dropped-lens section below reports. Fractions count "
        "strictly above the threshold.",
        "",
    ]
    summary_header = (
        ["variant", "N rows", "N joined", "median n", "median R_eff"]
        + [f"frac {_threshold_label(threshold)}" for threshold in N_THRESHOLDS]
        + [f"frac {_threshold_label(WIDE_N_EXTRA_THRESHOLD)} (wide_n)"]
    )
    summary_rows = []
    for variant in variants:
        summary = summaries[variant]
        row = [
            variant,
            summary["n"],
            len(joined),
            format_number(summary["median_n"]),
            format_number(summary["median_r_eff"]),
        ]
        row += [
            format_number(summary["fraction_above"].get(threshold))
            for threshold in N_THRESHOLDS
        ]
        if WIDE_N_EXTRA_THRESHOLD in summary["fraction_above"]:
            row.append(
                format_number(summary["fraction_above"][WIDE_N_EXTRA_THRESHOLD])
            )
        else:
            row.append("—")
        summary_rows.append(row)
    lines += markdown_table(summary_header, summary_rows)

    lines += [
        "",
        f"The configured prior is `Uniform({CONFIG_N_LOWER:g}, {CONFIG_N_UPPER:g})` "
        "(`config/priors/light/linear/sersic.yaml`); `wide_n` substitutes "
        f"`Uniform({WIDE_N_LOWER:g}, {WIDE_N_UPPER:g})`. "
        f"`frac {_threshold_label(WIDE_N_EXTRA_THRESHOLD)}` is reported for "
        "`wide_n` alone, because 5.0 is an interior point of its prior and the "
        "hard edge of everyone else's.",
        "",
        "## Paired deltas against baseline",
        "",
        f"Per lens, over the {len(joined)} lenses of the inner join: the same lens "
        "fitted twice, which cancels the large lens-to-lens scatter in `n`. The "
        "band is the 16th/84th percentile of the population of deltas.",
        "",
    ]

    for column, label in (
        ("sersic_index", "Δn (sersic_index)"),
        ("effective_radius", "ΔR_eff (effective_radius)"),
    ):
        delta_rows = []
        for variant in variants:
            if variant == BASELINE:
                continue
            delta = paired_deltas(rows[variant], rows[BASELINE], joined, column)
            delta_rows.append(
                [
                    variant,
                    delta["n"],
                    format_number(delta["median"]),
                    format_number(delta["p16"]),
                    format_number(delta["p84"]),
                ]
            )
        lines += [f"### {label}", ""]
        lines += markdown_table(
            ["variant", "N", "median Δ", "16 %", "84 %"], delta_rows
        )
        lines += [""]

    if lens_map is not None:
        comparison = june_comparison(variants_data, lens_map)
        lines += [
            "## June versus baseline",
            "",
            "`baseline n − June n`, per lens, over the joined lenses carrying a "
            "`sample/lens_map.csv` row (`sep1_tile` joined on `lens_name`). This "
            "is the control on the whole exercise: a baseline that does not "
            "reproduce June means every other variant is being compared against "
            "a moved goalpost.",
            "",
        ]
        lines += markdown_table(
            ["quantity", "value"],
            [
                ["lenses joined and mapped", comparison["n"]],
                ["median Δn", format_number(comparison["median"])],
                ["16 %", format_number(comparison["p16"])],
                ["84 %", format_number(comparison["p84"])],
                ["joined lenses with no lens_map row", len(comparison["missing"])],
            ],
        )
        if comparison["missing"]:
            lines += [""]
            lines += markdown_table(
                ["joined lens with no lens_map row"],
                [[lens] for lens in comparison["missing"]],
            )
        lines += [""]
    else:
        lines += [
            "## June versus baseline",
            "",
            "_Not computed: no `--lens-map` given, so there is no "
            "`june_sersic_index` to difference against._",
            "",
        ]

    lines += ["## Witness readings", ""]
    lines += markdown_table(
        ["W", "question", "reading", "threshold"],
        [
            [identifier, question, format_number(reading), threshold]
            for identifier, question, reading, threshold in witness_table(
                variants_data, lens_map=lens_map
            )
        ],
    )
    lines += [""]
    lines += witness_notes(variants_data, lens_map=lens_map)
    lines += [
        "",
        "_The thresholds above are transcribed for this script and are to be "
        'confirmed against the plan page "Euclid Sersics Plan" rev 3 before a '
        "reading is quoted. The reading and the threshold are printed side by "
        "side on purpose: each of the four questions is a science judgement over "
        "a sample with real scatter, and a word printed by a CSV reader would be "
        "read as that judgement having been made._",
        "",
        "## Lenses dropped by the inner join",
        "",
        f"The union of all variants holds {len(variants_data['union'])} lenses "
        f"and the inner join {len(joined)}. Every loss is named: a variant that "
        "quietly shrank is the one way all four readings come out tidier than the "
        "data are.",
        "",
    ]

    any_loss = False
    for variant in variants:
        dropped = variants_data["dropped"][variant]
        unparseable = variants_data["unparseable"][variant]
        if not dropped and not unparseable:
            continue
        any_loss = True
        lines += [f"### {variant}", ""]
        lines += markdown_table(
            ["lens", "why"],
            [
                [lens, "no row in this variant's scrape"]
                for lens in dropped
                if lens not in set(unparseable)
            ]
            + [
                [lens, "row present, sersic_index/effective_radius would not parse"]
                for lens in unparseable
            ],
        )
        lines += [""]

    if not any_loss:
        lines += [
            "_No lens was dropped and no row was unparseable: every variant "
            "carries every lens._",
            "",
        ]

    lines += [
        "## What this comparison cannot answer",
        "",
        "The `sersic_point` **nucleus flux fraction** is not in these CSVs and is "
        "not computed here. `catalogue/scripts/lens_sersic.py` scrapes the six "
        "free parameters of the lens's `lp_linear.Sersic` — `centre_0`, "
        "`centre_1`, `ell_comps_0`, `ell_comps_1`, `effective_radius`, "
        "`sersic_index` — and no `intensity`: a linear light profile's intensity "
        "is solved by linear algebra at every likelihood evaluation and never "
        "enters the non-linear samples. So how much light the `point` component "
        "took rather than the Sersic needs a separate scrape of that component, "
        "or the calibrated per-band fluxes in `magnitudes.csv`. W4 above reads "
        "the Sersic index's response, which is the question this scrape can "
        "answer.",
    ]

    if out_dir is not None:
        lines += ["", f"_Artefacts written under `{out_dir}`._"]

    return "\n".join(lines)


def write_histograms(variants_data, path):
    """
    One panel per variant, shared bins, written to ``path``.

    matplotlib is imported **here** rather than at module level, and the Agg
    backend is selected before ``pyplot`` is touched: every other function in
    this module is a pure CSV/numpy reading, and a script that pulls in a GUI
    toolkit to compute a median is a script that cannot run on the cluster.

    Every panel carries the configured prior's edges, so the four distributions
    are read against the same fence; the ``wide_n`` panel carries its own widened
    edges dashed on top, which is what makes "walked past the old edge" and
    "re-piled at the new one" visible in one glance.
    """
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    variants = variants_data["variants"]
    rows = variants_data["rows"]
    summaries = variants_data["summaries"]

    columns = 2
    panel_rows = max(1, math.ceil(len(variants) / columns))
    fig, axes = plt.subplots(
        panel_rows, columns, figsize=(11.0, 4.0 * panel_rows), squeeze=False
    )
    flat = [axis for row in axes for axis in row]

    for axis, variant in zip(flat, variants):
        indices = [row["sersic_index"] for row in rows[variant].values()]
        axis.hist(indices, bins=HISTOGRAM_BINS, color="#4477aa", edgecolor="white")

        axis.axvline(
            CONFIG_N_LOWER,
            color="#cc3311",
            linewidth=1.2,
            label=f"config prior {CONFIG_N_LOWER:g}–{CONFIG_N_UPPER:g}",
        )
        axis.axvline(CONFIG_N_UPPER, color="#cc3311", linewidth=1.2)

        if variant == "wide_n":
            axis.axvline(
                WIDE_N_LOWER,
                color="#228833",
                linewidth=1.2,
                linestyle="--",
                label=f"wide_n prior {WIDE_N_LOWER:g}–{WIDE_N_UPPER:g}",
            )
            axis.axvline(
                WIDE_N_UPPER, color="#228833", linewidth=1.2, linestyle="--"
            )

        median = summaries[variant]["median_n"]
        median_text = "n/a" if median is None else f"{median:.2f}"
        axis.set_title(
            f"{variant}  N={summaries[variant]['n']}  median n={median_text}"
        )
        axis.set_xlabel("Sersic index n")
        axis.set_ylabel("lenses")
        # A quarter-bin of air either side: the widened prior's edges are the
        # first and last bin edge, so without it those two dashed lines sit
        # under the axes frame and the legend names a line nobody can see.
        margin = float(HISTOGRAM_BINS[1] - HISTOGRAM_BINS[0])
        axis.set_xlim(
            float(HISTOGRAM_BINS[0]) - margin, float(HISTOGRAM_BINS[-1]) + margin
        )
        axis.legend(loc="upper left", fontsize="small")

    for axis in flat[len(variants) :]:
        axis.set_axis_off()

    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def parse_args(argv=None):
    """
    One directory of per-variant scrapes, an output directory, an optional lens
    map and an optional variant override.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Compare the four lens_sersic_<variant>.csv scrapes of the "
            "euclid_sersics re-fit: per-variant n distributions, paired deltas "
            "against baseline, June-vs-baseline, and the W1-W4 readings printed "
            "beside their thresholds."
        )
    )
    parser.add_argument(
        "directory",
        metavar="directory",
        help=(
            "Directory holding lens_sersic_<variant>.csv for each variant "
            "(one copy of each scrape, renamed)."
        ),
    )
    parser.add_argument(
        "--out",
        metavar="dir",
        default="inspect/sersic_variants",
        help=(
            "Directory for the markdown report and the histogram PNG. "
            "Default: inspect/sersic_variants (inspect/ is gitignored)."
        ),
    )
    parser.add_argument(
        "--lens-map",
        metavar="PATH",
        default=None,
        help=(
            "The science clone's sample/lens_map.csv, whose june_sersic_index "
            "column is the June reference W1 differences baseline against. "
            "Without it W1 reads n/a."
        ),
    )
    parser.add_argument(
        "--variants",
        metavar="a,b,c",
        default=None,
        help=(
            "Comma-separated variant override. Default: "
            + ",".join(VARIANTS)
            + ". 'baseline' is required in any set."
        ),
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    directory = Path(args.directory)
    if not directory.is_dir():
        raise SystemExit(f"ERROR: no such directory: {directory}")

    variants = VARIANTS
    if args.variants:
        variants = tuple(
            name.strip() for name in args.variants.split(",") if name.strip()
        )

    try:
        variants_data = load_variants(directory, variants=variants)
    except (FileNotFoundError, ValueError) as error:
        raise SystemExit(f"ERROR: {error}")

    lens_map = None
    if args.lens_map:
        try:
            lens_map = load_lens_map(args.lens_map)
        except FileNotFoundError as error:
            raise SystemExit(f"ERROR: {error}")

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    report = render_report(variants_data, lens_map=lens_map, out_dir=out_dir)
    print(report)

    report_path = out_dir / "sersic_variants.md"
    report_path.write_text(report + "\n")
    print(f"wrote {report_path}", file=sys.stderr)

    figure_path = out_dir / "sersic_variants.png"
    write_histograms(variants_data, figure_path)
    print(f"wrote {figure_path}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
