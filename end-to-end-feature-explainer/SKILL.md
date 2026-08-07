---
name: end-to-end-feature-explainer
description: Explain a completed feature or ticket sequence end to end, connecting the original spec, ticket responsibilities, implementation architecture, runtime flows, safeguards, validation evidence, review steps, and remaining limitations in clear user-facing language.
triggers:
  - "explain the whole feature"
  - "what was built"
  - "how does this all fit together"
  - "explain the tickets"
  - "give me an end-to-end overview"
  - "how do I review this feature"
---

# End-to-End Feature Explainer

Explain completed engineering work as a coherent system, not as a list of
commits. Connect the product intent to the implementation and tell the user
how to verify the result.

## When To Use

Use this skill when the user wants to understand:

- What a feature ultimately does after several tickets or phases.
- How the spec, tickets, code, data, workers, APIs, UI, and operations fit together.
- What each ticket accomplished and why the order mattered.
- How to test or review the finished feature.
- What was deliberately excluded, deferred, gated, or left unresolved.

Use it after implementation, during handoff, before human acceptance, or when a
user asks for a practical architecture walkthrough.

## Source Gathering

Before explaining, inspect the actual available evidence. Prefer, in order:

1. The canonical spec or product brief.
2. The linked tickets/issues and their dependency relationships.
3. Worker or implementation result packets.
4. The final integrated review and test reports.
5. Relevant code paths, migrations, runbooks, and configuration.
6. Git history only when it clarifies ownership or sequencing.

Do not infer completion from a ticket title alone. Distinguish clearly between:

- Planned behavior.
- Implemented behavior.
- Verified behavior.
- User-waived verification.
- Remaining risks or blockers.

## Explanation Method

Build the explanation in this order:

1. **Purpose:** State the user and business problem the feature solves.
2. **Scope and decisions:** State important constraints, policy decisions,
   supported roles/resources, environments, currencies, and explicit exclusions.
3. **Final capability:** Describe what exists at the end of the complete flow.
4. **End-to-end lifecycle:** Walk through the runtime sequence from setup or
   onboarding through initiation, provider/API boundaries, verification,
   fulfillment, background work, notifications, reconciliation, and recovery.
5. **Ticket map:** Explain each ticket's responsibility and how it depends on
   earlier work. Group remediation tickets with the feature area they hardened.
6. **Data and safety model:** Explain durable records, idempotency, snapshots,
   authorization, state transitions, audit trails, and what the system refuses
   to do.
7. **Admin and operational behavior:** Explain dashboards, alerts, refunds,
   runbooks, environment gates, monitoring, and manual actions.
8. **Verification guide:** Give a practical automated and manual checklist with
   commands, URLs, credentials only when already intentionally provided, and
   expected outcomes. Never expose secrets.
9. **Boundaries:** State what was not built, what was waived, and what must be
   approved before production or live activation.

## Detail Rules

- Explain the system in plain language first, then add technical names,
  statuses, tables, routes, migrations, or commits where they help.
- Explain why a boundary exists, not only what it is. For example, explain why
  a browser return cannot fulfill a payment without server verification.
- For asynchronous work, explicitly identify the durable state before enqueue,
  the worker, retry behavior, idempotency claim, and failure recovery path.
- For money or entitlement flows, distinguish principal, payer total, provider
  fee, settled amount, platform revenue, and recipient settlement.
- For state-changing actions, mention the relevant notification recipients.
- Mention units and conversion rules when amounts are stored differently from
  how they are displayed.
- Call out test-mode simulators versus real providers and never imply that a
  simulator proves live-provider behavior.
- Keep lists flat. Use short headings and compact paragraphs.
- Do not claim a ticket was closed unless the evidence explicitly says so.
- Do not claim production readiness when legal, provider, operational, or
  release gates remain unresolved.

## Recommended Output

Use this structure unless the user requests another format:

```markdown
# What The Feature Is

## Final Capability

## End-to-End Flow

## Ticket-by-Ticket Accomplishments

## Data, Safety, And Recovery

## Admin And Operations

## How To Check It

## What Is Not Included

## Remaining Risks And Gates
```

The explanation should answer these questions directly:

- What problem was solved?
- What exists now that did not exist before?
- What happens from the first user action to the final outcome?
- Which ticket added each major part?
- How are duplicates, failures, retries, refunds, and unknown states handled?
- What evidence says it works?
- What can the user safely test now?
- What still prevents live or production use?

## Example Prompts

- “Explain the whole payment feature we just built, ticket by ticket, and tell
  me how to review it.”
- “Give me the end-to-end architecture and runtime flow in non-jargony terms.”
- “What was ultimately delivered by this spec, and what is still out of scope?”
