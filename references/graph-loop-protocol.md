# Graph and loop execution protocol

Use a work graph to make dependencies, outputs, and verification explicit. Use a bounded loop to complete each ready node. The graph is a development artifact, not automatically a product feature.

## Contents

- Task contract
- Choose graph depth
- Node contract
- Edge rules
- Standard graph order
- Readiness and scheduling
- Bounded implementation loop
- Guided progress contract
- Approval boundaries
- Graph completion

## Task contract

Create this contract from the user's plain-language request and repository evidence:

```text
Goal:
User-visible behavior:
In scope:
Out of scope:
Acceptance criteria:
Architecture and security constraints:
Known facts and evidence:
Assumptions:
Unknowns and discovery actions:
Verification plan:
Mode: guided | plan-only | auto
```

Make acceptance criteria behavioral and testable. Avoid criteria such as “clean,” “robust,” or “works well” unless converted to concrete observations.

## Choose graph depth

| Change | Graph treatment |
|---|---|
| One local file or isolated behavior | Inline one-node checklist |
| Two layers with an obvious contract | Small inline dependency graph |
| Three or more layers, persistence, permissions, or migration | JSON work graph and validation |
| Broad, high-risk, or uncertain change | Discovery nodes followed by a validated graph revision |

Do not create graph ceremony that costs more than the change.

## Node contract

Every node must have:

- `id`: stable short identifier.
- `title`: concise action.
- `goal`: one independently verifiable outcome.
- `kind`: discovery, contract, domain, runtime, ipc, persistence, ui, observability, migration, test, packaging, security, or review.
- `dependencies`: IDs whose verified outputs are required.
- `inputs`: specific upstream outputs or repository evidence.
- `outputs`: files, contracts, behavior, or evidence produced.
- `acceptance`: behavioral conditions for completion.
- `checks`: commands or inspections that produce evidence.
- `risk`: low, medium, or high.
- `status`: pending, ready, in_progress, verified, blocked, failed, skipped, or deferred.
- `attempts`: count of materially distinct implementation attempts.
- `evidence`: results supporting verified status.

Keep a node small enough that failure has a clear cause, but large enough to produce a coherent result. A node should not merely mean “edit file X.”

## Edge rules

Add dependency `A -> B` only if at least one is true:

1. B consumes a contract, decision, data shape, or artifact produced by A.
2. B cannot be correctly implemented or verified before A.
3. A is an explicit safety or migration gate for B.

If removing the edge would not alter how B is built or verified, remove it. This is the fake-edge test.

Use dependencies for execution order, not visual storytelling. Keep the graph acyclic. Represent feedback with `attempts` and evidence, not a back edge.

## Standard graph order

Use only the nodes relevant to the feature:

1. Discover current behavior and comparable patterns.
2. Freeze acceptance criteria and shared contracts.
3. Implement domain or harness-neutral behavior.
4. Implement storage or migration when needed.
5. Integrate the Claude runtime adapter when needed.
6. Add secure IPC and preload exposure when needed.
7. Add renderer state and UI.
8. Add observability and recovery.
9. Run layer and integration tests.
10. Run packaging, security, and final acceptance review.

Prefer a small vertical slice over completing every backend node before any end-to-end validation.

## Readiness and scheduling

A pending node becomes ready only when:

- Every dependency is verified or explicitly waived with rationale.
- Required inputs exist.
- No unresolved approval or product decision blocks it.
- Its affected paths can be edited without overwriting unrelated work.

Execute ready nodes sequentially unless delegation is explicitly authorized. Choose the next node by critical-path importance, risk reduction, and ability to produce early end-to-end evidence.

## Bounded implementation loop

For one ready node:

```text
Inspect inputs and code
  -> implement smallest coherent change
  -> run narrow deterministic checks
  -> compare with acceptance criteria
     -> pass: record evidence and verify node
     -> fail: classify cause, repair, and retry
     -> blocked: stop node and report required decision or authority
```

Count only materially distinct repairs as attempts. Use at most three attempts unless the user explicitly authorizes more. Do not change multiple unrelated variables in one repair; preserve diagnostic value.

Classify failure before repair:

- **Implementation defect:** code contradicts known contract.
- **Incorrect assumption:** repository evidence invalidates the plan.
- **Environment issue:** dependency, platform, or service prevents meaningful execution.
- **Flaky check:** failure is nondeterministic and must be reproduced.
- **Requirement conflict:** two criteria cannot both be satisfied as written.
- **Scope discovery:** required work is outside the current graph.

When evidence changes the plan, update the smallest affected subgraph. Record the reason. Do not silently rewrite acceptance criteria to make the implementation pass.

## Guided progress contract

After a meaningful node or phase, report:

- Completed outcome.
- Evidence.
- Current graph status.
- Exact next ready node and why it is next.
- Any decision needed from the user.

Continue automatically when no decision is required. Avoid narrating every command.

## Approval boundaries

Pause before:

- Destructive migrations or data deletion.
- New network destinations, credentials, permissions, or telemetry.
- Disabling Electron security controls.
- Major dependency or framework replacement.
- A product behavior choice that cannot be derived from existing UX.
- Scope expansion beyond the accepted task contract.

## Graph completion

The graph is complete only when:

- Every required node is verified or explicitly waived by the user.
- Every acceptance criterion maps to evidence.
- No blocked node remains on the completion path.
- Integrated verification and final diff review pass.
- Deferred enhancements are clearly separated from required work.

Use `references/work-graph.schema.json` and run `python3 scripts/validate_work_graph.py <graph.json>` from the skill directory for persisted graphs.
