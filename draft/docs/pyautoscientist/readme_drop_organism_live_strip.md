# PyAutoScientist README — drop the organism-live strip and repo-status blockquote

Difficulty: trivial
Autonomy: supervised

## Original request (verbatim)

> remove this is redundant with dashboard stuff nw: The organism live
> Mind 2 in flight · 3 parked · 6 planned · 149 backlog · Heart STALE · 65 ·
> Hands 2026.8.20.1 · 15h ago · Memory 166 pages · 40% cited
>
> This repository is currently the home of the PyAutoScientist documentation,
> shared policies and links to its constituent repositories. The ecosystem is a
> working system used for daily PyAutoLabs development, but its installation
> and adoption process is still being prepared for wider use., also make these
> two lines: 📖 Docs: https://pyautoscientist.readthedocs.io 🍴 Adoption guide:
> https://pyautoscientist.readthedocs.io/en/latest/adoption/guide.html

## Scope

@PyAutoScientist only. Remove the README's `## The organism live` section
(scientist:begin/end markers + strip — redundant with the dashboard bullets)
and the "This repository is currently the home…" blockquote; render the 📖
Docs / 🍴 Adoption guide links as two lines (hard break) right after the
dashboard bullets. Also remove the now-dead "Update the README strip" step
(and its `--md-brief > readme_strip.md` render) from `organism_board.yml`;
`board.py --md-brief` itself stays.
