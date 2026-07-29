---
name: antigravity-delegation
description: Offload perception-heavy and large-context read-only work to Google Gemini through Antigravity. Use when analyzing screenshots, UI, PDFs, diagrams, or charts, when reading a whole repository or log, or when supporting analysis should run without blocking the main loop.
---

# Antigravity delegation

Gemini through Antigravity is a cheap, fast, huge-context, best-in-class
multimodal **helper** — not an autonomous driver. This skill is the policy for
substituting it into read-only work.

Requires the `opencode-antigravity-delegate` plugin, which exposes
`antigravity_delegate`, `antigravity_vision`, `antigravity_background_start`,
and `antigravity_background_poll`.

## The model profile that drives every rule

| Signal                | Value         | Consequence                                     |
| --------------------- | ------------- | ----------------------------------------------- |
| Coding                | ~70           | A genuinely capable worker                      |
| **Agentic**           | **~37**       | Poor long-horizon planner; keep it off the loop |
| Multimodal (MMMU-Pro) | **84%**       | Beats its own Pro tier — best vision option     |
| Speed                 | 280–437 tok/s | 4–7× frontier models                            |
| Context               | 1M            | But deep-1M recall degrades; keep needles early |

## Substitute, never add a stage

Antigravity **replaces** a suitable read-only call. It is not a mandatory
pre-step.

| Work                                        | Route                            |
| ------------------------------------------- | -------------------------------- |
| Trivial request                             | Answer directly; do not delegate |
| Large repository or log exploration         | `antigravity_delegate`           |
| Screenshot, PDF, diagram, chart             | `antigravity_vision`             |
| Design comparison, root-cause hypotheses    | `antigravity_delegate`           |
| Independent read-only diff analysis         | `antigravity_delegate`           |
| Shared code edits, integration, test repair | Your primary worker              |
| Stateful or safety-sensitive work           | Your primary worker first        |

## Prohibited

- Calling Antigravity **and** a routine worker for the same exploration.
- Requiring an Antigravity pass before implementation.
- Using it for simple requests.
- Serial chains of multiple Antigravity calls.
- Starting background work when you must immediately wait for it.
- Treating the AI Pro quota as free or unlimited.

## Quota is real

Roughly 100 agent requests per day under a weekly ceiling. Exhausting it can
strand the account for up to a week, so treat "quota exhausted" as a graceful
degrade — fall back to the primary model rather than failing the run. Background
jobs are capped at four concurrent for the same reason.

## Model choice

Use a tiered flash model (for example `gemini-3.6-flash-high`). **Tiered model
names already encode effort, so do not also pass an effort argument.** Do not
upgrade helper work to Gemini 3.1 Pro: Flash beats it on multimodal and costs
less.

**Gemini only.** Antigravity also serves Claude and gpt-oss, but routing a
third-party model through it stacks that vendor's terms on top of Google's. The
plugin rejects any non-`gemini-*` model.

## Background work

`antigravity_background_start` returns a job id immediately; collect it later
with `antigravity_background_poll`. Only worth it when the job genuinely
overlaps foreground work you are about to do anyway. Polling is a local file
read and costs no quota.

## Visual packets

When sending images, include: page, viewport, theme, user goal, expected visual
invariants, actions taken, focused DOM evidence, what changed, exact questions,
overlays or viewport/theme/scroll differences to ignore, and ask for at most
three evidence-backed findings with a verdict and confidence.

Gemini is an **advisory visual analyst only**: never let it click, type,
authenticate, approve, or control a browser. Verify actionable findings through
DOM, ARIA, computed styles, or bounding boxes before editing.

## Keep it off the critical path

Keep the agentic loop, escalation, and the milestone review gate on your primary
models. If Antigravity is unavailable, continue with semantic and DOM
verification and disclose that the offload was unavailable.
