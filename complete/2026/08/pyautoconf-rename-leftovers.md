- shipped: 2026-08-24 (PyAutoBrain#267 → PR #268, merge 2e7ea30)
- summary: Retired the PyAutoConf → PyAutoNerves rename leftovers across eight
  PyAutoBrain sites. Four were LIVE defects, all silent — nothing failed, the
  surfaces simply stopped seeing the Nerves repo.

## The root cause sat under the reported symptom

The prompt listed five sites and asked for per-site verification. The real
finding was one level down: `repo_aliases` split a single repo across **two
dead keys**. `@PyAutoConf` normalised to `autoconf` and `@PyAutoNerves` to
`pyautonerves`, and NEITHER is in the body map (`repos.yaml` names the repo
`PyAutoNerves`, category `organ`), so neither resolved to anything. That is why
`target_default_wiki` carried three rows for one repo — they were papering over
the split. Fix: `autonerves` is the single canonical key, with `pyautonerves`,
`autoconf` and `pyautoconf` aliased onto it — the shape the existing
`pyautobuild: pyautohands` entry had already established. Keeping the legacy
aliases rather than deleting them preserves routing for the ~150 archived Mind
prompts that say `@PyAutoConf` (same reasoning as
`complete/2026/07/rename-autobuild-to-autohands.md`, which kept `autobuild` as a
router keyword).

## The other three live defects

- `test_witness: autoconf: PyAutoConf/test_autoconf` — reachable only via the
  stale alias, pointing at a repo path that no longer exists. Confirmed live,
  not theoretical: `pyauto-brain refactor` reported `[unwitnessed: pyautonerves]`
  and advised "strengthen tests first" for a repo with a real suite.
- `release.relevant_repos` listed `PyAutoConf`; `nightly.sh:196` fetches
  `repos/<org>/$repo/commits` for each name verbatim.
- `hygiene.sh:147` timed `import autoconf`. A non-zero rc is recorded as
  `autoconf:n/a` and skipped, so Nerves import timing had been silently
  unmeasured since the rename. NOT in the prompt's list.

## Traps and findings

- **The prompt's redirect question could not be answered and was designed out
  instead.** It asked whether the nightly gate was still COUNTING PyAutoNerves
  activity through GitHub's renamed-repo redirect. A web-github session cannot
  test it — the agent proxy 403s `api.github.com` for both the old and new
  names, and `gh` is not installed. Rather than trust redirect behaviour, the
  gate now names `PyAutoNerves` directly and a new test pins every entry in
  `release.relevant_repos` to the body map. The HISTORICAL question is still
  open: whether quiet-night verdicts between the rename and this PR were judged
  on a repo the fetch could not see. Settling it needs one authenticated
  `gh api repos/<org>/PyAutoConf/commits` call.
- **Two sites were stale beyond the name.** `ensure_workspace_labels.sh`'s
  header claimed non-PyAutoLabs orgs (`rhayes777/PyAutoConf`,
  `rhayes777/PyAutoFit`, `Jammy2211/euclid_...`) while its own live `REPOS`
  array already listed all three under `PyAutoLabs/`;
  `skills/repo_cleanup/reference.md` mapped owners to `rhayes777`/`Jammy2211`.
  Both now defer to the body map's `github:` field. Only two non-PyAutoLabs
  homes remain in `repos.yaml` and neither is in that script.
- **A guard test found the eighth site.** `skills/OPERATIONS.md:41`
  ("autoconf lowercases YAML dict keys") is a live operational gotcha about
  current package behaviour, and no one had listed it. The repo-wide guard
  caught it on its first run.
- **The tenant firewall caught the agent's own drift.** Two drafts of the new
  tests hardcoded the org name and repo names in comments;
  `repos_sync.py --check` rejected both. The fix was to derive the assertions
  instead — which made them fork-safe as a side effect.
- **Pushed history is not rewritten here, so a commit-message overclaim was
  corrected on the PR instead.** The message says "157-test suite ... verified
  live". The PATH was verified properly (cloned the repo; `test_autonerves`
  exists with 17 `test_*.py` files); the COUNT was cited from
  `complete/2026/08/cli-noise-autonerves-batch.md` and not re-run. Recorded as
  an `idle` claim disposition rather than amended.

## Gate

Tests 467 pass (462 baseline + 5 new). `repos_sync --check` all 11 OK. Smoke n/a
(organism repo). Review CLEAN with three claim dispositions. **Heart NOT
EVALUATED** — `pyauto-heart` is unreachable from a web-github session, so leg 4
of the ship gate never ran; `autonomy_log.md` records it that way rather than
claiming a clean four-leg gate. Effective autonomy `supervised`; the run parked
at ship sign-off per the contract and resumed on human sign-off in the same
session.

## Follow-ups

- `#269` / PR #271 — the witness-map audit this task's sibling prompt asked for,
  shipped the same session.
- `draft/bug/pyautobrain/organ_repo_spellings_split_across_keys.md` — the bare
  organ spellings, still split.

## Original prompt

# PyAutoConf rename leftovers in Brain functional surfaces

Type: bug
Target: pyautobrain
Repos:
- PyAutoBrain
Difficulty: small
Autonomy: supervised
Priority: normal
Status: formalised
Filed: 2026-08-19 (backfilled from git)
Issued: 2026-08-24

Found by the 2026-08-19 readability census (#237). The PyAutoConf → PyAutoNerves
rename (package `autoconf` → `autonerves`) was fixed in the reader-facing docs
(ORGANISM.md, docs/example.md, skill prose), but these FUNCTIONAL sites still
carry the old name and need per-site verification, not a blind rename:

- @PyAutoBrain/config/policy.yaml:74 — unit-test location map entry
  `autoconf: PyAutoConf/test_autoconf`. Is the map keyed by package (should the
  key become `autonerves: PyAutoNerves/test_autonerves`?) and does anything
  still resolve the old path?
- @PyAutoBrain/config/policy.yaml:84 — the nightly activity gate's
  `relevant_repos` lists `PyAutoConf`. A renamed GitHub repo answers via
  redirect for some API calls but not all — verify whether activity on
  PyAutoNerves is being COUNTED by the gate today, then update the list (and
  check `tests/test_activity_gate.py:143`, which pins the old name in its
  fixture).
- @PyAutoBrain/bin/ensure_workspace_labels.sh:20 — comment names
  `rhayes777/PyAutoConf`; verify the script's live repo list.
- @PyAutoBrain/agents/conductors/health/health.sh:208 — comment example only.
- @PyAutoBrain/skills/repo_cleanup/reference.md:128 — "Owner mapping:
  PyAutoConf/PyAutoFit → `rhayes777`" is stale beyond the name: the body map
  says PyAutoLabs owns PyAutoNerves and PyAutoFit. Fix the mapping, and check
  whether any repo_cleanup behaviour actually keys on it.

Acceptance: grep for PyAutoConf/autoconf across PyAutoBrain returns only
deliberate historical references; the activity gate demonstrably counts a
PyAutoNerves commit; tests updated.
