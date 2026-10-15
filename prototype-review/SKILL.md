---
name: prototype-review
description: Review a completed throwaway prototype against its Wayfinder question, prerequisite decisions, and sibling prototypes, then produce a concise decision brief. Use when a prototype agent says it is finished or before closing a wayfinder:prototype issue and moving its result into a spec.
---

# Prototype Review

Review the decision the prototype was meant to answer, not the code as a production implementation.
This is a scoped feature and behavior review, not a general approval of the prototype's design.

## Gather context

1. Identify the prototype issue or issues from the prompt. If none is provided, ask for the issue URL or number.
2. Read each issue body, comments, labels, parent map, and blocker relationships with `gh`.
3. Read every blocker resolution comment and linked ADR, research artifact, prototype branch, or handoff. Treat accepted blocker decisions as constraints.
4. Read `AGENTS.md`, `CLAUDE.md`, `CONTEXT.md`, relevant `docs/adr/`, and the parent map's `Decisions so far`.
5. Inspect the prototype branch/worktree and its diff. Run its documented one-command prototype path when feasible. Note the exact commands and any prerequisites (install, env vars, ports, open flags) used to run the prototype so they can be recorded in the report. Do not merge or rewrite prototype code.
6. For a cohort review, inspect sibling `wayfinder:prototype` issues and compare their actual artifacts, not just their titles.

## Evaluate

Determine:

- The original question, user, scenario, and success condition.
- The capabilities and tradeoffs explicitly in scope for that question.
- Which prior decisions and constraints the prototype was expected to honor.
- What the artifact demonstrates, including important states, paths, and interactions.
- What it does not demonstrate, what is missing, and what remains uncertain.
- Differences between sibling prototypes in feature behavior, state transitions, inputs/outputs, constraints, failure recovery, and implementation implications.
- Which observations are evidence, which are recommendations, and which still require the user's decision.
- Which important checks or decisions the user may have missed, based on the issue, blockers, prototype behavior, and sibling comparisons.

At the top of the report, name every issue, ADR, research artifact, and handoff read for this review. Summarize each relevant prior decision in one line; do not paste full issue bodies.

Review visual polish, aesthetics, general UX, or accessibility only when the issue explicitly asks for them. Otherwise mark them out of scope rather than treating them as accepted or rejected.
Evaluate each in-scope capability separately. Never use a broad statement such as "the prototype is fine" to imply that untested features or design choices are approved.

Do not silently turn a plausible prototype choice into an accepted product decision. Do not run `/implement` or `/code-review` as part of this review.

## Report

Keep the report concise and understandable to someone who did not see the prototype. End the brief with the exact commands to run the prototype so anyone reading it can launch it without hunting through the branch. Use this structure:

```md
# Prototype Decision Brief

## Source Context

- **Issues read:** <issue titles and numbers>
- **Prior decisions:** <one-line summaries of the accepted decisions that constrain this prototype>
- **Artifacts read:** <ADR, research, branch, or handoff links>

## Question

<what this prototype was meant to answer>

## Context

<relevant accepted constraints and blockers>

## Review Scope

- **In scope:** <specific capabilities and tradeoffs being evaluated>
- **Out of scope:** <design or product areas not evaluated>

## What It Shows

<the observable behavior and strongest evidence>

## Gaps and Risks

<what it does not prove or where it conflicts with context>

## Feature Comparison

<a compact table of capability-by-capability differences when multiple prototypes were reviewed; omit when there is only one>

## Per-Dimension Decisions

1. **<capability or tradeoff>** — <accept, revise, or unresolved>; Recommended: <answer>

## Next Step

<what should carry into the spec or next prototype; this is not blanket approval of the prototype>

## How to Run

<exact, copy-pasteable commands to run the prototype, plus any required setup: install, env vars, ports, open flags>
```

Use the OpenCode `question` tool for the decisions. If the user requests batching, ask the whole currently answerable set in one call and defer only dependent questions to a later round. Do not act on the result until the user confirms shared understanding.

After presenting the brief, generate your own review questions in addition to anything the user already asked. Ask a concise batch through the question tool covering things the user should inspect, compare, verify, or decide, such as missing states, conflicting behavior, important tradeoffs, untested constraints, and differences between prototypes. Label each as a check or decision, explain why it matters in one line, and include a recommended answer or inspection target. Do not silently omit a question merely because the user did not think to ask it.

## After acceptance

Only after the user accepts the decisions:

1. Record durable domain language in `CONTEXT.md`.
2. Record hard-to-reverse or architectural decisions in an ADR with the correct status.
3. Post the concise verdict and artifact links as a resolution comment on each prototype issue.
4. Close resolved Wayfinder prototype issues and update the parent map's `Decisions so far` with links and one-line gists.
5. Leave unresolved questions as new or updated Wayfinder tickets; do not hide them in a closed issue.

The prototype itself remains throwaway. The durable output is the accepted decision and its context pointer, which `/to-spec` can later synthesize with the rest of the map.
