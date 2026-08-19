## readme-scientist-buttons
- issue: https://github.com/PyAutoLabs/PyAutoScientist/issues/11 (closed)
- completed: 2026-08-19
- commits: direct to main (matching the precedent commit "Link PyAutoScientist repo at top of README") — PyAutoMind deec2b6f, PyAutoBrain f1cdc9d, PyAutoHeart 894c982, PyAutoHands c6a5c74, PyAutoGut 9819707, PyAutoNerves 450594b, PyAutoMemory 9fcd105; all verified on origin/main via ls-remote.
- what shipped: the two-sentence PyAutoScientist header prose at the top of the seven organ READMEs replaced by one line of two shields.io `for-the-badge` buttons — "PyAutoScientist GitHub" (color 181717, per-repo science emoji: Mind 🔭, Brain ⚛️, Heart 🔬, Hands 🧪, Gut 🧫, Nerves ⚗️, Memory 🧮) and "PyAutoScientist ReadTheDocs" (📖 kept, color 8CA1AF). Emoji are percent-encoded inside the badge URL; shields serves them in the SVG label (verified by curl, 200 + emoji present in `<text>`).
- sizing override: `pyauto-brain feature` scored too-large(15) → 4 phases off repo count; overridden as a uniform two-line cosmetic swap per the recorded repo-count-proxy feedback, shipped as one task, override recorded in the issue body.
- trap for later: `for-the-badge` uppercases the label ("PYAUTOSCIENTIST GITHUB") — that is baked into the style, not an encoding bug; switch to `flat-square` in the badge URL if branded casing is ever wanted over the button look.
- PyAutoMemory carried an unrelated dirty `reading-queue.md` throughout; only README.md was staged (verified via `git show --stat`).

## Original prompt

# Replace organ-repo README header prose with PyAutoScientist buttons

Type: docs
Target: pyautoscientist
Repos:
- PyAutoMind
- PyAutoBrain
- PyAutoHeart
- PyAutoHands
- PyAutoGut
- PyAutoNerves
- PyAutoMemory
Difficulty: easy
Autonomy: supervised
Priority: normal
Status: formalised

Original request (verbatim):

> The README.md of the PyAuto scientist repos all begin with somethingl ike
> this 🧬 PyAutoScientist → https://github.com/PyAutoLabs/PyAutoScientist —
> this repo is one organ of the PyAuto organism.
> 📖 Full documentation → https://pyautoscientist.readthedocs.io — the whole
> PyAutoScientist organism, including how to fork and run your own. Instead of
> a full description of PyAutoScientist, which dedicated two sentenses before
> explaining the repo itself, can you make these clickable buttons which say
> "PyAutoScientist GitHub" and "PyAutoScientist ReadTheDocs". I like the emoji
> game, for docs keep the scroll but for PyAutoScietist can you either make it
> a random emoji which is sciencey or if thats too hard a different science
> emoji for each repo.

Scope: the identical two-line header block in the README.md of the seven organ
repos (@PyAutoMind @PyAutoBrain @PyAutoHeart @PyAutoHands @PyAutoGut
@PyAutoNerves @PyAutoMemory) becomes two clickable badge buttons —
"PyAutoScientist GitHub" (a different science emoji per repo) and
"PyAutoScientist ReadTheDocs" (keeps 📖) — dropping the two explanatory
sentences.
