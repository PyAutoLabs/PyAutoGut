## pyautoscientist-readme-two-paragraph-opening
- issue: https://github.com/PyAutoLabs/PyAutoScientist/issues/15
- completed: 2026-08-20
- workspace-pr: https://github.com/PyAutoLabs/PyAutoScientist/pull/16
- summary: PyAutoScientist README opening now matches the organ house pattern — one bold
  high-level intro paragraph starting "PyAutoScientist enables human-led, natural-language
  software development", then the Dashboard paragraph. The March-2026 transition history
  moved to a new "## Project History" section (after "The organs"), now explicitly naming
  PyAutoLens/PyAutoGalaxy/PyAutoFit/PyAutoArray/PyAutoCTI; the Docs/Adoption links moved
  below the organism-live strip. Mid-review refinement from the user reshaped the first
  draft (intro wording + history placement) before merge.

## Original prompt

# PyAutoScientist README — two-paragraph house-style opening

Difficulty: trivial
Autonomy: supervised

## Original request (verbatim)

> Like other repos, make the PyautoScientist README.md a single paragraph intro
> at a high level to introduce the project and then a second paragraph which
> goes to the dashboard

## Scope

@PyAutoScientist `README.md` only. Match the organ-README house pattern
(readability arc): title + badge → ONE bold high-level intro paragraph
(condensing the current three intro paragraphs: the March 2026 transition,
humans-describe-intent, natural-language-as-interface) → the existing
"See the PyAutoScientist Dashboard" paragraph → the `## The organism live`
strip section. The 📖 Docs / 🍴 Adoption guide links move below the strip
section. Marker-strip block and everything from "## From natural language to
trusted software" down stay unchanged.
