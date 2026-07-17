# OpenCode Integration Modes

OpenCode discovers project skills under `.agents/skills/`. The default setup
generates a skill there from Beads' own current OpenCode recipe rather than
adding that recipe to `AGENTS.md`.

## Lean skill

Run `bd setup opencode --print` and prepend the bundled skill frontmatter to its
complete, unmodified stdout. This preserves the exact upstream-maintained
OpenCode guidance while making it discoverable on demand instead of always
loading it through `AGENTS.md`. The generated recipe tells OpenCode to run
`bd prime`, so complete operational guidance still comes from the installed CLI.

Check for changes after upgrading Beads with:

```bash
diff -u <(bd setup opencode --print) <(tail -n +5 .agents/skills/beads/SKILL.md)
```

Exit status 0 means the installed skill exactly matches the current upstream
recipe. A diff means it must be regenerated. This provides the same stale-versus-
current decision for the skill layout even though `bd setup opencode --check`
hard-codes the managed `AGENTS.md` target. Beads 1.1.0's `--output` mode writes
instead of checking, and custom recipes only check that their target exists, so
neither is a content-freshness substitute.

This mode loads Beads guidance on demand. It does not inject `bd prime`
automatically at session start. That is an intentional tradeoff: no plugin and
no large always-loaded `AGENTS.md` section.

## Official managed section

First inspect the integrations supported by the installed Beads version:

```bash
bd setup --list
```

When listed, `bd setup opencode` creates a full managed section in `AGENTS.md`.
Its version and hash markers let `bd setup opencode --check` report whether the
section is missing, changed, or stale. Rerunning setup updates it in place;
upgrading Beads alone does not rewrite repository files automatically.

Do not replace that managed section with a pointer and expect upstream checks to
keep working. Choose the lean skill or the official managed section as one
authority. Install both only when the user knowingly accepts duplicated
guidance.
