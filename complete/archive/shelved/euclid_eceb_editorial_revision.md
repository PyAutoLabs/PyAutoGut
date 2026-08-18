# Address ECEB editorial comments on ECLIPSE-C

@euclid_assistant

## SHELVED 2026-08-18 — retired from the Mind board at the author's direction

The ECLIPSE-C manuscript revision is no longer tracked here. Shelved rather than
recorded as complete: PyAutoMind cannot verify the deliverable either way, so
this file makes no claim about whether the editorial comments were addressed.

**Why it is untrackable.** The work targets a private paper checkout
(`/mnt/c/Users/Jammy/Science/euclid`), not a repo in the workspace. The
2026-08-08 orphaned-prompt triage filed it to `parked.md` as STATE UNVERIFIED
for exactly this reason, and nothing since has changed that — no session with
access to that checkout has reported back. A prompt whose state can only ever be
`unverified` is Mind-side residue, not a task.

**Nothing is open on GitHub.** This prompt carried no issue of its own. Its
assistant-side half — the `euclid_assistant` wiki/rules changes for the ECEB
editorial points — already shipped: issue
https://github.com/Jammy2211/euclid_assistant/issues/6 (CLOSED) via PR
https://github.com/Jammy2211/euclid_assistant/pull/8 (MERGED squash `2f4f2ee`,
2026-07-14), recorded at `complete/2026/07/eceb-editorial-revision.md`. That
record already flagged the manuscript companion as "a separate deliverable
outside this repo"; this commit closes that thread. Only the Mind-side residue
survived — this prompt, the `parked.md` entry, and the two dashboard rows — and
it is removed here.

**Preserved below** is the editorial board's letter verbatim (Peter's comments,
2026-07), which is the reason this file is archived rather than deleted. It is
the only copy in a tracked repo. If the revision is ever re-opened as tracked
work, re-file it from here via `$intake` — note the structural request
(reduce main-text systems to those actually discussed, move the rest incl. the
multi-page Fig.3 to an appendix) is the substantial item; the rest is line-level
copy-editing.


## Original request

You are working in /mnt/c/Users/Jammy/Science/euclid, can you address the comments from the editorial board, update the wiki where appropriate if you think a comment catches something missing, and give me a response to the comments w/ a fresh change log. Dear James,

thanks a lot for submitting your paper to the ECEB. It has been
carefully prepared, and thus I have only relatively few detailed
editorial comments -- see below. However, I think the paper would
profit from a reorganisation of the material: E.g., you describe Fig.9
(p.13) on p.7 -- also for other figures, the corresponding text is far
from the location of the figure, and switching between the two is
rather inconvenient. I wonder if it would not be better to reduce the
number of systems shown in the main text to those that you explicitly
discuss, whereas the other systems can move to an appendix -- in
particular, of course, the multi-page Fig.3. Perhaps also move the
description ofa figure (``a galaxy to the south abd additional objects
near the edge of the mask'') from the text to the figure
caption. Maybe this also is not ideal -- but I think it's worth to
give this a bit more thought and make the paper more attractive/easy
to read and appreciate.

Best regards
Peter

Please change title to

\title{Euclid Data Release 1 (DR1)}
\subtitle{The Euclid Lens Identification Pipeline and Scientific Exploration
(ECLIPSE). C: Lens modelling pipeline overview}

The 2990 is in red, since it will change for the final version. But I
guess many other number will change as well? Please make sure (as in
the other ECLIPSE papers) to indicate the preliminary results.

l.17: A&A does not like italics for emphasis, and certainly no \bf
(l.82, 657) in the text

l.52: point-spread function

l.84: 2\,000 --> 2000

l.84, 334, 821: Euclid --> \Euclid

Please avoid parentheses within parentheses. If needed, please use
[....(...)]. Also, please avoid ``) (‘’ in the text. E.g., l.110
[write ``... Lines et al. 2026, hereafter ECLIPSE-A''], 115, 120

l.139: ESA qants a reference to Datalabs and a note in the
acknowledgement

l.162: This manual workflow does not scale to samples of [> 2990 -->
thousands of] strong lenses

Minus signs must be in math mode -- that also applies to figures,
e.g., numbers on the axes, and tables. E.g., Figs.1, 2, l.196

I think you should give at least once the full official name of a source,
Euclid-DR1\,J030313.592$-$580619.97

Please use the Oxford comma consistently, e.g., l.199

Eq.(4): do you define what \xi is?

Consistency: \theta_{\rm E} vs. \theta_\sfornt{E}, e.g., l.271 vs. 273

A&A does not accept single sentence paragraphs; please merge with previous or following. E.g., l.328

l.335: please remove colon

l.342: Sect. A --> Appendix A

l.354: ; --> ,

You write definitions/naming conventions multiple times, e.g.  “Multi
Galaxy Lens (MGL)” (l.379, 386, 422, 430 ....), but also without
quotation marks in l.369. While for Multi Galaxy Lens you have an
acronym, you don't have one for Success, which you use with and
without quotation marks. This all appears quite
non-structured. Suggestion: Make a clear definition of the cases once
(e.g.: SC for success, FL for failure, MGL, DSPL, UIL) and use these
acronyms consistently thereafter -- this will increase the readability
of the paper

l.478-480; l.497--499, l.530--533: needed in this form (e.g., the
percentages could be deleted) -- it's a;; in the Table

Table 1 caption largly repeats the definitions that are in the text;
please delete.

l.535: ``through to'': correct?

Please don't write in Fig.3 ``follows the diagnostic-panel layout
introduced in Fig. 5'' -- wrong order.

Fig.3: ``the exact Success-vote fraction'': hmmmm -- with 18 inspectors,
how can one get an exact vote fraction of 75%?

I think you can delete ``The panel format is described in the main caption.'' from p.9, 10

Figs.4, 5: Panels (a)–(f) show the RGB image, VIS data, foreground
lens-light model, lens-subtracted image, lensed source-model image,
and source-plane reconstruction, respectively.: Copied verbatim;
please change

l.650: ``magnification formally diverges.'' only for point sources

l.661: ``denominator'': Of which fraction?

l.668: With this paper, strong lensing science enters the large-sample era: I disagree, it's not with this paper, but with DR1 + ECLIPSE team effort

l.709: under --> less than

Fig.14: vs --> vs.; why R_eff instead of \theta_eff

References need to be placed after acknowledgement

References:

Please use consistently A&A, ApJ, AJ, MNRAS, JCAP, PASP, ARA&A, Nat, Sci, etc. for the most often occurring journals.

Birrer, S., Shajib, A. J., Galan, A., et al. 2020, A&A, 643 [arXiv:2007.02941]: give paper number and remove arXiv

Etherington, A., Nightingale, J. W., Massey, R., et al. 2023b, arXiv:2301.05244
[arXiv:2301.05244]: arXiv twice, same for Stacey et al.

l.1051: arXiv:astr, 1 ??

Shajib, A. J., Nihal, N. S., Tan, C. Y., et al. 2025, dolphin: A fully automated
forward modeling pipeline powered by artificial intelligence for galaxy-scale
strong lenses: Bibliographic info missing

Wong, K. C., Suyu, S. H., Chen, G. C.-F., et al. 2020, MNRAS
[arXiv:1907.04869]: proper MNRAS infor, remove arXiv

## Scope

- Revise the private ECLIPSE-C manuscript and its fresh persistent changelog.
- Add or refine euclid_assistant wiki/rules only for editorial points supported by the Euclid Style Guide or official template conventions.
- Compile and re-audit the manuscript, test any assistant changes, and provide a point-by-point response to the editorial board.
