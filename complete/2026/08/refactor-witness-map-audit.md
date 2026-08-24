- shipped: 2026-08-24 (PyAutoBrain#269 → PR #271, merge cf969f3; stacked on #268)
- summary: The witness-map audit `refactor_witness_map_missing_autonerves.md`
  asked for and never got. PyAutoNerves was not a one-off: `test_witness` had no
  row at all for PyAutoCTI or for five organs with real suites, and two more
  repos carried the same split-key defect.

## What the audit found

| Repo | Test dir (verified) | Before |
|---|---|---|
| PyAutoCTI | `test_autocti` | missing entirely |
| PyAutoReduce | `test_autoreduce` | keyed `pyautoreduce`; `@autoreduce` missed |
| PyAutoBrain / Heart / Hands / Memory / Mind | `tests` | missing |
| PyAutoGut | *none* | correctly absent — now documented as such |

`behaviour_preservation` reports any repo absent from the map as `unwitnessed`
and advises "strengthen tests first". For six tested repos that advice was
wrong, and wrong silently.

## Traps and findings

- **Convention would have produced six wrong rows.** The libraries follow
  `test_<package>`; the organs do NOT — Brain, Heart, Hands, Memory and Mind all
  keep a plain `tests/`. Every row was verified by reading each repository's own
  tree (blobless `--filter=blob:none --no-checkout` clone + `git ls-tree`), which
  is cheap enough to do for ten repos and is the only reason the organ rows are
  right.
- **The keying rule was implicit and is now written down** where the map lives:
  canonical key is the bare package name where the repo ships one, the repo name
  where it does not. That asymmetry is why the map looked arbitrary.
- **The guards were mutation-tested, not assumed.** Dropping the `autocti` row
  fails guard 1; dropping the `pyautoreduce` alias fails guards 1 and 2;
  restoring the original mis-keyed Reduce row fails all three. That last one is
  the real check — the pre-existing defect would now fail CI three ways.
- **The tenant firewall rejected two drafts of these tests** for hardcoding repo
  names, which forced the guards to derive everything from the body map. They
  are stronger for it and hold for an adopting fork.
- **Third instance of one defect class.** PyAutoNerves (#267), PyAutoCTI and
  PyAutoReduce (here). The shared cause is that `repo_aliases` is
  HAND-MAINTAINED while `KNOWN_REPOS` is DERIVED from the body map, so the two
  drift silently and the gap only ever surfaces as a wrong-but-plausible
  conductor message. Guard 2 closes the witness-map instance; an alias gap in a
  map with no coverage guard is still invisible.

## Deliberately not done

The bare ORGAN spellings still split: `_target_sets` registers both
`pyautobrain` and `autobrain` as known targets but only the prefixed form is
canonical, so `@autobrain`, `@autoheart`, `@automemory`, `@automind` and
`@autogut` resolve to keys nothing is filed under. Only `@autohands` was joined,
because `extra_organism_targets` declares it and it reaches real code today.
Fixing the rest requires deciding whether organs key bare or prefixed ACROSS
`target_signals` too — a routing-policy question, not a maintenance edit — so it
was filed rather than folded in:
`draft/bug/pyautobrain/organ_repo_spellings_split_across_keys.md`.

## Gate

Tests 468 pass. `repos_sync --check` all 11 OK. Smoke n/a (organism repo).
Review CLEAN, the lifted claim ("every row verified against the repository
itself") basis-cited by the tree reads. **Heart NOT EVALUATED** — unreachable
from a web-github session. Effective autonomy `safe` (header `safe`,
`maintenance` cap `safe`).

## Note on the intake that filed the follow-up

`pyauto-brain intake classify` scored the follow-up `bug` at high confidence
(kept) but proposed `Target: autocti` — it read the prior-instance history in
the draft as the subject — and `Difficulty: too-large`, inflated by the repo
names and design-decision keywords. Corrected to `pyautobrain` / `large` on
review. Worth knowing: the classifier keys on surface tokens, so a prompt that
narrates its own history misroutes.

## Original prompt

# Refactor Agent witness map lacks PyAutoNerves test suite

Type: maintenance
Target: pyautobrain
Repos:
- @PyAutoBrain
Difficulty: low
Autonomy: safe
Priority: low
Status: draft
Filed: 2026-08-19 (backfilled from git)
Issued: 2026-08-24

## Finding (2026-08-19, lazy-heavy-imports RefactorDecision)

`pyauto-brain refactor` reported `[unwitnessed: pyautonerves]` and advised
"strengthen tests first", but PyAutoNerves has a real suite
(`test_autonerves`, 157 tests, verified jax-less in the JAX-default arc).
The witness map only knows autoarray/autofit.

## Task

Add PyAutoNerves (`PyAutoNerves/test_autonerves`) — and audit the other
organ/library repos — to the Refactor Agent's witness map so refactor
decisions stop flagging witnessed repos as unwitnessed.
