## release-ships-simulated-datasets (Group A — all 4 legs complete & MERGED; Group B separate)
- issue: https://github.com/PyAutoLabs/PyAutoBuild/issues/126 (CLOSED)
- completed: 2026-07-13 (--auto supervised; user greenlit "go" + route purges via PyAutoGut; merges human-directed)
- prs: PyAutoBuild#150 (leg1 `-f` drop + leg4 `autobuild/check_dataset_allowlist.py`) + autolens_workspace#272 (~207 files purged) + autogalaxy_workspace#129 (~107) — all MERGED (squash) 2026-07-13. Merged workspaces-first, guard-last (nightly-release safety).
- summary: `pre_build.sh`'s `git add -f dataset/` force-committed simulated datasets against each workspace `.gitignore` allowlist (the disproven "15×15 smoke" framing of #126). Fix: **leg 1** drop `-f`; **leg 2** MOOT (workspaces already self-provision via the older `not dataset_path.exists(): subprocess.run([...simulator...])` idiom — 130+ scripts; the prompt's "7 unguarded" and an interim "16 needs-guard" were both wrong, keyed on the `should_simulate` string); **leg 3** purge every non-allowlisted regenerable dataset via **PyAutoGut** (`condemned.md` type:file, sweep-after 2026-08-13, archive-ref = pre-purge fork SHA 8625a1de/e940f8cd, in main history); **leg 4** allowlist-based guard in pre_build (allowlist-presence-gated so bare-`dataset/` Group-B repos skip). Final smoke autolens 9/9 + autogalaxy 8/8 (re-run after every purge).
- key traps / findings: guard signal is the simulator-subprocess, NOT the `should_simulate` string (topic-namespaced dataset_names; `samples` is `dataset_label="samples"`+`dataset_sample_name`, nested → guarded by advanced graphical/hierarchical/EP guides). Leg-4 guard **caught a leak the manual audit missed** — `dataset/imaging/los_halos` mixed real-looking `.npy` + simulated `.fits`; on inspection simulator.py `np.save()`s the `.npy` too (output, nothing reads them) so BOTH purged + de-allowlisted. User calls: `interferometer/simpleold` killed (dead); `interferometer/many_visibilities` kept→allowlisted (active); autogalaxy `database/simple__{0,1,2}` kept→allowlisted (committed-by-design aggregator = Group-B b2). `interferometer/dark_matter_subhalo` (sim-only, no consumer) purged. gh traps hit: `gh pr edit` fails Projects-classic (use `gh api PATCH`); `sed s///` breaks on `9/9` slash (use python).
- Group B: `bug/pyautobuild/release_datasets_group_b_policy.md` (autofit/HowToFit/HowToGalaxy/HowToLens bare-`dataset/`; leg-4 guard skips them until they adopt allowlists).
- worktree ~/Code/PyAutoLabs-wt/release-ships-simulated-datasets — safe to remove (all merged; PyAutoHeart branch unused).

## Original prompt

# Release pipeline force-commits simulated workspace datasets; add missing should_simulate guards, purge committed sim data, stop the -f leak

Type: bug
Target: PyAutoBuild
Repos:
- PyAutoBuild
- PyAutoHeart
- autolens_workspace
- autogalaxy_workspace
- autofit_workspace
- HowToLens
- HowToGalaxy
- HowToFit
Difficulty: large
Autonomy: supervised
Priority: high
Status: formalised

Release pipeline force-commits simulated workspace datasets against .gitignore; the real defect is example scripts that load simulated data WITHOUT the should_simulate() auto-simulate guard. Supersedes the old framing in issued/release_ships_smoke_datasets.md (PyAutoBuild#126, which said "regenerate datasets full-size" — disproven).

CORRECTED DIAGNOSIS (researched 2026-07-13, deeply, with the user):
- Design intent (encoded in each workspace .gitignore): dataset/** is gitignored except a small allowlist of REAL observational data un-ignored via ! lines (autolens: cosmos_web_ring, slacs1430+4105, double_einstein_ring, mass_stellar_dark, extra_and_scaling_galaxies, a few group/cluster/interferometer dirs, los_halos npy). All SIMULATED datasets are meant to be generated at runtime, never committed.
- The self-provision mechanism ALREADY EXISTS: al.util.dataset.should_simulate(dataset_path) (in autoarray util) returns True when data is missing (and, under PYAUTO_SMALL_DATASETS=1, deletes existing data so the simulator re-creates it at 15x15). The standard idiom is: `if al.util.dataset.should_simulate(str(dataset_path)): subprocess.run([sys.executable, "scripts/.../simulator.py"], check=True)` then Imaging.from_fits(...). See scripts/imaging/modeling.py:94-108 for the canonical example.
- Two coupled bugs: (1) pre_build.sh:64 runs `git add -f dataset/` — the -f FORCE-OVERRIDES .gitignore, committing simulated datasets that should be ignored (autolens: 242 tracked files / 8.1MB across 33 dirs are non-allowlisted; many are also degenerate 15x15 because a smoke run PYAUTO_SMALL_DATASETS=1 generated them in the checkout before pre_build). (2) a MINORITY of example scripts load simulated data WITHOUT the should_simulate guard, so they only work because the -f leak committed the data for them.
- autolens_workspace audit (190 from_fits scripts): 29 load only real/allowlisted data (correct, stays committed); 104 load simulated data WITH a should_simulate guard (correct, self-provision); 7 load simulated data with NO guard = THE DEFECT (mostly scripts/imaging/data_preparation/gui/* + manual/* + guides/results/latent_variables.py, loading simple__no_lens_light / extra_galaxies / lens_sersic).
- generate.py does NOT execute simulators (jupytext script->notebook conversion only), so the build isn't shrinking data — it's force-committing whatever a prior smoke run left on disk.

FOUR-LEG FIX (tractable — NOT an epic; no notebook-prose rewrite, no simulator compute):
1. Stop the leak: drop the -f from `git add dataset/` in PyAutoBuild/pre_build.sh so staging honors .gitignore; only allowlisted real data can ever be staged. (Already-tracked real data stays tracked — dropping -f does not untrack it.)
2. Fix the problem set: add the should_simulate()+simulator-subprocess guard to the unguarded scripts (mirroring modeling.py:96-102) so they self-provision like the other 104.
3. Purge: git rm the non-allowlisted committed simulated datasets so the tree matches .gitignore intent. Users/CI/Colab regenerate via the simulators.
4. Guard: a check asserting `git ls-files dataset/` contains nothing outside the .gitignore allowlist (allowlist-based, NOT git check-ignore-based — see caveat), wired as a PyAutoHeart leg or a pre_build assertion, so it can't recur.

CROSS-REPO AUDIT REQUIRED (the autolens numbers above are ONE repo): run the same allowlist-vs-tracked + guarded-vs-unguarded audit across autogalaxy_workspace, autofit_workspace, HowToLens, HowToGalaxy, HowToFit (and sanity-check the *_workspace_test repos). Report per-repo: count of non-allowlisted committed datasets, count of unguarded simulated-data loaders, and total committed-data size. Each repo has its own .gitignore allowlist that is the source of truth.

ADVERSARIAL CAVEATS to verify during execution:
- NOTEBOOK/COLAB CWD RISK: the guard's subprocess uses a RELATIVE path ("scripts/.../simulator.py") that resolves from the workspace root but may break in notebooks (nbconvert CWD = notebook dir). This morning's workspace-validation run had run_notebooks failures — possibly linked. MUST verify the should_simulate subprocess resolves in notebook + Colab execution BEFORE purging data; if not, purging breaks notebooks even with guards (may need a root-anchored path or a setup_notebook chdir).
- ORPHAN DATASETS: some purge candidates have no consumer and no simulator (autolens: interferometer/many_visibilities, simpleold). Classify each purge candidate as {guarded-consumer + simulator exists → purge safe}, {no consumer → dead, purge}, {consumer but no simulator → needs attention, do not blind-purge}.
- .gitignore re-include subtlety: `dataset/**` + `!dataset/X/**` negations may not actually re-include under git's "can't re-include if parent excluded" rule; the allowlisted real data is currently tracked (so shipping is fine), but the leg-4 guard must be allowlist-based, not `git check-ignore`-based (which mis-flags both tracked files and negated paths).

CONSTRAINTS: autolens_workspace is currently claimed by the active lenstool-scaling task (PR#267) — its leg-2/leg-3 work must coordinate or wait. Difficulty: medium. Autonomy: supervised. This is workspace + PyAutoBuild-pipeline + a PyAutoHeart guard leg (library-first: pipeline + guard, then per-workspace). Retire/supersede issued/release_ships_smoke_datasets.md and update PyAutoBuild#126 to the corrected diagnosis.

<!-- formalised by the Intake (Conception) Agent on 2026-07-13 from file:/tmp/claude-1000/-home-jammy-Code-PyAutoLabs/1d6139c3-b7f4-46d0-805e-f13b5bf2a8ea/scratchpad/intake_smoke_datasets.md -->
