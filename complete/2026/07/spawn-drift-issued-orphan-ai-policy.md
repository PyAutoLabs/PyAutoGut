- issue: none (same-session continuation of the 2026-07-27 /wake_up red-jobs sweep)
- prs: PyAutoMind#113 — MERGED; both templates republished (spawn: regenerate from e4548f8)
- summary: |
    PyAutoMind/spawn_drift red. THREE stacked spec gaps, each surfacing only
    once the previous one was cleared:

    1. issued/remove_pulse_compat.md — sole survivor of the retired flat
       issued/ pile. The lifecycle split (#71/#72) repointed spawn.py's
       ("issued/*", "DROP") rule to ("active/*", "DROP"), leaving this one file
       matching NO rule -> DROP + WARN -> exit 1. Pure orphan: the work was done
       (PyAutoPulse gone, no pulse refs in PyAutoHeart) and already recorded at
       complete/2026/07/remove-pulse-compat.md. Deleted.
    2. AI_POLICY.md — added org-wide the same day with no rule, so it became the
       next UNMATCHED the instant (1) cleared. Names the owning org twice ->
       KEEP_SUB, not verbatim KEEP.
    3. CONTRIBUTING.md — was KEEP verbatim. The same day's centralisation
       rewrote it to "# Contributing to PyAutoLabs", so a republish would have
       stamped PyAutoLabs branding into a fresh-slate template spawned for
       someone else's org. Moved to KEEP_SUB in both rule sets.

    Clearing the spec gaps was necessary but NOT sufficient: the job also failed
    on content drift, cleared by republishing both templates.

    Also repointed planned.md's jax-point-source-point-smoke-sentinel entry,
    which pointed at issued/jax_point_source_point_smoke_sentinel.md — a
    130-line diagnostic prompt dropped as "legacy" by the lifecycle migration
    while the task stayed planned and UNFIXED. Restored verbatim to
    draft/bug/autolens/.
- verification: |
    spawn.py --check: "unmatched: none" + "canary scan: clean" for both, then
    OK/OK exit 0 against freshly cloned published repos. Real spawn_drift run
    dispatched on main: SUCCESS (run 30298558351).
- traps: |
    TRAP: spawn.py --check reads the GIT INDEX, not the filesystem. An UNSTAGED
    deletion still shows as UNMATCHED — `git add` first or the check lies.
    TRAP: fixing one UNMATCHED reveals the next; the check reports one class at
    a time, so re-run after every rule change rather than assuming you are done.
    TRAP: `git add -A` in the SHARED PyAutoMind checkout swept a concurrent
    session's draft->active move onto this branch. Recovered by merging
    origin/main (net diff back to own files only) — but the real lesson is do
    not branch the shared Mind checkout, and commit explicit paths only.
    NOTE: README.md pointers to PyAutoScientist/PyAutoBrain and repos_sync.py's
    tenant-firewall baseline still contain literal "PyAutoLabs" in the templates.
    Pre-existing and arguably intentional (reference-implementation pointers +
    generator machinery); the canary scan passes. Not addressed.
