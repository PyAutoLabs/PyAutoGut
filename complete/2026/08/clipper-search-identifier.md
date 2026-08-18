- library-prs: https://github.com/PyAutoLabs/PyAutoFit/pull/1494
- merge-commits: PyAutoFit `f3767a79743e6976accd8fd6957afc5f366654fb` (2026-08-18, squash)
- issue: PyAutoFit#1493 (closed by the PR)
- summary: The prior-support `Clipper` now enters the search identifier, scoped
  to the two search families that consume one: `__identifier_fields__ =
  ("clipper",)` on `AbstractMultiStartGradient` and `AbstractBFGS` — the entire
  source change. Nested samplers, MCMC searches and `Drawer` are untouched and
  their identifiers pinned byte-identical by regression tests. Closes follow-up
  4 of `complete/2026/08/prior-support-clipper.md`.
- validation: identifier test file 29/29 (23 existing incl. the untouched
  `test_dynesty_static` pin + 6 new); full suite on py3.13 with jax extras
  1864 passed, 1 failed = the documented environment-specific
  `test_nautilus.py::test__single_core_builds_no_pool` (reproduced identically
  on a clean tree); CI green on 3.12 / 3.13 / docs. Human authorized the merge
  on green CI.
- release: not performed; merged PR remains in the pending-release queue.

## The decision (human, 2026-08-18)

The prompt was filed `Autonomy: human-required` because either answer costs
someone's stored results. The human chose option 2 of the four, scoped:
**the clipper enters the identifier on the searches that consume one, and the
nested samplers' identifiers stay byte-for-byte identical** — nested-sampling
runs are the long-lived, expensive archive; MLE gradient fits are
minutes-to-hours and re-keying them is an accepted one-time cost. Conditional
inclusion (option 3) was rejected as a new concept in the identifier machinery
with unaudited consumers; the loud-collision fix (option 4) is a different,
larger task and may still be filed separately.

## Why the scoping is structural, not conditional

`clipper` is resolved on `AbstractMLE.__init__` and exists nowhere else;
`nest/` and `mcmc/` contain zero clipper references and every nested/MCMC
search declares its own explicit `__identifier_fields__` tuple. So declaring
the field on the two MLE families cannot touch the nested samplers by
construction. Three test layers enforce it anyway: the pre-existing
`test_dynesty_static` hash pin (passed unchanged), new hash-list pins for
`Nautilus` / `DynestyDynamic` / `Emcee` / `Zeus` captured on `main` at
`c302f51` *before* the change, and a structural tripwire
(`assert not hasattr(af.Nautilus(), "clipper")`) that fails loudly if a future
refactor hoists `clipper` from `AbstractMLE` toward `NonLinearSearch`.

## The finding worth more than the change

Until this PR, `AbstractMultiStartGradient` and `AbstractBFGS` inherited the
base class's **empty** `__identifier_fields__ = tuple()`, so their identifier
hash list was literally `['MultiStartAdam']` — the class name and nothing
else. Not just the clipper but `n_starts`, `total_steps`, `learning_rate` and
every other result-affecting setting collided. The original prompt knew about
the clipper collision; the emptiness underneath it was found while grounding
the decision. Widening the tuple beyond `clipper` was deliberately kept out of
this PR (one prompt = one task) but re-keys are cheapest paid together —
raised as an open question on the PR; if wanted it needs its own prompt and a
field-by-field "does this affect the result?" audit.

## Behaviour change shipped

Every existing `MultiStart*` / `BFGS` / `LBFGS` output directory re-keys,
**including default-`ClipperNone` runs** — the hash gains the `clipper` field
itself (`['MultiStartAdam', 'clipper', 'ClipperNone']`). Stored results are
orphaned on disk, not deleted; re-running recomputes into a fresh directory.
`ClipperPriorBox`'s constructor args enter the hash via the identifier's
constructor-args walk, so different `margin`s fork too — no clipper-class
change was needed for that. Release notes for the next release must state the
re-key plainly (the PR body carries the text).

## Traps measured

- **`Drawer` inherits a clipper it never uses.** It sits under `AbstractMLE`
  so it carries the attribute, but `drawer/search.py` never consumes it — a
  setting that cannot affect the result must not re-key stored results, so
  `Drawer` deliberately does not declare the field, and a test asserts its
  identifier ignores an explicitly-passed clipper.
- **Float resolution in the identifier hash.** `ClipperPriorBox`'s
  `strict_epsilon=1e-12` hashes as `'0.0'` (the identifier rounds floats to
  `RESOLUTION`), while `margin=1e-06` survives distinctly. Sub-resolution
  differences in clipper constants will not fork the identifier — fine for the
  current constants, worth knowing before anyone adds a tiny tunable.
- **The phase-2 mitigation retires.** Unique per-arm `name`s to separate
  clipper arms (`complete/2026/08/clipper-validation-campaign.md`) are no
  longer needed for clipper comparisons.

## Workflow notes

- `worktree_check_conflict` flagged PyAutoFit as claimed by
  `stored-sample-reconstruction-guard` and `version-stamp-sync-guards`;
  proceeded on the human's explicit "go" — cloud session on its own branch, no
  local worktree contention, disjoint files, and those two tasks already claim
  PyAutoFit concurrently themselves.
- Environment: cloud session, no worktree; py3.13 venv with `.[jax]` extras.
  `pyauto-heart` unreachable → WORKFLOW.md pytest fallback gate.
- PyAutoFit branch `claude/clipper-search-identifier-4cowi2` (merged,
  deletable).

## Original prompt

# Put the clipper in the search identifier — MLE searches only, nested samplers untouched

Type: feature
Target: autofit
Repos:
- PyAutoFit
Difficulty: small
Autonomy: supervised
Priority: high
Status: formalised

Filed 2026-08-16 as the decision question owed by the prior-support `Clipper`
(`complete/2026/08/prior-support-clipper.md`, PyAutoFit#1477, follow-up 4).
**DECIDED 2026-08-18 by the human (James), recorded here per the original
prompt's "Whatever is chosen" clause.** The `Autonomy: human-required` header
this file carried existed only for that decision; with it made, the remaining
work is a small, mechanical, well-tested change — now `supervised`.

## The decision

**The clipper enters the search identifier — but only on the searches that
consume one, and the nested samplers' identifiers must stay byte-for-byte
identical.** That second clause is the load-bearing backwards-compatibility
constraint: nested-sampling runs are the long-lived, expensive, archived
results, and nothing about this change may re-key them.

This is option 2 of the original four ("include the clipper in
`__identifier_fields__`"), scoped to the clipper-consuming searches. Options
rejected, for the record:

- **Status quo (1)** — the collision is real and has already been stepped on:
  the phase-2 campaign (`complete/2026/08/clipper-validation-campaign.md`) had
  to work around it with unique per-arm names, and stacked with the
  `.completed` short-circuit a later run silently returns the earlier run's
  numbers.
- **Conditional inclusion (3)** — only-when-not-`ClipperNone` keeps existing
  directories but makes the identifier conditional, a new concept in that
  machinery with unaudited consumers (database, aggregator, `.completed`
  discovery). Not worth it for a one-time re-key of cheap MLE results.
- **Loud collision instead (4)** — refusing the `.completed` short-circuit on
  config mismatch fixes a broader hazard, but it is a different, larger task
  and does not make the identifier honest. May still be filed separately; it is
  not this task.

Accepted cost: **every existing `MultiStart*` / `BFGS` / `LBFGS` output
directory re-keys** — including runs using the default `ClipperNone`, because
the hash gains the `clipper` field itself. Stored results are orphaned, not
deleted. These are minutes-to-hours gradient fits, not the nested-sampling
archive; the trade was judged acceptable by the human. Release notes must say
so plainly (see "Whatever ships").

## Why this scoping already guarantees the nested samplers — verified

Verified against PyAutoFit `main` at `fe9f81337` (shallow clone, 2026-08-18):

- The identifier hashes `[search, model]` (+ `unique_tag` when set) —
  `autofit/non_linear/paths/abstract.py:279-283`.
- For any object declaring `__identifier_fields__`, **only** those attributes
  (plus the class name) enter the hash — `autofit/mapper/identifier.py:113-121`.
  An empty tuple means class name only.
- The base declares `NonLinearSearch.__identifier_fields__ = tuple()`
  (`abstract_search.py:318`). Neither `AbstractMultiStartGradient`
  (`mle/multi_start_gradient/search.py:23`) nor `AbstractBFGS`
  (`mle/bfgs/search.py:18`) overrides it — which is *why* the clipper never
  entered, and why today **nothing** search-specific on those searches enters
  (see "Latent finding" below).
- The `clipper` attribute is resolved on `AbstractMLE.__init__`
  (`mle/abstract_mle.py:16-22`), so it exists on `MultiStartAdam` /
  `MultiStartADABelief` / `MultiStartLion` / `MultiStartProdigy`, `BFGS` /
  `LBFGS`, and `Drawer` — and on nothing else.
- The nested samplers (`AbstractNest` → Nautilus, DynestyStatic,
  DynestyDynamic) and the MCMC searches (Emcee, Zeus, NUTS) do not inherit
  `AbstractMLE`, contain **zero** references to the clipper (`grep -rn clipper
  nest/ mcmc/` → 0 hits), and each declares its own explicit
  `__identifier_fields__` tuple (`nest/nautilus/search.py:25`,
  `nest/dynesty/search/static.py:14`, `nest/dynesty/search/dynamic.py:10`,
  `mcmc/emcee/search.py:26`, `mcmc/zeus/search.py:23`,
  `mcmc/blackjax/nuts/search.py:26`). Their identifiers are unchanged **by
  construction** — this task touches none of those classes.

## Implementation

1. Add `__identifier_fields__ = ("clipper",)` to `AbstractMultiStartGradient`
   and to `AbstractBFGS`. That is the entire source change. The identifier walk
   then hashes the clipper's class name plus its constructor-arg attributes
   (`identifier.py:127-128`), so `ClipperNone` hashes as its name and two
   `ClipperPriorBox`es with different margins hash differently — which is
   correct, since the margin moves where a lane can sit.
2. **`Drawer` is deliberately untouched.** It inherits the `clipper` attribute
   from `AbstractMLE` but never uses it (zero references in
   `mle/drawer/search.py`) and has its own `__identifier_fields__ =
   ("total_draws",)`. A setting that cannot affect the result must not re-key
   it.
3. No change anywhere under `nest/` or `mcmc/`.

## Tests — the nested-sampler guarantee is the point

- `test_dynesty_static`
  (`test_autofit/database/identifier/test_identifiers.py:389`) already pins
  DynestyStatic's exact hash list. It must pass **unchanged** — it is the
  existing regression guard for this task's hard constraint.
- Add sibling hash-list pins for `Nautilus` and `DynestyDynamic` (and ideally
  Emcee/Zeus/NUTS), **captured on `main` before the change** and asserted
  after, so "nested sampler identifiers unchanged" is a test, not a claim.
- Add a structural guard that the nested samplers have no `clipper` attribute
  (e.g. `assert not hasattr(af.Nautilus(), "clipper")`). This is the tripwire
  for the failure mode the human explicitly flagged: a future refactor hoisting
  `clipper` from `AbstractMLE` up to `NonLinearSearch` would silently put it
  within reach of the nest identifiers; this test makes that loud.
- MLE side: `MultiStartAdam()` vs `MultiStartAdam(clipper=ClipperNone())`
  identical (the default resolves to `ClipperNone`, so explicit-default must
  not fork); vs `ClipperPriorBox()` different; two `ClipperPriorBox` margins
  different; same trio on `LBFGS`.

## Latent finding — flag, do not fix here

Because their `__identifier_fields__` is the inherited empty tuple, the
identifier of a `MultiStartAdam` / `LBFGS` today contains **only the class
name**: `n_starts`, `total_steps`, `learning_rate`, and every other
result-affecting setting collide exactly like the clipper does. Since this PR
re-keys those directories anyway, widening the tuple in the same PR would pay
the orphaning cost once instead of twice — but that widens scope beyond the
decision recorded here, and which fields are "result-affecting" needs its own
audit. **Put the question to the human at PR time; default is clipper-only.**
If declined, file the widening as its own prompt so the finding is not lost.

## Whatever ships

- Release notes must state that multi-start and (L)BFGS output directories
  re-key (results orphaned on disk, not deleted), that nested-sampler and MCMC
  identifiers are unchanged, and that re-running an orphaned fit recomputes
  into a fresh directory.
- The phase-2 mitigation (unique `name` per arm when comparing clipper
  settings) becomes unnecessary for clipper comparisons once this lands; the
  campaign record already documents it as the historical workaround.

## Sequencing note

The original prompt tied this to "before phase 3" (the default flip). Phase 2
has since concluded with a **recommendation against flipping the default on
accuracy grounds** (`complete/2026/08/clipper-validation-campaign.md`), so the
entanglement concern is mostly moot — but the decision stands on its own: the
identifier should tell the truth about what produced a result, and the
collision it fixes has already bitten once. If phase 3 is ever revived, this
lands first, exactly as originally argued.

## Out of scope

- Flipping the clipper default (phase 3 — currently recommended against).
- The `.completed` short-circuit's general config-mismatch hazard (rejected
  option 4; file separately if wanted).
- Widening `__identifier_fields__` beyond `clipper` (see "Latent finding").
- Any change to `Drawer`, the nested samplers, or the MCMC searches.

<!-- Grounding: verified against PyAutoFit main at fe9f81337 (shallow clone,
     2026-08-18). Read mapper/identifier.py:81-159 (the walk, the
     __identifier_fields__ filter, the constructor-args fallback),
     non_linear/paths/abstract.py:279-283 (identifier composition),
     non_linear/search/abstract_search.py:318 (base empty tuple),
     mle/abstract_mle.py:16-22 (clipper resolution tier),
     mle/multi_start_gradient/search.py:23,709-712,1043 and
     mle/bfgs/search.py:18,122 (the two consumers), mle/drawer/search.py
     (0 clipper refs), nest/ + mcmc/ (0 clipper refs; explicit identifier
     tuples), test_autofit/database/identifier/test_identifiers.py:389
     (the DynestyStatic pin). Decision supplied by the human in the
     2026-08-18 session that produced this revision. -->
