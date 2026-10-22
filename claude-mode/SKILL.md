---
name: claude-mode
description: Switch Claude Code between lean (spend-limited, Haiku subagents) and burn (limits don't matter) cost modes, or check which mode is active. Use when the user mentions modes, usage limits, switching subagent models, or settings.json drift.
---

# claude-mode

Machine-specific: needs the `claude-mode` script (`~/.local/bin/claude-mode`) and `~/.claude/modes/`, neither of which is in this repo. On another machine this skill is only a description.

Two cost modes live in `~/.claude/modes/`. `~/.claude/settings.json` is GENERATED from them: never hand-edit it.

| File                    | Role                                                                                                                                                                                                      |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `base.json`             | settings shared by both modes (model, hooks, plugins, Opus effort, Haiku 110k window)                                                                                                                     |
| `lean.json` / `lean.md` | spend-limited: Agent-tool subagents forced onto `claude-haiku-5-5`, Sonnet compacts at ~150k, 8 unused claude.ai connectors denied, PostHog off, 50 unused skills hidden, claude.ai plugin/skill sync off |
| `burn.json` / `burn.md` | limits irrelevant: subagent default `claude-sonnet-5-5` (not forced), nothing hidden, PostHog on, sync back on                                                                                            |
| `active.md`             | symlink to the active mode's policy; `~/.claude/CLAUDE.md` imports it                                                                                                                                     |
| `backups/`              | every switch saves the previous settings.json here (last 20)                                                                                                                                              |

## Commands

```
claude-mode status     # active mode + drift check (does settings.json match the generated file?)
claude-mode lean       # switch (regenerates settings.json, repoints active.md)
claude-mode burn
claude-mode rollback   # restore the most recent backup
```

## Rules

- To change a setting: edit `base.json` (both modes) or `<mode>.json` (one mode), then run `claude-mode <current mode>`. Editing `settings.json` directly gets flagged as drift and overwritten (a copy is kept in `backups/`).
- Claude Code itself writes `settings.json` when you use `/config` or `/model`. `claude-mode status` shows that as drift; move the change into `base.json`/`<mode>.json`.
- Env vars (the subagent model and its force flag) are read at session start: restart sessions after switching. Settings and CLAUDE.md changes reach new sessions.
- A new mode = `modes/<name>.json` + `modes/<name>.md`. Lists merge only for `deniedMcpServers` (concatenated with base).
- Hidden skills use `skillOverrides: "user-invocable-only"`: Claude stops seeing them but `/name` still works. Plugin skills are not covered by `skillOverrides` (use `enabledPlugins` or the sync flags).
- Memory notes that cap model use (agent-model-cap, subagent-haiku-first) are lean-mode rules.
