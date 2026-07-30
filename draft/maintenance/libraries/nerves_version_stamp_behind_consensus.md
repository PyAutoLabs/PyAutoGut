# PyAutoNerves committed version stamp behind sibling consensus

Type: maintenance
Target: libraries
Repos:
- @PyAutoNerves
Difficulty: small
Autonomy: safe
Priority: low
Status: draft

`PyAutoBrain/bin/version_drift.sh` (2026-07-30) reports:

```
✗ PyAutoNerves  2026.7.9.1 (≠ consensus 2026.7.23.1)
✓ PyAutoArray/PyAutoFit/PyAutoGalaxy/PyAutoLens  2026.7.23.1
```

`PyAutoNerves/autonerves/__init__.py:113` still carries `2026.7.9.1` while the
four coupled libraries carry `2026.7.23.1` — Nerves missed the pre_build stamp
sweep that aligned the others (releases themselves are unaffected; autonerves
`2026.7.29.2` shipped fine, the committed stamp is deliberately not bumped on
release). Align the stamp with the siblings and check why the pre_build
stamping step skipped Nerves so it doesn't drift again. Also: the drift script
reports the three workspace stamps as "(stamp unresolved)" — while in there,
check whether its workspace-stamp lookup is stale.
