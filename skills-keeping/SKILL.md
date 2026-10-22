---
name: skills-keeping
description: "Keep agent skills in one place and in sync. Use when adding, editing, moving or installing a skill, when a skill seems stale or differs between agents or projects, when setting up another machine, or before editing any SKILL.md that is not under ~/code/skills."
---

# Skills keeping

`~/code/skills` (git, remote `nathnael-desta/skills`) is the single editable source for personal skills. Every agent folder holds **symlinks** into it, so there is one copy and nothing drifts.

## Where skills live

| Place                                                                                                  | Holds                                                                                                |
| ------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------- |
| `~/code/skills/<name>/`                                                                                | the real, editable personal skills                                                                   |
| `~/.agents/skills/`                                                                                    | hub every agent reads: symlinks to the repo, plus vendor installs (Matt Pocock, Expo, ui-ux-pro-max) |
| `~/.claude/skills/<name>`                                                                              | symlink to `../../.agents/skills/<name>` (or straight to the repo for Claude-only skills)            |
| `~/.codex`, `~/.config/opencode`, `~/.commandcode`, `~/.openhands`, `~/.pi`, `~/.gemini/config/skills` | links to the hub or the repo; `~/.gemini/config/skills` is itself a symlink to the hub               |
| `<project>/.agents/skills`, `.claude/skills`                                                           | project-specific skills, and vendor installs recorded in the project's `skills-lock.json`            |

Left alone on purpose: vendor installs (`~/.agents/.skill-lock.json` lists them; `skills update` owns them), plugin skills, and project-specific skills (`behigamlak-*`, `finish-work`, `xstate`).

## The rule

Edit a skill only in `~/code/skills/<name>/`. A real folder with a `SKILL.md` anywhere else that shares a name with a repo skill is a stale copy: diff it, merge anything newer into the repo, replace it with a symlink.

## Add a skill

1. Write `~/code/skills/<name>/SKILL.md` (see `writing-for-agents`; quote a `description` that contains `: `, or the `skills` CLI skips the skill).
2. Link it where it should be visible: `ln -s ~/code/skills/<name> ~/.agents/skills/<name>`, then `ln -s ../../.agents/skills/<name> ~/.claude/skills/<name>`. Add the same link under any other agent that should see it.
3. Add a line to the README, commit. Done when `readlink -f ~/.claude/skills/<name>/SKILL.md` resolves and the frontmatter reads.

## Check drift

```bash
python3 -I ~/code/skills/skills-keeping/scripts/check_drift.py --projects ~/code/routa ~/code/Behigamlack
```

It lists real copies of repo skills in the agent folders and in the projects (`same` or `differs`, and which side is newer), and broken links; exit 1 means drift. `--all` also lists local-only skills and repo skills missing from the hub. Run it when you start work in a project after the skills changed, and monthly.

A project copy of a repo skill is deleted (the hub already provides it) or refreshed with `cp -a`. Never symlink it: an absolute link committed to the project breaks on other machines and in CI. Copies that must ship with the project stay, and `check_drift.py` is how you see they are behind.

## Another machine

```bash
git clone git@github.com:nathnael-desta/skills.git ~/code/skills   # later: git -C ~/code/skills pull
npx skills@latest add nathnael-desta/skills -g                      # pick skills and agents
npx skills@latest update -g -y                                      # refresh installed skills later
```

`skills add` copies into the hub, so there the repo is read-only upstream. The `skills` CLI has no separate check command: `update` both checks and applies. On a machine with the symlink layout, do not run `add` or `update` for repo-owned skills; `git pull` is the update.

## Never

- Edit a skill inside a project folder or a global agent folder.
- `cp -r` a skill into an agent folder.
- Delete a copy before it is in `~/temp/skills-migration-backup/`.
- Commit a symlink to `~/code/skills` into another repository.
