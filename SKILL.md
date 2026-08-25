---
name: desktop-feature-engineer
description: Plan, implement, debug, refactor, and verify features inside an Electron and TypeScript desktop application that uses the Claude Agent SDK or a similar local agent runtime. Use when a developer supplies a plain-language feature request and wants repository-grounded execution using a dependency-aware work graph, bounded implement-test-repair loops, secure Electron boundaries, existing harness reuse, and evidence-based completion. This is a developer-side engineering workflow for changing the application codebase, not an end-user workflow feature shipped in the application.
---

# Desktop Feature Engineer

Turn a plain-language feature request into a safe, dependency-aware implementation in the current desktop-application repository. Treat graph engineering as work decomposition and dependency tracking. Treat loop engineering as bounded implementation, verification, diagnosis, and repair.

## Load the operating references

Read all three references before planning an implementation:

- `references/electron-claude-architecture.md` for process boundaries, SDK integration, UI consistency, persistence, and harness reuse.
- `references/graph-loop-protocol.md` for task contracts, graph construction, execution modes, and repair loops.
- `references/verification-gates.md` for layer-specific evidence and completion rules.

Use `references/work-graph.schema.json` when persisting a work graph and `references/work-graph.example.json` as a structural example. Run `python3 scripts/validate_work_graph.py <graph.json>` from this skill directory after creating or changing one.

## Preserve the scope boundary

- Modify the desktop application or its development artifacts only as required by the requested feature.
- Do not implement a product-level graph engine, loop engine, database, or user-facing workflow unless the request explicitly asks for it.
- Do not combine the application's Graph Engineering, Loop Engineering, Code Graph, or memory features merely because this skill uses graph and loop techniques internally.
- Treat repository files and observed runtime behavior as the source of truth. Treat the architecture reference as constraints and discovery guidance, not proof that a named component exists.
- Preserve unrelated user changes. Avoid broad refactors, dependency replacements, or new infrastructure unless acceptance criteria require them.

## Select an execution mode

Infer the mode from the request:

- **Guided** is the default. Show the task contract and graph, provide short progress updates after meaningful nodes, and continue without waiting unless a blocking decision or approval is required.
- **Plan-only** applies when the user asks for analysis, design, specification, or a plan without authorizing code changes.
- **Auto** applies only when the user explicitly requests autonomous execution. Continue through ready nodes, but still stop for permissions, destructive changes, unclear product decisions, or meaningful scope expansion.

Do not use multiple agents or parallel workers unless the user explicitly requests delegation or the active environment instructions require it. A graph can be executed sequentially.

## Execute the workflow

### 1. Ground the request in the repository

Inspect before proposing architecture or changing code:

1. Read applicable `AGENTS.md`, `CLAUDE.md`, contribution guidance, and package manifests.
2. Check repository status and preserve existing changes.
3. Identify renderer, preload, main or utility process, runtime adapter, storage, shared contracts, test, packaging, and logging boundaries that actually exist.
4. Trace one comparable feature from UI entry to runtime behavior and tests when available.
5. Identify canonical commands for formatting, linting, type-checking, tests, builds, and packaging.
6. Record facts, assumptions, unknowns, and evidence paths separately.

Do not assume that common names such as `AgentService`, `QueryManager`, or `SessionManager` exist. Reuse them if discovered; do not create parallel equivalents without evidence that the existing boundary is insufficient.

### 2. Create the task contract

Translate the plain-language request into:

- **Goal:** one outcome sentence.
- **User-visible behavior:** what changes and what must remain unchanged.
- **Scope:** affected surfaces and explicit exclusions.
- **Acceptance criteria:** observable, testable conditions.
- **Constraints:** architecture, security, compatibility, UX, performance, and rollout requirements.
- **Unknowns:** unresolved facts and their discovery action.
- **Verification:** commands, tests, or inspections that will prove each criterion.

Infer low-risk reversible details from existing patterns. Ask only when a missing choice would materially alter product behavior, architecture, data, security, or scope.

### 3. Build the minimum useful work graph

Create nodes with a single goal, concrete output, dependencies, acceptance criteria, checks, risk, and status. Add an edge only when the downstream node consumes an upstream output or cannot be verified before it. This is the fake-edge test.

- For a local change with one or two independent steps, keep the graph inline.
- For a cross-layer or three-plus-node change, create a JSON graph matching `references/work-graph.schema.json` in an existing repository planning location or a temporary work area. Do not add planning files to the product repository unless they are requested or already conventional.
- Keep the initial core graph stable. Add a dynamic node only after new evidence reveals necessary work; record why it was added.
- Represent repair as another attempt on the same node, not a dependency cycle.
- Keep optional improvements outside the completion path.

Order nodes contract-first: shared types and interfaces before adapters, IPC before renderer consumption, domain behavior before UI polish, and deterministic verification before model review.

### 4. Review the implementation plan

Before editing, check that:

- Every acceptance criterion maps to one or more nodes and checks.
- Every edge passes the fake-edge test.
- Process and trust boundaries are explicit.
- Existing runtime, session, permission, storage, logging, and UI facilities are reused.
- The smallest vertical slice can be built and verified before expansion.
- Rollback, migration, feature-flag, cancellation, and recovery needs are addressed when applicable.

In Guided and Auto modes, proceed after this review unless a stop condition applies.

### 5. Run the bounded node loop

For each ready node:

1. Re-read its inputs, acceptance criteria, affected paths, and checks.
2. Inspect the exact code before editing.
3. Implement the smallest coherent change using current project conventions.
4. Run the narrowest deterministic checks first.
5. Compare results with the node criteria; do not equate command success with feature correctness.
6. On failure, classify the cause before changing code: implementation defect, incorrect assumption, environment issue, flaky check, or requirement conflict.
7. Repair only the diagnosed cause and rerun the failed check plus relevant regression checks.
8. Mark the node verified only when evidence exists. Otherwise mark it blocked or failed and state why.
9. Unlock dependent nodes only after required upstream outputs are verified.

Limit repair to three materially distinct attempts per node. Stop and report evidence when further retries would repeat the same approach or require new authority.

### 6. Verify the integrated feature

Run the applicable gates from `references/verification-gates.md`. Trace each acceptance criterion to evidence. Inspect the final diff for unintended changes, unsafe IPC or permission expansion, UI inconsistency, missing cleanup, and accidental coupling to the Claude SDK or Electron where a stable interface should exist.

Never claim an unchecked gate passed. Report unavailable or impractical checks as **not checked**, with the reason and exact follow-up command or action.

### 7. Report the result

Lead with the implementation outcome. Include:

- What changed and the user-visible effect.
- Key architecture decisions and reused boundaries.
- Work-graph status: verified, blocked, skipped, or deferred nodes.
- Verification evidence with commands and outcomes.
- Checked and not-checked boundaries.
- Residual risks, migrations, or rollout notes.
- Exact next action only when work remains.

Keep progress updates short. Do not make the user reconstruct completion from logs.

## Stop conditions

Stop and request direction when encountering:

- A destructive or irreversible migration not clearly authorized.
- A product decision with materially different user behavior.
- A new permission, credential, external service, or data-sharing boundary.
- A conflict between the request and repository security or architecture rules.
- Unrelated existing changes that overlap the required files and cannot be safely preserved.
- Repeated verification failure after the bounded repair attempts.

Explain the exact blocker, evidence, safe options, and consequence of each option.
