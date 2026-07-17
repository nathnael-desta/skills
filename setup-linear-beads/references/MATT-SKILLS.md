# Matt Pocock Skills

Matt's skills remain owned by `mattpocock/skills`. Install and update them
through Vercel Skills so `skills-lock.json` records provenance. Never copy or
recreate their skill bodies.

## Recommended bundle

```text
setup-matt-pocock-skills wayfinder to-spec to-tickets implement code-review
```

Map known environments to Vercel Skills agent IDs:

| Environment | Agent ID      |
| ----------- | ------------- |
| OpenCode    | `opencode`    |
| Claude Code | `claude-code` |
| Codex       | `codex`       |

For multiple known agents, pass all IDs after one `--agent` flag. For another
environment, use the installer's agent selector instead of guessing an ID.

Example project-local OpenCode install:

```bash
npx skills@latest add mattpocock/skills --skill setup-matt-pocock-skills wayfinder to-spec to-tickets implement code-review --agent opencode -y
```

Add `--global` for global scope. Omit `--skill` and `-y` for interactive skill
selection. Use `--skill '*' -y` only after the user chooses all skills.

Verify every requested skill for every selected agent:

```bash
npx skills@latest list --agent opencode --json
npx skills@latest list --global --agent opencode --json
```

When already installed, offer updates only if the user asks to update or the
installed copy is incompatible with setup:

```bash
npx skills@latest update setup-matt-pocock-skills wayfinder to-spec to-tickets implement code-review --project
npx skills@latest update setup-matt-pocock-skills wayfinder to-spec to-tickets implement code-review --global
```
