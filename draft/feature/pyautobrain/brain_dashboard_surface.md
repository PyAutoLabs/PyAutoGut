# feat: give the Brain a generated dashboard surface

Type: feature
Target: PyAutoBrain
Repos:
- PyAutoBrain
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised

Add a new dashboard capability to @PyAutoBrain: a generated, committed dashboard page the way the Mind has dashboard.md plus its GitHub Pages dashboard.html twin, so more of the Brain becomes a standing page like the other organs rather than output that exists only inside a live session.

Today every Brain surface - the community scan, health, hygiene, vitals, the intake census - is emitted into a session and then lost. There is no committed read-only page a human can open on a phone to see what the Brain currently thinks. Add a renderer that emits the conductor and faculty surfaces as a committed markdown page plus an HTML twin deployed by GitHub Pages, regenerated on push and drift-checked the way the Mind dashboard self-heals, carrying the same one-tap-copy affordance that routes a tap on the page back into a session.

Open design questions for the human, not settled here: which surfaces belong on a standing page at all (some, like vitals, are only meaningful live and may need a freshness stamp rather than a cached verdict); whether the page is one Brain page or one per conductor; and whether regeneration is cheap enough to run on every push given some surfaces make network calls.

Also add a GitHub REST fallback to the community conductor, the data-path feature that makes such a page trustworthy. The conductor shells out to the gh CLI, which does not exist in Claude Code web and remote containers, so the entire scan aborts with 'cannot run gh api'. Observed 2026-08-22: a gh api shim over curl was refused by the session sandbox classifier, and the fallback of attaching repos one at a time was partially refused too, so PyAutoNerves, HowToLens, PyAutoCTI and several assistant repos went unscanned - the scan was best-effort and silently under-reported who was waiting, which is exactly the failure a dashboard must not inherit. Adding a REST fallback when gh is absent, or installing gh in the environment, makes the surface complete and machine-readable from any harness, turning it into a real dashboard data source instead of something only a CLI session can produce.

Phasing note: these are two legs of one goal - the page, and the data path that makes the page honest. Expect start_dev to split them into phased PRs, REST fallback first so the dashboard is built on a complete surface.

<!-- formalised by the Intake (Conception) Agent on 2026-08-22 from user-intake -->
