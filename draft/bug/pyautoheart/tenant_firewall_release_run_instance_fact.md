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
