Removed the vestigial `jax<0.7 jaxlib<0.7` pin from `.github/scripts/smoke_install.sh`
in both `autolens_workspace_test` and `autogalaxy_workspace_test`, and replaced the
accidental correctness with an asserted one.

## PRs

- autolens_workspace_test#268 — MERGED (`9348e152`), 3/3 legs green, closes #266
- autogalaxy_workspace_test#107 — MERGED (`0a91883d`)

## What the pin actually was

The prompt asked to establish what the pin protected before deleting it. Git history
answered it outright, and the answer was stronger than "probably stale":

| Date | Commit | Event |
|------|--------|-------|
| 2026-05-08 | `91c818a` (#82) | Pin added, for one stated reason: keeping `tensorflow-probability==0.25.0` importable, since `tfp.substrates.jax` referenced `jax.interpreters.xla.pytype_aval_mappings`, removed in JAX 0.7.0 |
| 2026-07-10 | `35ae97b` | Line carried verbatim from `smoke_tests.yml` into the new `smoke_install.sh` |
| 2026-07-19 | `fb7a4e7` (#184) | `pip install tensorflow-probability==0.25.0` deleted; stack moved to tfp-nightly. The pin's sole protected object ceased to exist. |

It was not merely inert. jax is a **base** dependency of autonerves
(`jax>=0.7.0,<0.12.0`, PyAutoLens#702), so the preceding line already installed a
conforming jax; the pin downgraded it to 0.6.2 — unsupported — and only the following
`[optional]` re-resolution repaired it. Correct by line ordering, not by constraint.

## The trap worth remembering: delete a stale pin, don't restate it

The prompt offered "remove it **or** replace it with a pin stating the real intended
range", and quoted autonerves as `jax<0.11.0,>=0.7.0`. That quote was **already stale**
— the cap had moved to `<0.12.0`. Had the pin been rewritten at the quoted range, CI
would have been held a full minor version behind the supported one.

CI proved this concretely: with the pin gone the resolver landed on **jax 0.11.1**, not
the 0.10.2 the prompt observed, and the full suite passed there on 3.12 and 3.13.
`incompatible` no longer appears in the install log at all.

General form: a constraint restated in a second place drifts from its owner. Assert the
range; don't own a copy of it.

## What was added

A post-install assertion, so the resolved version is checked rather than inferred from
a green run:

```bash
python - <<'JAXCHECK'
import jax
major, minor = (int(part) for part in jax.__version__.split(".")[:2])
assert (0, 7) <= (major, minor) < (0, 12), (...)
print(f"resolved jax {jax.__version__}")
JAXCHECK
```

Deliberate choices: a major/minor **tuple** rather than `packaging.version` (the guard
runs inside the install step, where a missing import fails the install rather than
failing softly, and the epilogue does not declare `packaging`); `import jax` unguarded
(the workflow runs on `ubuntu-latest`, where autonerves' platform marker always installs
jax, so an absent jax is itself worth catching).

## Sibling sweep

`autogalaxy_workspace_test` carried the identical line — hence the second PR, widening
the task beyond the prompt's declared single repo. `autocti_workspace_test` and
`autofit_workspace_test` were checked and carry no jax pin. In the autogalaxy copy the
issue references are qualified as `autolens_workspace_test#82` / `#184`, since bare
numbers would resolve to unrelated issues in that repo.

## Loose end, filed separately

`autogalaxy#107`'s smoke suite **hung** on `imaging/jax_likelihood/mge.py` — 59 minutes
of zero output, orphan python processes at teardown. Not this change: the same script
passed in 29.7s under the same jax 0.11.1 in autolens (23/23), and a re-run of the
identical commit did not reproduce the stall. It is a known pattern in that repo (four
prior runs at ~6h against an 11-14min norm; a sibling JAX script already parked for it).
Filed as `draft/bug/workspaces/intermittent_smoke_hang_jax_mge.md`.

`autogalaxy#107` was merged with its re-run still in flight, on the strength of the
identical autolens change being green — a judgement call the human made explicitly. The
follow-up's per-script-timeout item is what would make that call unnecessary next time.

## Environment note

Shipped from a web-github session: no local worktree, branched in the session clones,
so the `active.md` entry carried no `worktree:` field. The Heart gate returned STALE
(no library checkouts / report.json in-session) with zero red and zero yellow reasons;
per `agents/faculties/vitals/AGENTS.md` the dev-ship gate treats STALE as passing, since
an evidence gap is organism-scope, not branch-scope.

## Original prompt

# smoke_install.sh's stale `jax<0.7` pin — CI is on the right jax by accident

Type: maintenance
Target: ci
Repos:
- @autolens_workspace_test
- @autogalaxy_workspace_test
Difficulty: low
Autonomy: supervised
Priority: medium
Status: formalised
Filed: 2026-08-22 (backfilled from git)
Issued: 2026-08-23

Found 2026-08-22 while building a CI-equivalent environment to reproduce
autolens_workspace_test#260. Latent — CI is green today — but it is green for the
wrong reason.

## The defect

`autolens_workspace_test/.github/scripts/smoke_install.sh:9`:

```bash
pip install "jax<0.7" "jaxlib<0.7"
```

Replaying the install script verbatim, that line **downgrades jax to 0.6.2** and
raises a resolver conflict against autonerves' own requirement:

```
autonerves 9999.0.0.dev0 requires jax<0.11.0,>=0.7.0; ... but you have jax 0.6.2
which is incompatible.
Successfully installed jax-0.6.2 jaxlib-0.6.2
```

The install only ends up on the intended **0.10.2** because the *next* line's
`[optional]` extras happen to pull it back up:

```bash
pip install "./PyAutoArray[optional]" "./PyAutoGalaxy[optional]" "./PyAutoLens[optional]"
```

## Why it matters

The pin no longer expresses the intent it was written for, and the correct
outcome now depends on line ordering rather than on the constraint. Any
reordering of those two lines, or a change to what the `[optional]` extras
resolve, would silently drop the entire smoke suite onto jax 0.6.2 — and because
`autonerves` declares `jax>=0.7`, that is a configuration the stack does not
claim to support. The failure would surface as unexplained smoke breakage, not as
an install error.

The comment block immediately below that line (about `tfp-nightly` vs
`tensorflow-probability`) is still accurate and should be preserved.

## Suggested scope

1. Establish what the `jax<0.7` pin was originally protecting against, and whether
   that reason still holds — do not simply delete it because it looks stale.
2. Either remove it (letting `autonerves`' `jax<0.11.0,>=0.7.0` govern) or replace
   it with a pin that states the real intended range.
3. Verify by replaying the install from scratch and asserting the resolved jax
   version, rather than inferring it from a green run.
4. Check whether sibling workspaces' install epilogues carry the same stale pin.

<!-- Sizing: declared low; the sizing faculty derives medium (5). Kept at low — the
     change is one line plus a verification replay; the prompt is long because the
     evidence is, not because the work is. -->

<!-- Not filed as a GitHub issue at discovery time: unrelated to the bug being
     worked (autolens_workspace_test#260), and deliberately not folded into it. -->
