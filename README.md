# Skills

Agent skills for repeatable development workflows across Claude Code,
OpenCode, Codex, and other skill-aware coding agents.

## Installation

Install through [Vercel Skills](https://github.com/vercel-labs/skills). It
discovers the skills in this repository, asks which ones and which agents to
target, and manages project or global installation without manual file copying.

From the repository's GitHub location:

```bash
npx skills@latest add nathnael-desta/skills
```

From a local clone:

```bash
npx skills@latest add /path/to/this-repository
```

Choose `setup-linear-beads` and the agents that will run it. Add `--global` for
a user-level installation; project installation is the default. See
[installation and lifecycle](docs/installation.md) for targeted, unattended,
update, verification, and removal commands.

Restart or reload the selected agent if required, then invoke
`setup-linear-beads` in the Git repository you want to configure.

`setup-linear-beads` is the single setup entry point. It can configure Claude
Code, OpenCode, Codex, or another user-selected agent; install a lean
project-local Beads skill for OpenCode; and optionally install and run Matt
Pocock's engineering-skills setup through Vercel Skills.

The setup distinguishes machine prerequisites from per-repository state. If the
Beads CLI, repository database, Linear credentials, team selection, or agent
integration is missing, it explains that layer and walks through recovery before
continuing.

## Skills

- `agent-browser` - browser automation through the `agent-browser` CLI.
- `frontend-verification` - browser-based completion checks for frontend work.
- `setup-linear-beads` - configure Linear as the human planning layer and
  Beads as the implementation execution graph, with optional support for Matt
  Pocock's engineering skills.

## Development

```bash
npm test
npm run verify:skills
```

Each skill lives in a top-level directory with a required `SKILL.md`. Detailed
material belongs under that skill's `references/` directory so the main skill
stays concise.

## Publishing

Publish the repository at a stable Git URL so Vercel Skills can record source
provenance and update installed skills from upstream. Before publishing, run
`npm test` and `npm run verify:skills`.

## License

MIT
