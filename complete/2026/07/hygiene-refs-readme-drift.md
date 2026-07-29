Widened PyAutoBrain's hygiene `refs` scanner so it can see the reference idiom
workspace READMEs actually use. Started from "autolens_workspace/README.md refers
to slam_pipeline"; the scanner change is what turned that one symptom into a
measurable class.

## The blind spot

**Two** checkers could have caught this and neither could, for the same reason:
both only matched reference tokens anchored on `scripts/` or `notebooks/`.

- `_hygiene_refs.py` — `is_reference()` also required a trailing `/` or a
  `.py`/`.ipynb` suffix, and `scanned_files()` read only `scripts/**/*.py` plus
  the **top-level** README.
- PyAutoHands `check_navigator.py` — a per-PR hard gate on 6 repos. It already
  read `scripts/**/README.md`; `_PATH_TOKEN_RE` simply could not match.

READMEs write references as structure-list bullets (``- `slam_pipeline`: ``),
slash-less relative paths (`data_preparation/imaging`), and config YAML names.
So the scripts kept running, Heart stayed green, and only the reader was
misdirected.

## Shipped

- **#178** — scan every `scripts/**/README.md` and `config/**/README.md`;
  recognise the three shapes above. **refs 4 → 218** across 7/7 repos, becoming
  the top-ranked hygiene item. 32 tests.
- **#180** — bug found *by* the follow-on workspace fix: `Resolver.resolves` used
  `lstrip("./")`, which strips a character **set**, not a prefix, mangling every
  dot-directory reference (`.claude/skills` → `claude/skills`) and reporting it
  dead. Surfaced when correcting a README's `skills` entry to the accurate
  `.claude/skills` made the scanner flag the correction. 33 tests.

## What carried the precision (reusable)

Recall was easy; precision was the work. First attempt reported **563**.

- **Extension folding.** Prose habitually drops the suffix ("see
  `features/pixelization/modeling`"). Resolving extension-less tokens against
  directory **and** file **and** `<name>.py` cut 563 → 221.
- **Structure-list quorum.** A bare backticked word is only a path in the
  ``- `x`: `` bullet idiom, and even there a list may describe parameters. The
  list itself is the evidence: trust extension-less names only when ≥2 in the
  same block resolve. A glossary is skipped whole; one stale entry among live
  ones still reports. Names with a file extension bypass the quorum — that is
  what catches a config README inventorying deleted YAML.
  *Cost:* a small block where everything is dead reports nothing
  (`casa_to_autogalaxy`, `profiling` were found by hand).
- **Anchoring must accept head OR tail.** Requiring the leading segment to be a
  real directory silently suppressed exactly the typo cases the work existed to
  find (`sdvanced/modeling`, `guide/advanced`). Requiring both ends would too.

Residual false-positive classes are documented in the module docstring rather
than tuned away silently.

## Traps

- The Feature Agent scored both phases `large`/`too-large` and proposed a
  4-phase `design`/`core_api` split off its repo-count proxy — meaningless for a
  prose sweep. Overridden and recorded on both issues.
- A commit-message heredoc quoted with `"` lets bash eat backticked spans; the
  message landed with holes. Use `-F <file>`.

## Original prompt

# Teach hygiene `refs` the workspace-README drift class

Type: feature
Target: pyautobrain
Repos:
- PyAutoBrain
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised

The hygiene `refs` mode cannot see the dominant reference idiom in workspace
`README.md` files, so a whole class of restructure debt accumulates invisibly.
`autolens_workspace/README.md` still lists `slam_pipeline` as a top-level
directory; it has not existed for a long time (SLaM lives under
`scripts/guides/modeling/slam_start_here.py` and `scripts/multi/features/slam/`).

Two independent gaps in `agents/conductors/hygiene/_hygiene_refs.py`:

1. **Scanned set too narrow.** `scanned_files()` reads `scripts/**/*.py` plus the
   *top-level* README only. Nearly all of the drift lives in nested
   `scripts/**/README.md` and `config/**/README.md`.
2. **`is_reference()` cannot match the README idiom.** It accepts a reference
   only when it ends in `/` (multi-segment) or its last segment matches
   `\.(py|ipynb)$`. Workspace READMEs instead write:
   - bare structure-list bullets — ``- `slam_pipeline`: The SLaM pipelines…``
   - directory paths with no trailing slash — `` `data_preparation/imaging` ``
     (the real package is `imaging/data_preparation`)
   - config file names — `` `mcmc.yaml` ``, `` `generag.yaml` ``

Extend the scanner to cover all three shapes, plus the widened file set. Keep
every existing precision suppression (`RUNTIME_DIRECTORIES`, bare `name.py`,
single-segment folder refs, un-checked-out siblings) — this tier's value depends
on staying high-precision. Confine the bare-name rule to the ``- `x`: `` bullet
idiom so a backticked word in running prose is never treated as a reference.

Resolution reuses the existing `RepositoryIndex.has_directory` / `has_file`
machinery; no new resolver is needed.

Add cases to `tests/test_hygiene_conductor.py` covering each new rule **and**
each known false-positive class, specifically these verified non-findings which
must stay unreported: runtime-generated targets (`main_lens_centres.json`,
`dataset/imaging/clumpy`, `search_internal/`, `activate.sh`) and cross-repo refs
that genuinely resolve in a sibling checkout.

Update the `refs` row in `agents/conductors/hygiene/AGENTS.md` and the `refs`
gloss in `skills/hygiene/hygiene.md` to describe the widened scope.

Acceptance: `bin/pyauto-brain hygiene refs` surfaces the audited autolens /
autogalaxy README findings (structure-list entries, reversed relative paths,
`generag.yaml`, stale config inventories) with no verified false positive
present, and `bin/pyauto-brain hygiene` still emits a coherent ranked worklist.

## Original request

> the autolens workspacde readme has API drift (e.g. it refers to slam_pipeline).
> Can you do a sweep of this over autolens_workspaceand gaalxy and then put the
> thing in the hygeine agent?
