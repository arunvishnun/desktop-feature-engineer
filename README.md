# Desktop Feature Engineer

`desktop-feature-engineer` is a developer-side skill for planning, implementing, testing, and verifying features inside an Electron and TypeScript desktop application that uses the Claude Agent SDK.

The skill uses two internal techniques:

- **Graph engineering:** represent implementation work as verifiable nodes with real dependencies.
- **Loop engineering:** implement, test, diagnose, and repair each node through a bounded loop.

It does not add a graph engine or loop engine to the desktop application unless the requested feature explicitly requires one.

## Package contents

```text
desktop-feature-engineer/
├── SKILL.md
├── README.md
├── references/
│   ├── electron-claude-architecture.md
│   ├── graph-loop-protocol.md
│   ├── verification-gates.md
│   ├── work-graph.example.json
│   └── work-graph.schema.json
├── scripts/
    └── validate_work_graph.py

```

For an Electron application using its own Claude Agent SDK skill loader:

| Item | Needed? | Purpose |
|---|---:|---|
| `SKILL.md` | Yes | Main skill workflow and triggering instructions |
| `references/` | Yes | Architecture, graph-loop, schema, and verification guidance |
| `scripts/` | Yes | Deterministic work-graph validation |
| `README.md` | Optional | Human usage documentation |
| `agents/` | No | ChatGPT/Codex display metadata |
| `assets/` | No | Icon referenced by the ChatGPT/Codex metadata |

You may remove `agents/` and `assets/` from the copy used by your Claude Agent SDK application. Keep them when installing the same package in ChatGPT or Codex.

## Installation

1. Extract the `desktop-feature-engineer` folder.
2. Place it in the project or application skill directory recognized by your desktop application's skill loader.
3. Ensure the Claude Agent SDK session loads project-level instructions and skills.
4. Open the desktop application repository as the active workspace.
5. Invoke the skill by name in the feature request.

The exact directory is determined by the skill loader implemented in your application. The skill cannot become available merely by existing elsewhere on the filesystem.

## Basic usage

A short feature request is sufficient:

```text
Use desktop-feature-engineer.

Add a Stop button for active Claude responses and make cancellation recoverable.
```

The skill will inspect the repository before deciding which files or layers need to change.

## Guided-mode example

Guided mode is the default:

```text
Use desktop-feature-engineer in guided mode.

Add a Stop button while Claude is generating a response. Clicking it should
cancel the active query, display “Cancelled,” and preserve that state when the
conversation is reopened.

Match the existing UI and reuse the current session, query, permission,
persistence, and IPC infrastructure.
```

Expected internal work graph:

```text
Discover cancellation flow
  -> define terminal-state contract
  -> implement runtime cancellation
  -> expose narrow IPC/preload operation
  -> update React state and UI
  -> verify persistence, restart, security, and integration
```

The agent provides short progress updates and continues without asking for confirmation unless it encounters a destructive change, new permission, significant product decision, security conflict, or overlapping user change.

## Plan-only example

Use this when you want a specification without code changes:

```text
Use desktop-feature-engineer in plan-only mode.

Plan a local workflow-history feature. Do not modify code.
```

## Auto-mode example

Auto mode must be requested explicitly:

```text
Use desktop-feature-engineer in auto mode.

Implement export-to-Markdown for conversations. Stop only for a destructive,
security, permission, or major product decision.
```

Auto mode does not bypass user approvals or repository safety rules.

## What the skill does

1. Reads repository instructions and traces comparable code.
2. Converts the request into testable acceptance criteria.
3. Builds the minimum useful dependency graph.
4. Implements one ready node at a time.
5. Runs the narrowest deterministic checks first.
6. Classifies failures before repairing them.
7. Limits repair to three materially different attempts per node.
8. Runs integrated Electron, Claude SDK, IPC, persistence, UI, security, and packaging checks when applicable.
9. Reports verified, blocked, deferred, and not-checked work explicitly.

The skill does not use multiple agents or parallel workers unless the user explicitly requests delegation and the environment permits it.

## Token usage

The current version prioritizes consistency and accuracy over minimum context usage. It instructs the agent to read the main skill and three operating references before implementation.

| Source | Approximate model input |
|---|---:|
| Main `SKILL.md` | 2,000–2,500 tokens |
| Three required references | 4,500–5,500 tokens |
| Graph schema and example, when needed | 1,000–2,000 tokens |
| Repository code and command output | Depends on feature scope |
| Repair loops | Added only when verification fails |

Expect roughly **7,000 tokens of skill guidance before substantial repository exploration**. This is reasonable for medium or large cross-layer features, but relatively expensive for a one-file change.

The deterministic Python validator does not consume model reasoning tokens while it runs, although its command and result appear in the agent context.

### Controlling token use

- Use this skill for features where architecture, IPC, persistence, permissions, recovery, or multiple layers matter.
- For a trivial one-file edit, ordinary coding instructions may be more economical.
- State the exact desired behavior and exclusions so the agent performs less discovery.
- Reuse an existing conversation when the repository architecture is already grounded and still current.
- Avoid requesting multi-agent execution unless the task is broad enough to justify duplicated context.
- Ask for plan-only mode when implementation is not yet authorized.

A future token-optimized version can use conditional reference loading:

- **Fast path:** local one- or two-file changes; main skill only.
- **Standard path:** cross-layer features; architecture and verification references.
- **Complex path:** persistence, permissions, migrations, or broad changes; full graph protocol and schema.

## Work-graph validation

For a persisted JSON graph, run this from the skill directory:

```bash
python3 scripts/validate_work_graph.py path/to/work-graph.json
```

The validator checks required fields, node identifiers, dependency existence, cycles, attempt limits, blockers, and evidence for verified nodes.

## Important boundaries

- The repository is always the source of truth.
- The renderer must not receive direct Node.js, filesystem, credential, or Claude SDK access.
- Existing runtime, sessions, permissions, persistence, logging, and UI patterns should be reused.
- The skill should not create a second agent harness or database without explicit need.
- Graph Engineering, Loop Engineering, Code Graph, and memory remain separate product features even though this development skill uses graph and loop reasoning internally.
