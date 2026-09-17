# `scripts/analysis/` — post-run analysis over catalogue scrapes

Scripts that read **already-built** catalogue CSVs and say something about them.
Nothing here fits a lens, runs a search or imports a PyAuto library: an analysis
script takes a directory of scrapes as a positional argument, reads CSVs with
`csv` + `numpy`, and writes a markdown report and a figure. That is why they live
beside the pipelines rather than in `scripts/`, and why each one is listed in
`config/build/no_run.yaml` rather than in `smoke_tests.txt` — the smoke runner
appends one global `args_default` (`--dataset=… --sample=…`) to every entry, which
an analysis script's argparse rejects, and a clean checkout holds no scrapes to
analyse anyway. Their coverage is a unit test on a synthetic fixture instead.

`scripts/tools/compare_catalogues.py` is the neighbouring idea: it diffs two
*built* catalogues row by row. The difference is the question — that one asks
whether two catalogues are the same catalogue; these ask what a catalogue says.

## `sersic_variants.py` — the four Sersic variant scrapes, compared

The `euclid_sersics` project asks why the lens-light Sersic index `n` piles up at
the prior edge `n = 5` in the June DR1 catalogue (67 % of the core 100 lenses came
back above 4.5). The same 100 lenses are re-fitted under four variants of the
Sersic stage, and this script lays the four resulting `n` distributions beside one
another.

### Producing the four inputs

One fit and one scrape per variant. `catalogue/scripts/lens_sersic.py` writes a
file called `lens_sersic.csv` every time, so each scrape goes to its own
`--inspect_dir` and is then copied to a per-variant name in **one** directory:

```bash
mkdir -p inspect/sersic_variants_in

for v in baseline wide_n central_noise sersic_point; do
    python scripts/sersic_lens_model.py --sample=euclid_sersics --variant=$v

    python catalogue/scripts/lens_sersic.py \
        --sample=euclid_sersics \
        --unique_tag=sersic_lens_model_$v \
        --inspect_dir=inspect/euclid_sersics_$v

    cp inspect/euclid_sersics_$v/lens_sersic.csv \
       inspect/sersic_variants_in/lens_sersic_$v.csv
done
```

`--variant` is `scripts/sersic_lens_model.py`'s (PR #75); each variant writes its
results under the unique tag `sersic_lens_model_<variant>`, which is what the
scrape's `--unique_tag` selects.

### Running it

```bash
python scripts/analysis/sersic_variants.py inspect/sersic_variants_in \
    --lens-map ../euclid_sersics/sample/lens_map.csv \
    --out inspect/sersic_variants
```

- `directory` (positional) — holds `lens_sersic_<variant>.csv` for each variant.
- `--out` — where the two artefacts go. Default `inspect/sersic_variants`;
  `inspect/` is gitignored.
- `--lens-map PATH` — the science clone's `sample/lens_map.csv`
  (`euclid_object_id,sep1_tile,batch_zip,offset_arcsec,total_valid_votes,june_sersic_index`),
  joined on `sep1_tile == lens_name`. Without it W1 reads `n/a`.
- `--variants a,b,c` — override the variant set; `baseline` is required in any
  set, because every paired delta is taken against it.

### What the outputs hold

- `<out>/sersic_variants.md` (also printed to stdout) — the inputs and their row
  counts; each variant's own `n` and `R_eff` medians and the fractions above
  4.5 / 4.9 / 9.5 (plus 5.0 for `wide_n`, whose prior edge moved); the paired
  Δn and ΔR_eff against `baseline` with 16–84 % bands over the inner join; the
  June-vs-baseline Δn when `--lens-map` is given; the W1–W4 readings; every lens
  the inner join dropped and every unparseable row, named; and the closing note
  on what the scrape does not carry.
- `<out>/sersic_variants.png` — a four-panel histogram of `n`, one panel per
  variant, all four on the same 0.5–10.0 bins (width 0.25) so they are read
  against one another. Every panel carries the configured prior's edges
  (0.8 / 5.0); the `wide_n` panel carries its widened edges (0.5 / 10.0) dashed
  on top.

Summary numbers are computed over **all** of a variant's parseable rows; paired
deltas over the **inner join** only, so a median Δn is the same lenses fitted
twice.

### The four readings

| W | Question | Reading | Threshold |
|---|---|---|---|
| W1 | Does `baseline` reproduce June? | median(baseline `n` − June `n`) over the joined lenses with a `lens_map` row | \|Δn\| ≤ 0.5 |
| W2 | Does the prior edge cause the pile-up? | `wide_n` fraction with `n` > 5.0 | ≥ 0.5 |
| W3 | Do the central pixels drive it? | median paired Δn (`central_noise` − `baseline`) | ≤ −0.5 |
| W4 | Does a nucleus component absorb it? | median paired Δn (`sersic_point` − `baseline`) | ≤ −0.5 |

W1 also prints baseline's own fraction above 4.5 beside the June reference 0.67,
and W2 the `wide_n` fraction above 9.5 — a distribution that simply re-piles at
the widened prior's own edge has told you the prior is still what holds `n`.

**The thresholds above are transcribed** for this script and are **to be confirmed
against the plan page "Euclid Sersics Plan" rev 3** before any reading is quoted.
They live in one constant (`WITNESSES`) so a revision is a one-line edit.

The script prints the reading and the threshold side by side and **forms no
verdict**: each of the four questions is a science judgement over a sample with
real scatter, and a single word printed by a CSV reader would be read as that
judgement having been made.

### Out of scope

The `sersic_point` **nucleus flux fraction** is not available from these CSVs.
`catalogue/scripts/lens_sersic.py` scrapes the six free parameters of the lens's
`lp_linear.Sersic` (`centre_0`, `centre_1`, `ell_comps_0`, `ell_comps_1`,
`effective_radius`, `sersic_index`) and no `intensity` — a linear light profile's
intensity is solved by linear algebra at every likelihood evaluation and never
enters the non-linear samples. How much light the `point` component took needs a
separate scrape of that component, or the calibrated per-band fluxes in
`magnitudes.csv`. W4 reads the Sersic index's response instead, which is what
this scrape can answer.

### Tests

`tests/test_sersic_variants_analysis.py` runs the script end to end on a
synthetic four-CSV fixture (20 tiles, the real 32-column `lens_sersic.csv`
header) and pins the fractions, the paired medians and bands, the inner join and
its named losses, the duplicate/missing-file errors, the `--lens-map` join, and
that the module source carries no verdict word.
