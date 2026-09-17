"""
The four-variant Sersic comparison's numbers.

``scripts/analysis/sersic_variants.py`` is what the ``euclid_sersics`` re-fit is
read through: four ``lens_sersic_<variant>.csv`` scrapes go in, and the numbers
that come out are the ones a human compares against the W1-W4 thresholds before
deciding why the lens Sersic index piles up at ``n = 5``. Nothing downstream
re-derives them, so a quiet arithmetic change here is a quiet change to the
science reading. This module pins every number the report prints.

The fixture is four synthetic CSVs written per test into ``tmp_path``: 20 tiles,
the real 32-column ``lens_sersic.csv`` header (asserted against
``tests/data/dr1_headers/lens_sersic.txt``), and ``sersic_index`` /
``effective_radius`` values chosen so every expected number is hand-computable —
``wide_n`` is ``baseline + 1.0`` on the pile-up lenses, ``central_noise`` is
``baseline - 0.7`` and two tiles short, ``sersic_point`` is ``baseline - 0.3``
with one blank ``sersic_index`` cell.

Eight cases:

* ``test_per_variant_fractions_are_counted_over_all_rows`` — the fractions above
  4.5 / 4.9 / 9.5 (and 5.0 for ``wide_n``) are the hand-computed values, and they
  are counted over **all** of a variant's parseable rows rather than over the
  18-lens inner join. Clipping them to the join would hide exactly the shortfall
  the dropped-lens section exists to report.
* ``test_paired_deltas_against_baseline`` — the paired medians and 16-84 % bands
  are the hand-computed values over the inner join. The whole point of pairing is
  that the lens-to-lens scatter cancels; a delta taken over a variant's own rows
  instead would still look plausible.
* ``test_inner_join_and_its_named_losses`` — the lens set is the intersection
  (18 of 20), the two tiles ``central_noise`` never wrote are named in the report,
  and the blank ``sersic_index`` cell is named as an unparseable row rather than
  silently dropped.
* ``test_duplicate_lens_name_raises`` — a repeated ``lens_name`` raises
  ``ValueError`` naming it. Keeping the last row silently would make two
  concatenated results trees indistinguishable from one.
* ``test_missing_variant_file_names_the_present_ones`` — a missing scrape raises
  ``FileNotFoundError`` that lists what *is* there, which is the answer to "then
  what did I copy?".
* ``test_lens_map_june_comparison`` — with ``--lens-map`` the June-vs-baseline
  median is the hand value and the one joined lens absent from the map is named.
* ``test_witness_table_reads_numbers_beside_thresholds`` — exactly four rows
  W1-W4, every reading a number beside its threshold text, and the module source
  carries no verdict word. The four questions are science judgements over a
  sample with real scatter; a word printed by a CSV reader would be read as that
  judgement having been made.
* ``test_cli_writes_both_artefacts`` — ``main`` returns 0, writes
  ``sersic_variants.md`` and a non-empty ``sersic_variants.png``, and prints the
  summary table to stdout.

The module under test imports no PyAuto library and runs no fit, so these are
pure-CSV tests: fast, and safe in the ``not slow`` suite. Only the CLI case
touches matplotlib.
"""

import csv
import importlib.util
import re
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent

MODULE_PATH = PROJECT_ROOT / "scripts" / "analysis" / "sersic_variants.py"

# The stored DR1 header this fixture's CSVs must reproduce exactly.
HEADER_FIXTURE = PROJECT_ROOT / "tests" / "data" / "dr1_headers" / "lens_sersic.txt"

# The six Sersic parameters `catalogue/scripts/lens_sersic.py` scrapes, in the
# order it calls `add_variable`. No `intensity`: an `lp_linear.Sersic` solves it.
BASES = (
    "centre_0",
    "centre_1",
    "ell_comps_0",
    "ell_comps_1",
    "effective_radius",
    "sersic_index",
)

# The four value flavours beside the median, in `AggregateCSV`'s order.
VALUE_SUFFIXES = ("_lower_1_sigma", "_upper_1_sigma", "_lower_3_sigma", "_upper_3_sigma")

# 20 tiles, named the way the DR1 sample names them.
TILE_COUNT = 20

# Baseline lens Sersic indices: 13 of the 20 above 4.5 (0.65) and 5 of those
# above 4.9 (0.25), which is the June pile-up in miniature.
BASELINE_N = (
    [4.95] * 5
    + [4.70] * 4
    + [4.60] * 4
    + [3.00, 3.00, 2.00, 2.00, 1.50, 1.20, 0.90]
)

# Effective radii: a clean 0.1 ladder, so a shifted median is obvious.
BASELINE_R_EFF = [0.5 + 0.1 * index for index in range(TILE_COUNT)]

# The two tiles `central_noise` never wrote (its search did not complete), and
# the tile whose `sersic_index` cell `sersic_point` left blank (the `latent.`
# prefix shape). Together they cut the 20-tile union to an 18-lens inner join.
CENTRAL_NOISE_MISSING = (18, 19)
SERSIC_POINT_BLANK = 19

# The joined lens the synthetic lens_map has never heard of.
LENS_MAP_MISSING = 5


def _tile(index):
    """
    A DR1-shaped tile name for one fixture lens.
    """
    return (
        f"Tile1020{index:02d}065"
        f"RA0135279431{487 + index:03d}"
        f"DECNEG0701599765{928 - index:03d}"
    )


TILES = [_tile(index) for index in range(TILE_COUNT)]


@pytest.fixture(scope="module")
def analysis():
    """
    ``scripts/analysis/sersic_variants.py`` loaded by path: it is a script run
    with ``python scripts/analysis/...``, not an importable package member, so it
    is loaded the way ``tests/test_compare_catalogues.py`` loads the comparator.
    """
    spec = importlib.util.spec_from_file_location(
        "_sersic_variants_under_test", MODULE_PATH
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _columns():
    """
    The header of a synthetic ``lens_sersic_<variant>.csv``: the two label
    columns, then five columns per base in ``AggregateCSV``'s order.
    """
    header = ["id", "lens_name"]
    for base in BASES:
        header.append(base)
        header += [f"{base}{suffix}" for suffix in VALUE_SUFFIXES]
    return header


def _row(lens_name, values, *, blank=()):
    """
    One CSV row from ``{base: (median, sigma)}``.

    The four bound columns are built from the median and the sigma, so a row is
    self-consistent by construction and a test that wants an inconsistent one has
    to ask for it: ``blank`` empties every column of a base, which is how
    ``add_variable`` writes a missed argument.
    """
    row = {"id": f"{lens_name}_id", "lens_name": lens_name}
    for base, (median, sigma) in values.items():
        if base in blank:
            row[base] = ""
            for suffix in VALUE_SUFFIXES:
                row[f"{base}{suffix}"] = ""
            continue
        row[base] = repr(median)
        row[f"{base}_lower_1_sigma"] = repr(median - sigma)
        row[f"{base}_upper_1_sigma"] = repr(median + sigma)
        row[f"{base}_lower_3_sigma"] = repr(median - 3 * sigma)
        row[f"{base}_upper_3_sigma"] = repr(median + 3 * sigma)
    return row


def _values(sersic_index, effective_radius):
    """
    The six bases of one fixture row. Only ``sersic_index`` and
    ``effective_radius`` are varied per variant; the rest are held fixed so a
    change in them cannot be what moves a reading.
    """
    return {
        "centre_0": (0.01, 0.005),
        "centre_1": (-0.02, 0.005),
        "ell_comps_0": (0.10, 0.01),
        "ell_comps_1": (-0.20, 0.01),
        "effective_radius": (effective_radius, 0.05),
        "sersic_index": (sersic_index, 0.10),
    }


def _variant_rows(variant):
    """
    ``[(tile, sersic_index, effective_radius, blank_bases)]`` for one variant.

    ``wide_n`` walks the pile-up lenses (baseline ``n > 4.5``) one full unit past
    the old prior edge; ``central_noise`` drops every lens by 0.7 and is two tiles
    short; ``sersic_point`` drops every lens by 0.3 and has one blank cell.
    """
    assert variant in ("baseline", "wide_n", "central_noise", "sersic_point"), (
        f"unknown fixture variant {variant}"
    )

    rows = []
    for index, tile in enumerate(TILES):
        sersic_index = BASELINE_N[index]
        effective_radius = BASELINE_R_EFF[index]
        blank = ()

        if variant == "wide_n":
            if sersic_index > 4.5:
                sersic_index = sersic_index + 1.0
            effective_radius = effective_radius + 0.2
        elif variant == "central_noise":
            if index in CENTRAL_NOISE_MISSING:
                continue
            sersic_index = sersic_index - 0.7
            effective_radius = effective_radius - 0.1
        elif variant == "sersic_point":
            sersic_index = sersic_index - 0.3
            effective_radius = effective_radius - 0.05
            if index == SERSIC_POINT_BLANK:
                blank = ("sersic_index",)

        rows.append((tile, sersic_index, effective_radius, blank))
    return rows


def _write_variant(directory, variant, rows=None):
    """
    Write ``lens_sersic_<variant>.csv`` into ``directory`` and return its path.
    """
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"lens_sersic_{variant}.csv"
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=_columns())
        writer.writeheader()
        for tile, sersic_index, effective_radius, blank in (
            _variant_rows(variant) if rows is None else rows
        ):
            writer.writerow(
                _row(tile, _values(sersic_index, effective_radius), blank=blank)
            )
    return path


def _fixture_directory(tmp_path):
    """
    The four scrapes in one directory, as the user copies them.

    Also asserts the written header is byte-for-byte the stored DR1 one: a
    fixture whose header has drifted from the real producer's would let this whole
    module pin the wrong file.
    """
    directory = tmp_path / "scrapes"
    for variant in ("baseline", "wide_n", "central_noise", "sersic_point"):
        path = _write_variant(directory, variant)
        written = path.read_text().splitlines()[0]
        assert written == HEADER_FIXTURE.read_text().strip(), (
            f"lens_sersic_{variant}.csv header is not the stored DR1 header"
        )
    return directory


def _write_lens_map(tmp_path, missing_index=LENS_MAP_MISSING):
    """
    A synthetic ``sample/lens_map.csv`` with the six real columns.

    ``june_sersic_index`` is ``baseline - 0.2`` on even tiles and
    ``baseline - 0.4`` on odd ones, so the June delta has a real median rather
    than one repeated value, and ``missing_index`` is left out of the map
    entirely.
    """
    path = tmp_path / "lens_map.csv"
    header = [
        "euclid_object_id",
        "sep1_tile",
        "batch_zip",
        "offset_arcsec",
        "total_valid_votes",
        "june_sersic_index",
    ]
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        for index, tile in enumerate(TILES):
            if index == missing_index:
                continue
            offset = 0.2 if index % 2 == 0 else 0.4
            writer.writerow(
                {
                    "euclid_object_id": f"{2_000_000 + index}",
                    "sep1_tile": tile,
                    "batch_zip": f"batch_{index // 5}.zip",
                    "offset_arcsec": repr(0.05 + 0.01 * index),
                    "total_valid_votes": f"{10 + index}",
                    "june_sersic_index": repr(BASELINE_N[index] - offset),
                }
            )
    return path


def _run(analysis, directory, out_dir, extra=()):
    """
    Run the CLI over ``directory`` and return ``(exit_code, report_text)``. The
    report is read back from the written file rather than captured off stdout,
    because the file is what the analysis keeps.
    """
    code = analysis.main([str(directory), "--out", str(out_dir), *extra])
    return code, (out_dir / "sersic_variants.md").read_text()


def test_per_variant_fractions_are_counted_over_all_rows(analysis, tmp_path):
    """
    Pins each variant's own distribution: the medians and the fractions above
    4.5 / 4.9 / 9.5, plus 5.0 for ``wide_n``.

    The denominators are the load-bearing part. ``baseline`` has 20 parseable
    rows against an 18-lens inner join, so ``13/20 = 0.65`` proves the fractions
    are counted over all of a variant's rows; over the join the same count would
    read ``13/18 = 0.722``.
    """
    directory = _fixture_directory(tmp_path)
    data = analysis.load_variants(directory)
    summaries = data["summaries"]

    # baseline: 20 rows, 13 above 4.5, 5 above 4.9.
    assert summaries["baseline"]["n"] == 20
    assert summaries["baseline"]["median_n"] == pytest.approx(4.60)
    assert summaries["baseline"]["median_r_eff"] == pytest.approx(1.45)
    assert summaries["baseline"]["fraction_above"][4.5] == pytest.approx(13 / 20)
    assert summaries["baseline"]["fraction_above"][4.9] == pytest.approx(5 / 20)
    assert summaries["baseline"]["fraction_above"][9.5] == pytest.approx(0.0)

    # Counted over all 20 rows, not over the 18 the inner join keeps.
    assert len(data["joined"]) == 18
    assert summaries["baseline"]["fraction_above"][4.5] != pytest.approx(13 / 18)

    # wide_n: the 13 pile-up lenses walked a full unit past the old edge, and
    # none of them re-piled at the new one.
    assert summaries["wide_n"]["n"] == 20
    assert summaries["wide_n"]["median_n"] == pytest.approx(5.60)
    assert summaries["wide_n"]["median_r_eff"] == pytest.approx(1.65)
    assert summaries["wide_n"]["fraction_above"][5.0] == pytest.approx(13 / 20)
    assert summaries["wide_n"]["fraction_above"][9.5] == pytest.approx(0.0)

    # central_noise: two tiles short, and every lens 0.7 lower, which takes the
    # whole sample below 4.5.
    assert summaries["central_noise"]["n"] == 18
    assert summaries["central_noise"]["median_n"] == pytest.approx(3.95)
    assert summaries["central_noise"]["median_r_eff"] == pytest.approx(1.25)
    assert summaries["central_noise"]["fraction_above"][4.5] == pytest.approx(0.0)
    assert 5.0 not in summaries["central_noise"]["fraction_above"]

    # sersic_point: 20 rows in the file, 19 parseable, so the denominator is 19.
    assert summaries["sersic_point"]["n"] == 19
    assert data["row_counts"]["sersic_point"] == 20
    assert summaries["sersic_point"]["median_n"] == pytest.approx(4.30)
    assert summaries["sersic_point"]["median_r_eff"] == pytest.approx(1.35)
    assert summaries["sersic_point"]["fraction_above"][4.5] == pytest.approx(5 / 19)
    assert summaries["sersic_point"]["fraction_above"][4.9] == pytest.approx(0.0)


def test_paired_deltas_against_baseline(analysis, tmp_path):
    """
    Pins the paired medians and the 16-84 % bands over the 18-lens inner join,
    for both ``sersic_index`` and ``effective_radius``.

    ``wide_n`` is the interesting one: 13 lenses moved by 1.0 and 5 did not move
    at all, so the median is 1.0 and the band spans 0.0 to 1.0 — a summary that
    reported only the median would hide the fact that a quarter of the sample is
    untouched.
    """
    directory = _fixture_directory(tmp_path)
    data = analysis.load_variants(directory)
    rows, joined = data["rows"], data["joined"]

    wide = analysis.paired_deltas(rows["wide_n"], rows["baseline"], joined, "sersic_index")
    assert wide["n"] == 18
    assert wide["median"] == pytest.approx(1.0)
    assert wide["p16"] == pytest.approx(0.0)
    assert wide["p84"] == pytest.approx(1.0)

    central = analysis.paired_deltas(
        rows["central_noise"], rows["baseline"], joined, "sersic_index"
    )
    assert central["n"] == 18
    assert central["median"] == pytest.approx(-0.7)
    assert central["p16"] == pytest.approx(-0.7)
    assert central["p84"] == pytest.approx(-0.7)

    point = analysis.paired_deltas(
        rows["sersic_point"], rows["baseline"], joined, "sersic_index"
    )
    assert point["n"] == 18
    assert point["median"] == pytest.approx(-0.3)

    for variant, expected in (
        ("wide_n", 0.2),
        ("central_noise", -0.1),
        ("sersic_point", -0.05),
    ):
        delta = analysis.paired_deltas(
            rows[variant], rows["baseline"], joined, "effective_radius"
        )
        assert delta["n"] == 18
        assert delta["median"] == pytest.approx(expected)
        assert delta["p16"] == pytest.approx(expected)
        assert delta["p84"] == pytest.approx(expected)


def test_inner_join_and_its_named_losses(analysis, tmp_path):
    """
    Pins the inner join at 18 of the 20 union lenses, and pins that every loss is
    **named** in the report: the two tiles ``central_noise`` never wrote, and the
    row whose ``sersic_index`` cell ``sersic_point`` left blank.

    A variant that quietly shrank is the one way all four readings come out
    looking tidier than the data are, so a count alone is not enough.
    """
    directory = _fixture_directory(tmp_path)
    data = analysis.load_variants(directory)

    assert len(data["union"]) == 20
    assert data["joined"] == sorted(TILES[:18])

    dropped_tiles = [TILES[index] for index in CENTRAL_NOISE_MISSING]
    assert data["dropped"]["central_noise"] == sorted(dropped_tiles)
    assert data["dropped"]["sersic_point"] == [TILES[SERSIC_POINT_BLANK]]
    assert data["dropped"]["baseline"] == []
    assert data["unparseable"]["sersic_point"] == [TILES[SERSIC_POINT_BLANK]]

    report = analysis.render_report(data)
    section = report.split("## Lenses dropped by the inner join")[1]
    for tile in dropped_tiles:
        assert tile in section, f"dropped tile {tile} is not named in the report"
    assert "would not parse" in section, (
        "the blank sersic_index row must be reported as unparseable, not dropped "
        "silently"
    )


def test_duplicate_lens_name_raises(analysis, tmp_path):
    """
    A repeated ``lens_name`` raises ``ValueError`` naming the tile.

    The producer writes one row per lens, so a duplicate means two results trees
    were concatenated or a tile was scraped twice; keeping the last row silently
    would make those indistinguishable from a clean scrape.
    """
    directory = tmp_path / "scrapes"
    doubled = _variant_rows("baseline") + [_variant_rows("baseline")[3]]
    path = _write_variant(directory, "baseline", rows=doubled)

    with pytest.raises(ValueError) as error:
        analysis.read_scrape(path)

    assert TILES[3] in str(error.value)


def test_missing_variant_file_names_the_present_ones(analysis, tmp_path):
    """
    A missing ``lens_sersic_<variant>.csv`` raises ``FileNotFoundError`` that
    names the path it wanted *and* lists the scrapes that are present — the
    answer to "then what did I copy?".

    Also pins that ``baseline`` is required in any variant set: every paired
    delta and the June comparison are taken against it.
    """
    directory = tmp_path / "scrapes"
    _write_variant(directory, "baseline")
    _write_variant(directory, "wide_n")

    with pytest.raises(FileNotFoundError) as error:
        analysis.load_variants(directory)

    message = str(error.value)
    assert "central_noise" in message
    assert "lens_sersic_baseline.csv" in message
    assert "lens_sersic_wide_n.csv" in message

    with pytest.raises(ValueError):
        analysis.load_variants(directory, variants=("wide_n",))


def test_lens_map_june_comparison(analysis, tmp_path):
    """
    With ``--lens-map`` the June-vs-baseline median is the hand value over the
    17 joined lenses the map carries, and the one joined lens the map has never
    heard of is named.

    The deltas are 0.2 on nine lenses and 0.4 on eight, so the median is a real
    median and not one repeated value; a shrinking overlap quietly changes what
    W1 is a median of, which is why the absentee is named rather than counted.
    """
    directory = _fixture_directory(tmp_path)
    lens_map = analysis.load_lens_map(_write_lens_map(tmp_path))

    assert len(lens_map) == 19

    data = analysis.load_variants(directory)
    comparison = analysis.june_comparison(data, lens_map)

    assert comparison["n"] == 17
    assert comparison["median"] == pytest.approx(0.2)
    assert comparison["p16"] == pytest.approx(0.2)
    assert comparison["p84"] == pytest.approx(0.4)
    assert comparison["missing"] == [TILES[LENS_MAP_MISSING]]

    report = analysis.render_report(data, lens_map=lens_map)
    section = report.split("## June versus baseline")[1].split("## Witness readings")[0]
    assert TILES[LENS_MAP_MISSING] in section


def test_witness_table_reads_numbers_beside_thresholds(analysis, tmp_path):
    """
    Exactly four rows W1-W4, each a number beside the threshold text it is to be
    read against, and **no verdict word anywhere in the module source**.

    Each of the four questions is a science judgement over a sample with real
    scatter. A single word printed by a CSV reader would be read as that judgement
    having been made, so the script prints the reading and the threshold and stops.
    """
    directory = _fixture_directory(tmp_path)
    lens_map = analysis.load_lens_map(_write_lens_map(tmp_path))
    data = analysis.load_variants(directory)

    table = analysis.witness_table(data, lens_map=lens_map)

    assert [row[0] for row in table] == ["W1", "W2", "W3", "W4"]
    assert all(len(row) == 4 for row in table)

    readings = {row[0]: row[2] for row in table}
    thresholds = {row[0]: row[3] for row in table}

    assert readings["W1"] == pytest.approx(0.2)
    assert readings["W2"] == pytest.approx(13 / 20)
    assert readings["W3"] == pytest.approx(-0.7)
    assert readings["W4"] == pytest.approx(-0.3)
    assert all(isinstance(value, float) for value in readings.values())
    assert all(isinstance(text, str) and text for text in thresholds.values())

    # Without the map W1 has nothing to difference against and says so, rather
    # than inventing a June value.
    without_map = analysis.witness_table(data)
    assert without_map[0][2] == "n/a (no --lens-map)"

    # The verdict words, assembled here so this test file is not itself what the
    # search trips on.
    banned = ("".join(("PA", "SS")), "".join(("FA", "IL")))
    source = MODULE_PATH.read_text()
    for word in banned:
        assert not re.search(rf"\b{word}\b", source), (
            f"scripts/analysis/sersic_variants.py must form no verdict, but its "
            f"source carries the word {word!r}"
        )


def test_cli_writes_both_artefacts(analysis, tmp_path, monkeypatch, capsys):
    """
    The CLI returns 0, writes ``sersic_variants.md`` and a non-empty
    ``sersic_variants.png`` under ``--out``, and prints the report to stdout.

    This is the only case that touches matplotlib, which the module imports
    lazily inside ``write_histograms`` with the Agg backend selected first; the
    caches are pointed at ``tmp_path`` the way a restricted environment needs.
    """
    monkeypatch.setenv("MPLCONFIGDIR", str(tmp_path / "mpl"))
    monkeypatch.setenv("NUMBA_CACHE_DIR", str(tmp_path / "numba"))

    directory = _fixture_directory(tmp_path)
    lens_map_path = _write_lens_map(tmp_path)
    out_dir = tmp_path / "out" / "sersic_variants"

    code, report = _run(
        analysis, directory, out_dir, extra=["--lens-map", str(lens_map_path)]
    )

    assert code == 0
    assert (out_dir / "sersic_variants.md").is_file()
    assert (out_dir / "sersic_variants.png").is_file()
    assert (out_dir / "sersic_variants.png").stat().st_size > 0

    assert "## Per-variant summary" in report
    assert "| variant | N rows | N joined | median n | median R_eff |" in report

    captured = capsys.readouterr()
    assert "## Per-variant summary" in captured.out
    assert "wrote" in captured.err
