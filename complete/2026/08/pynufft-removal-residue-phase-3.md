Shipped 2026-08-24 across three repos (issue @PyAutoHands#258):
@PyAutoHands#259, @PyAutoHeart#162, @PyAutoCTI#107 — plus @PyAutoCTI#108, an
unplanned fix for a red `main` this task walked into.

Phase 3 of 3, closing the pynufft-removal residue. Phases 1-2 shipped
2026-08-23. Run entirely from a mobile/web session: no local checkout, no
worktree — branches pushed from fresh clones through the GitHub API.

## What changed

- **@PyAutoHands** `release.yml` — 3 sites. `release_test_pypi` -> Tests dropped
  a bare `pip install pynufft==2025.1.1`; `run_smoke_tests` and
  `release_workspaces` went from `pip install pynufft==2025.1.1 numba` to
  `pip install numba`. `numba` kept at both shared sites; the neighbouring
  "matplotlib deliberately unpinned" comments are about matplotlib and were left
  alone.
- **@PyAutoHeart** `workspace-validation.yml:302` — the same one-line edit in the
  `mode=release` "Install TestPyPI wheels" step. The `nufftax>=0.6.1,<0.7.0`
  install two lines below is the *live* NUFFT backend and is untouched.
- **@PyAutoCTI** `docs/installation/source.rst` — the whole "For unit tests to
  pass you will also need the following optional requirements" stanza in the
  *Building Only PyAutoCTI* section, not just its pynufft line (below).

## Scope change: pylops went too

The stanza held `pip install pynufft` **and** `pip install pylops==1.11.1`. The
human confirmed mid-task that pylops is defunct, so both went and the sentence
went with them — a heading over an empty `code-block` is invalid RST.

Same evidence covers both: no import or reference anywhere in PyAutoCTI (only
`paper/paper.bib`, a published record), `pyproject.toml`'s `optional` extra is
`["numba"]`, and CI installs neither while the suite passes.

## Verified, not assumed — as the prompt demanded

The prompt asked specifically that CTI's suite be confirmed to pass without
pynufft before the line came out:

- `main.yml` is a thin caller of PyAutoHeart's reusable `lib-tests.yml`, which
  installs `./PyAutoCTI[optional]` plus the Nerves/Fit/Array chain and installs
  **neither** pynufft nor pylops — in the `unittest` leg or the
  `unittest-nojax` leg.
- Full-tree greps: pynufft only in `paper/paper.bib`, `files/citations.tex` and
  the deleted line; pylops only in `paper.bib` and the deleted line.

## The detour: PyAutoCTI `main` was already red

Opening the docs PR turned up a failure on all three CTI legs. It was **not**
the diff — a single deleted `.rst` line, and the run was on the PR *merge* ref,
so the failure was `main`'s:

```
test_serial_eper.py::test__region_list_from__array_2d_list_from
  autoarray.exc.MaskException: shape_native[1] must be a positive number of
  pixels; got 0. The full shape_native input was (3, 0)
```

`lib-tests.yml` clones PyAutoArray **`main`** at run time, so CTI's suite tracks
autoarray source, not a released wheel. @PyAutoArray#440 (`f2f7a4f`, 2026-08-09
— the #333/B8 input-validation guards, record
`autoarray-input-validation-guards.md`) added the zero-length `shape_native`
guard to `Mask2D.__init__`. CTI's last `main` run was **2026-08-07**, so the
break sat dormant for two weeks: nothing had pushed to CTI since the guard
landed. It would have blocked every CTI PR.

**The guard did not break a working test — it exposed one that checked nothing.**
`serial_array` is 3x10 (columns 0-9). For region `(0, 3, 5, 8)`, whose trailing
region starts at column 8, `pixels=(2, 3)` resolves to columns 10-11: a window
entirely past the edge, extracting to `(3, 0)`. The assertion it fed was

    assert (array_2d_list[1] == np.array([[10.0], [10.0], [10.0]])).all()

and an empty-array comparison is vacuously True for **any** expected value —
confirmed empirically, not reasoned about: `(np.zeros((3,0)) == [[10.]]*3).all()`
is True, and so is the same comparison against `999.0`. `10.0` is not even a
value the fixture contains. That is the tell worth carrying forward: **an
expected value outside the fixture's range is a smell for a vacuous assertion.**

@PyAutoCTI#108 fixed it test-only — the case now asserts that a fully
out-of-range window raises, so the edge stays covered instead of silently
passing. Deliberately NOT decided there: whether such a window *should* raise or
clip to empty. A partially overlapping window still clips (the `pixels=(0, 3)`
case asserts it), so the two behaviours are currently inconsistent.

## Verification caveat — the changed lines are release-path

Every Hands/Heart line this task touched is on a **release** path: `release.yml`
is `workflow_dispatch`-only, and Heart's line is in the `mode=release` leg
reached only via `release-integrate.yml`. Ordinary PR CI cannot exercise them.
The pre-merge signal was each repo's own PR checks plus the diff; **full
confirmation lands on the next release rehearsal / nightly run.** The CTI leg,
by contrast, is fully exercised and green.

CI at merge: Hands 3/3 legs (3.12/3.13/3.14), Heart 2/2 (3.12/3.13), CTI 3/3
(3.12/3.13/no-jax) on both #108 and #107.

## Heart was RED throughout

"release validation FAILED" — pre-existing, unrelated, acknowledged by the human
at launch. PR-open was authorized under that acknowledgement; merge came later
as a human act (`/prm`).

## Follow-ups left open

- `draft/bug/autocti/serial_eper_zero_width_region_vs_autoarray_guard.md` — the
  clip-vs-raise semantics question #108 deliberately did not answer, plus a
  sweep for the same vacuous-assertion pattern in the parallel-EPER siblings.
- **CTI install-doc rot, untouched:** the *Building All Projects* section still
  says `pip install -r PyAutoArray/optional_requirements.txt`, and the prose
  above points at `PyAutoCTI/requirements.txt`. Neither file exists any more —
  packaging moved to `pyproject.toml` extras.
- `paper/paper.bib` and `files/citations.tex` still cite PyNUFFT and PyLops.
  Deliberate: published-record material, per the parent task.

## Original prompt

# Phase 3: stop installing pynufft in Hands/Heart CI and PyAutoCTI install docs

Type: maintenance
Target: ci
Repos:
- @PyAutoHands
- @PyAutoHeart
- @PyAutoCTI
Difficulty: low
Autonomy: supervised
Priority: normal
Status: issued
Filed: 2026-08-23
Issued: 2026-08-23

Phase 3 of 3. Parent: `pynufft_removal_downstream_residue.md`. Independent of
phases 1 and 2.

`pynufft` is no longer a dependency of any PyAuto library (@PyAutoArray#475
dropped it from both `optional` and `dev`), but four CI recipes and one install
doc still install it.

## Sites

- `@PyAutoHands/.github/workflows/release.yml:296,355,774` —
  `pip install pynufft==2025.1.1` (once bare, twice with `numba`)
- `@PyAutoHeart/.github/workflows/workspace-validation.yml:302` — same
- `@PyAutoCTI/docs/installation/source.rst:58` — `pip install pynufft`, listed
  under "For unit tests to pass you will also need the following optional
  requirements". **Confirm PyAutoCTI's suite genuinely has no such need before
  deleting the line** — verify, do not assume.

## Severity

Not urgent. These pin **2025.1.1**, not the broken `2022.2.2`, so they are
**not** hitting the `scipy.linalg.pinv2` failure and no build is red. This is
wasted install time and unnecessary resolver surface.

Worth knowing while working: these recipes are the only reason the local dev
environment still has `pynufft 2025.1.1` installed at all — removing them
changes what a fresh local env contains.

## Acceptance

- No PyAuto CI workflow installs `pynufft`.
- PyAutoCTI's install doc no longer instructs users to, with evidence its tests
  pass without it.
- The affected workflows are confirmed green afterwards — **every run and every
  matrix leg**, not just the first one reported.
