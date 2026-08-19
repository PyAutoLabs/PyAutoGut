Tenant firewall: release_run.py's hardcoded 'PyAutoLabs' — already fixed on
Heart main the day after filing; verified and retired without dev work.

- issue: (none — no dev work remained; verified already fixed at start_dev, 2026-08-19)
- completed: 2026-07-31 — PyAutoHeart commit `92d93d8` on `main` ("Derive the
  release-channel repo slug from the checkout origin"), a direct follow-up to
  the release-channel-freshness feature (PyAutoHeart#129, see
  `complete/2026/07/release-channel-freshness.md`) that had introduced the
  hardcoded fallback the day before.
- prompt: draft/bug/pyautoheart/tenant_firewall_release_run_instance_fact.md (folded below)
- summary: the prompt reported `heart/checks/release_run.py:42` hardcoding the
  `PyAutoLabs` org name as the `GITHUB_REPOSITORY` fallback — the sole tenant
  firewall mismatch on 2026-07-30. The fix took the prompt's first suggested
  option (derive, don't allowlist): `_own_repo_slug()` now derives the
  owner/repo slug from the checkout's own git origin, the same identity source
  the firewall's local-checkout check uses; with no origin the gh-backed
  callables fail and the check reports unavailable instead of guessing. The
  docstring cites the tenant firewall as the motivation. `release_run.py`
  correctly carries **no** `FIREWALL_ALLOWLIST` entry.

## Verified at retirement (2026-08-19)

- `heart/checks/release_run.py` on PyAutoHeart `main` (`7659f15`) contains no
  firewall token; the slug is derived via `_own_repo_slug()` with
  `GITHUB_REPOSITORY` taking precedence in CI.
- `python3 PyAutoMind/scripts/repos_sync.py --check --only "tenant firewall
  (organ code)"` → **OK** with PyAutoHeart checked out at the root (the
  organ-must-be-present trap from `complete/2026/08/tenant-firewall-drift-aug.md`
  was respected — a Heart checkout was attached before trusting the OK).
- This draft was NOT one of the 9 mismatches of the Aug arc (issue #198 /
  `tenant-firewall-drift-aug.md`, which lists it as "a separate open draft") —
  those all postdated this fix. Nothing from that arc re-touched the
  `release_run.py` fallback.

## Note

The fix shipped one day after the prompt was filed, outside the Mind workflow
(direct commit to Heart main, no issue), so the draft sat open for three weeks
after its subject was resolved. `intake reconcile` / `lifecycle.py issues
--drafts` could not catch it: no issue or PR ever referenced the draft, and it
declared no `Closes-when:` gate — the staleness-detection blind spot recorded
in `complete/2026/08/draft-staleness-detection-signals.md` (a fix with no
Mind-side trace is only reachable by the upstream `--repo` read).

## Original prompt

# Tenant firewall: release_run.py carries an unlisted 'PyAutoLabs' instance fact

Type: bug
Target: pyautoheart
Repos:
- @PyAutoHeart
Difficulty: small
Autonomy: safe
Priority: normal
Status: draft

`python3 PyAutoMind/scripts/repos_sync.py --check` reports the sole manifest
mismatch keeping Heart readiness YELLOW:

```
check tenant firewall (organ code): 1 mismatch(es)
  ✗ PyAutoHeart/heart/checks/release_run.py: new instance fact(s) in unlisted file — 'PyAutoLabs' (line 42)
```

`heart/checks/release_run.py:42` hardcodes the `PyAutoLabs` org name in organ
code that the tenant firewall does not list as instance-fact-bearing. Fix by
whichever is correct: derive the owner from `PyAutoMind/repos.yaml` /
existing config plumbing like the other checks do, or (if the fact is
legitimately local to this file) add the file to the firewall's allowlist in
the repos_sync manifest. Found 2026-07-30 by /wake_up; it is the only YELLOW
manifest reason in `pyauto-heart readiness`.
