---
name: finish-ticket
description: Validate a completed ticket implementation, identify anything still required, and produce a close-ready checklist or explicit blockers. Use when implementation is believed finished and the user asks what to verify, check, or do before finishing or closing an issue.
argument-hint: "[ticket ID, file, path, or description]"
disable-model-invocation: true
---

# Finish Ticket

Act as the final acceptance gate after all implementation agents for the ticket or feature have finished and their changes are integrated. This skill checks the complete result; it does not silently expand the scope or close the issue.

Do not run this as each implementation agent finishes when other related agents are still working. Those agents should still run their own targeted checks and `/code-review`; this skill is the final integrated acceptance pass.

## Workflow

### 1. Establish the source of truth

- Find the ticket in the current conversation, the argument, the configured issue tracker, or a local ticket/spec file.
- Extract acceptance criteria, non-goals, constraints, and any explicit verification steps.
- Confirm that all related implementation agents are finished and their changes are present in the same integrated working state. If not, stop and report that the final acceptance pass is premature.
- If the ticket cannot be found, ask the user to provide its text or location before judging completion.
- Identify the complete implementation boundary from ticket-linked commits, the current branch, or the working tree. Include interactions between related changes, not just each agent's individual diff. Ask for a fixed point only when the changed scope cannot be isolated reliably.

### 2. Inspect the implementation

- Read the relevant diff and the surrounding code, tests, configuration, and documentation.
- Map every acceptance criterion to concrete evidence. Never mark a criterion complete because the code merely appears to support it.
- Check for unintended scope, missing error paths, stale names, dead code, compatibility concerns, security or accessibility regressions, and required migrations or configuration.
- Check repository guidance such as `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, and project test instructions.

### 3. Verify with the cheapest sufficient checks

Run checks instead of describing checks that should be run:

- Targeted tests for changed behavior.
- Typechecking, linting, formatting, or build checks required by the repository.
- The full test suite when the project provides one; this is the final integrated pass.
- `curl` or another direct API check for backend/API behavior.
- Browser verification only for visual layout, hydration, overlays, image loading, or multi-step interaction behavior.
- Review generated files, migrations, fixtures, and test data when the ticket touches them.

Record the exact command and result for each check. Do not claim a check passed if it was not run or if it failed.

### 4. Decide the outcome

Return exactly one of these statuses:

- **READY TO CLOSE** — all acceptance criteria have evidence, relevant checks pass, and no blocker remains.
- **NOT READY** — one or more concrete blockers remain; give the exact action or command needed for each.
- **NEEDS HUMAN DECISION** — completion depends on an unresolved product, UX, security, migration, or release decision rather than more coding.

Use severity for findings: `Blocker`, `Follow-up`, or `Informational`. A follow-up must not be presented as a reason to keep the ticket open unless the ticket or repository requires it.

## Report format

```text
Status: READY TO CLOSE | NOT READY | NEEDS HUMAN DECISION

Acceptance criteria
- [pass|fail|unclear] criterion: evidence

Verification run
- `command`: result

Remaining actions
- Blocker or human decision, if any

Closure note
- A concise summary suitable for the ticket, only when READY TO CLOSE
```

Do not close the ticket, commit, or push unless the user explicitly asks. If no issue tracker is connected, provide the closure note for the user to apply manually and say that the issue remains open externally.
