# OpenCode Integration Modes

OpenCode discovers project skills under `.agents/skills/`. The default setup
generates a skill there from Beads' own current OpenCode recipe rather than
adding that recipe to `AGENTS.md`.

## Compatibility matrix

Exactly one generator must own each output path. Codex's official recipe owns
`.agents/skills/beads/SKILL.md`, so lean OpenCode cannot coexist with Codex.

| Selected agents                | Recipe ownership          | OpenCode mode  |
| ------------------------------ | ------------------------- | -------------- |
| OpenCode                       | OpenCode lean             | Lean           |
| OpenCode + Claude Code         | OpenCode lean and Claude  | Lean           |
| Codex                          | Codex official            | Not applicable |
| Codex + Claude Code            | Codex and Claude official | Not applicable |
| Codex + OpenCode               | Codex and OpenCode        | Official       |
| Codex + OpenCode + Claude Code | All official              | Official       |

When Codex and OpenCode are both selected, run the official recipes and require
both checks to pass in the same final state:

```bash
bd setup codex --check
bd setup opencode --check
```

## Lean skill

Run `bd setup opencode --print` and prepend the bundled skill frontmatter to its
complete, unmodified stdout. This preserves the exact upstream-maintained
OpenCode guidance while making it discoverable on demand instead of always
loading it through `AGENTS.md`. The generated recipe tells OpenCode to run
`bd prime`, so complete operational guidance still comes from the installed CLI.

Append the managed tracker-precedence block after the generated recipe. Check
for changes after upgrading Beads by comparing `bd setup opencode --print` with
the file content between the frontmatter and precedence markers. A temporary
extraction or equivalent in-memory comparison is preferable to a line-number-
dependent command.

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

Do not replace or edit that managed section or the Codex-generated Beads skill;
doing so breaks upstream checks. Place the tracker-precedence block after all
generated Beads sections in the automatically loaded instruction file. Choose
the lean skill or the official managed section as one OpenCode authority.
