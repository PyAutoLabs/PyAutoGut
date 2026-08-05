# Add a --detail flag to the hygiene config scan so

Type: feature
Target: PyAutoBrain
Repos:
- PyAutoBrain
Difficulty: small
Autonomy: safe
Priority: normal
Status: formalised

Add a --detail flag to the hygiene config scan so its findings are routable. The config scan in PyAutoBrain agents/conductors/hygiene/_hygiene_config.py emits only a 'count|summary' line naming how many library config keys are absent downstream and a per-target tally. Its main() accepts only --root and prints that one line, so there is no way to see which key paths actually drifted. The hygiene skill tells the operator to route config findings onward for repair, but the mode hands over nothing routable: recovering the key paths currently means importing the module and re-running its diff() internals by hand. Add a --detail flag that prints each drifted key path grouped by the config file it is missing from, keeping the existing single-line output as the default so the conductor's summary table is unchanged. Extend the same treatment to the orphan_files signal the module already computes.

<!-- formalised by the Intake (Conception) Agent on 2026-08-05 from user-intake -->
