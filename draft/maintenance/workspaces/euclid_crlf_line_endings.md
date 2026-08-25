# euclid: CRLF has reached the HPC submit scripts AGENTS.md warns about

Type: maintenance
Target: workspaces
Repos:
- euclid_strong_lens_modeling_pipeline
Difficulty: small
Autonomy: supervised
Priority: normal
Status: formalised
Filed: 2026-08-24

Noticed during `aplt-output-drift-remaining-repos` (PyAutoGalaxy#585,
2026-08-24), which preserved CRLF in the three files it edited rather than
bury a real fix inside whole-file diffs.

## The state

`euclid_strong_lens_modeling_pipeline/AGENTS.md` says:

> All files must use Unix line endings (`\n`). CRLF will break shell scripts on
> the HPC.

Measured on `main`: **20 of 126 tracked text files carry CRLF** — mixed, not
uniform, so this is drift rather than a deliberate convention.

| Extension | CRLF / total |
|---|---|
| `.py` | 11 / 29 |
| `.yaml` | 8 / 79 |
| `.sh` | 1 / 1 |

## Why this is not cosmetic

The CRLF has reached exactly the files the rule exists to protect, **including
their shebang lines**:

```
hpc/sync                          #!/usr/bin/env bash^M
hpc/batch_gpu/submit_start_here   #!/bin/bash -l^M
hpc/batch_cpu/submit_start_here   #!/bin/bash -l^M
activate.sh                       BASE=/mnt/ral/jnightin/PyAuto^M
```

A trailing `\r` becomes part of the interpreter path, which is the documented
`bad interpreter` failure. Also affected: `hpc/batch_gpu/submit_full_model`,
`hpc/batch_cpu/template`, `hpc/sync.conf.example`, `hpc/.gitignore`.

**Do not assume these are currently broken.** They are evidently in use for real
GPU runs, so either they are invoked in a way that tolerates it (`bash hpc/sync`
ignores the shebang), or SLURM is forgiving, or the CRLF is recent. **Establish
which before writing the PR** — `git log` the affected files to see when CRLF
appeared, and say plainly in the PR whether this was a live break or a latent
one. That distinction is the whole value of the task.

`activate.sh` is the interesting case: it is `source`d, not executed, so its
`\r` lands inside a variable — `BASE` gains a trailing carriage return and every
path built from it is subtly wrong. That fails differently and more quietly than
a bad shebang.

## Shape of the fix

1. Convert all tracked text files to LF in one mechanical pass.
2. **Add a `.gitattributes`** — the repo has none, which is why this recurred.
   Without it nothing stops the next contributor on Windows reintroducing it.
   `* text=auto eol=lf`, with explicit entries for the `hpc/` scripts that carry
   no extension.
3. Verify: no tracked text file contains `\r`; the `hpc/` scripts still parse
   (`bash -n`); Python files still compile.

## Scope note

This is a whole-repo whitespace commit and will touch 20 files with no logical
change — that is the point, and it is why it was kept out of PyAutoGalaxy#585.
Land it on its own so the diff stays reviewable as "line endings only", and land
it when no other euclid branch is open, since it will conflict with everything.
