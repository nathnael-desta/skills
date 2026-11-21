# Skills

Agent skills for Claude Code, OpenCode, Codex and other agents that read
`SKILL.md` files. Each top-level folder is one skill.

## Install

Install with the [Vercel Skills CLI](https://github.com/vercel-labs/skills). It
reads this repository from GitHub, asks which skills and which agents you want,
and copies them into place.

```bash
npx skills@latest add nathnael-desta/skills            # current project
npx skills@latest add nathnael-desta/skills --global   # every project
```

One skill, no prompts:

```bash
npx skills@latest add nathnael-desta/skills --skill writing-tests --agent claude-code -y
```

Update, list, remove and the lock file: [docs/installation.md](docs/installation.md).

## Skills

### Tests and CI

- `writing-tests` - rules for adding, changing or deleting a test: name the bug
  first, extend before adding, mock only at system boundaries, red before green,
  and report each new test with the bug it catches.
- `pruning-tests` - audit an existing suite: a cheap-model first pass in batches,
  per-test coverage of the delete and merge candidates, a stronger-model
  re-review, per-file approval, then the edits. Ships the rubric, briefs and a
  coverage script.
- `speeding-up-ci` - speed up slow GitHub Actions CI in order: measure, remove
  duplicate runs, cache, fix slow database and frontend tests, then shard or buy
  runners. Includes measured before and after numbers.
- `reviewing-deploys` - checklist for a push-to-deploy pipeline (rollback,
  deployed SHA, health gate, migrations, gating on the tree CI passed) and a
  shimmed-docker harness to simulate the deploy script.

### Reviews and handoffs

- `codex-code-review` - review local changes with the OpenAI Codex CLI: staged,
  branch-diff, security and performance reviews, with prompts and a runner
  script.
- `claude-session-handoff` - turn a Claude Code session from a repository or
  worktree into a redacted Markdown handoff for a fresh agent.
- `end-to-end-feature-explainer` - explain a finished feature or ticket sequence
  end to end: spec, tickets, architecture, runtime flows, checks and remaining
  limits.

### Feature workflow

These build on Matt Pocock's skills (`wayfinder`, `grilling`, `to-spec`,
`to-tickets`); install those from
[mattpocock/skills](https://github.com/mattpocock/skills) first.

- `plan-feature` - turn a settled Wayfinder or grilling outcome into one spec
  issue and approved, dependency-ordered tickets, without starting work.
- `execute-feature` - implement an approved spec's tickets in order, or in
  parallel worktree batches when they are independent, with a review per ticket.
- `ship-feature` - plan-feature and execute-feature in one run, ending in an
  acceptance report.
- `finish-ticket` - check a finished ticket and list what is still required
  before closing it.
- `prototype-review` - review a throwaway prototype against its Wayfinder
  question and produce a short decision brief.

### Browser and visuals

- `visual-proof` - drive the real app, fix what you find, re-walk it, and hand
  back an HTML report of captioned screenshots and before/after sliders.
  Needs a browser driver (`browse` or Playwright) and Python 3.
- `t3-visualize` - show charts, timelines and before/after inline with T3 Code's
  `html_render` and `html_preview` tools.
- `gemini-research` - research with Gemini Deep Research and Gemini Tasks in
  the user's own browser: prompt template, parallel tabs, extraction, and
  checking key numbers against the sources. Needs the `browse` CLI.

### Other

- `antigravity-delegation` - hand screenshots, PDFs, diagrams and whole-repo
  reads to Google Gemini through Antigravity, with what it may and may not do.
- `update-catalog` - write feature breakdowns, changelogs and "what's new"
  catalogs for a project in a fixed format.

## Development

```bash
npm install
npm test                 # structure, frontmatter and formatting
npm run verify:skills    # ask the Skills CLI to discover every skill
```

A skill is a folder with a `SKILL.md` whose frontmatter `name` matches the
folder. Longer material goes in that skill's `references/` folder.

## License

MIT. Each skill is the author's own work unless its `SKILL.md` says otherwise.
