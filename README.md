# Skills

Agent skills for repeatable development workflows across Claude Code,
OpenCode, Codex, and other skill-aware coding agents.

## Installation

Install through [Vercel Skills](https://github.com/vercel-labs/skills). It
discovers the skills in this repository, asks which ones and which agents to
target, and manages project or global installation without manual file copying.

From the repository's GitHub location:

```bash
npx skills@latest add nathnael-desta/skills --global
```

Because this repository exposes one skill, the installer selects
`setup-github-beads` automatically. OpenCode is included through the always-on
Universal `.agents/skills` target; select any additional agent-specific targets
you also want, then confirm the installation.

For a non-interactive OpenCode installation:

```bash
npx skills@latest add nathnael-desta/skills --skill setup-github-beads --agent opencode --global -y
```

From a local clone:

```bash
npx skills@latest add /path/to/this-repository
```

Omit `--global` to install into only the current project. See [installation and
lifecycle](docs/installation.md) for other targeted, unattended, update,
verification, and removal commands.

Restart or reload the selected agent if required, then invoke
`setup-github-beads` in the Git repository you want to configure.

`setup-github-beads` is the single setup entry point. It can configure Claude
Code, OpenCode, Codex, or another user-selected agent; install a lean
project-local Beads skill for OpenCode; and extend the currently installed Matt
Pocock setup skill without recreating its GitHub tracker behavior. If the
upstream setup dependency is missing, it offers to install it through Vercel
Skills.

The setup distinguishes machine prerequisites from per-repository state. If the
GitHub CLI, Beads CLI, repository database, Beads GitHub access, or agent
integration is missing, it explains that layer and walks through recovery
before continuing.

## Skills

- `setup-github-beads` - retain the current Matt Pocock GitHub Issues workflow
  and add Beads as the implementation execution graph with minimal defaults and
  routing policy.

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
