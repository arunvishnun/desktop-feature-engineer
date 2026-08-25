# Electron and Claude Agent SDK architecture

Use this reference to preserve safe boundaries while adapting to the repository that actually exists.

## Contents

- Discovery precedes design
- Process and trust boundaries
- Reuse the current harness
- Claude Agent SDK integration
- IPC and shared contracts
- Persistence and recovery
- UI and experience integration
- Modularity and scalability
- Observability
- Common feature lanes

## Discovery precedes design

Verify names, locations, and responsibilities in code. Do not manufacture this reference architecture if the repository uses different boundaries. Prefer the existing working pattern unless it violates an explicit requirement or security rule.

Inspect:

- Root and nested `AGENTS.md`, project `CLAUDE.md`, settings, package manifests, and build configuration.
- Electron main, preload, renderer, utility processes, workers, and shared types.
- Agent SDK construction, session lifecycle, query cancellation, streaming events, permission handling, and tool registration.
- Storage schema and migration mechanism.
- Existing feature flags, telemetry, structured logging, and correlation identifiers.
- Test layers and packaging configuration.
- A comparable end-to-end feature path.

## Process and trust boundaries

| Boundary | Owns | Must avoid |
|---|---|---|
| Renderer | React UI, presentation state, user interaction | Direct Node.js, filesystem, credentials, SDK sessions, or privileged tools |
| Preload | Narrow typed bridge and event subscriptions | Generic IPC passthrough, arbitrary channel access, unvalidated payloads |
| Main or utility process | Privileged orchestration, lifecycle, cancellation, policy enforcement | UI rendering logic or renderer-controlled authority |
| Runtime adapter | Claude Agent SDK calls and vendor-specific event normalization | Leaking SDK types through the whole application |
| Domain/core | Stable feature rules, serializable contracts, state transitions | Direct Electron or Claude imports when an interface suffices |
| Persistence | Durable local state and migrations | Multiple competing sources of truth |

Preserve context isolation and sandboxing where configured. Do not weaken `nodeIntegration`, web security, navigation controls, content security policy, or permission checks to simplify a feature.

## Reuse the current harness

Search for existing services responsible for:

- Agent sessions and resume or fork behavior.
- Active query registration, duplicate prevention, and cancellation.
- Tool execution and permission requests.
- Workspace resolution and path authorization.
- Streaming events and structured messages.
- Settings, credentials, logs, and storage.

Reuse these facilities. If components resembling `AgentService`, `QueryManager`, or `SessionManager` exist, extend their public contracts or add a focused collaborator rather than creating a second agent harness.

If the broader runtime may later move outside the desktop team, put new experience behavior behind stable application-owned interfaces. Isolate Claude-specific logic in adapters so UI and domain code consume normalized contracts.

## Claude Agent SDK integration

- Preserve the repository's configured setting sources, project instructions, tool policy, and permission flow.
- Keep workspace and session identity explicit.
- Normalize streaming SDK events before they cross into renderer state.
- Preserve cancellation, graceful shutdown, crash recovery, and session resume.
- Correlate a user request, SDK session, query, tool calls, and UI updates with existing identifiers.
- Do not silently broaden allowed tools or bypass a user approval path.
- Treat prompts and model responses as untrusted data at privileged boundaries.

## IPC and shared contracts

- Define narrow request, response, event, and error contracts in a shared safe location.
- Validate payloads in the privileged process even if TypeScript types exist.
- Prefer domain-specific channels over generic invoke or event forwarding.
- Return serializable data; do not expose Electron or SDK objects.
- Provide unsubscribe and cleanup behavior for event listeners.
- Keep error codes stable enough for renderer handling and tests.
- Version persisted or externally stable contracts when compatibility matters.

## Persistence and recovery

Use the existing local persistence layer as the source of truth. If SQLite already owns sessions, messages, tool calls, permissions, and settings, extend it through the established migration system. Do not introduce another database merely for a feature.

For durable behavior, define:

- Ownership and lifecycle of each record.
- Transaction and partial-failure behavior.
- Migration, downgrade, or rollback expectations.
- Restart and stale-in-flight recovery.
- Retention and deletion.
- Repository or workspace scoping.
- Redaction of secrets and sensitive content.

Use the filesystem only according to existing conventions, typically for user artifacts or logs rather than competing application state.

## UI and experience integration

- Trace existing page, panel, modal, navigation, streaming, empty, loading, error, and permission patterns.
- Reuse design-system components, tokens, spacing, typography, animation, and accessibility behavior.
- Preserve the current desktop application's visual language; do not introduce a standalone visual system.
- Keep long-running work cancellable and make progress, blocked state, recovery, and verification legible.
- Use feature-flagged or pluggable UI slots when the repository already supports them.
- Keep renderer state derived from normalized runtime events, not raw SDK internals.

## Modularity and scalability

- Prefer a focused feature module with explicit public contracts.
- Keep feature-specific code independent from unrelated application areas.
- Reuse shared mechanisms without turning a first feature into a universal framework prematurely.
- Design repeated use cases around data and contracts rather than copied conditionals.
- Add an abstraction only after identifying the concrete variation it isolates.

## Observability

Use existing structured logging and tracing. Capture enough evidence to diagnose:

- Feature or operation name.
- Correlation, session, query, and workspace identifiers where safe.
- State transitions and durations.
- Tool and permission outcomes without secret values.
- Cancellation, retry, recovery, and terminal failure.

Avoid logging prompts, files, credentials, personal data, or model content unless existing policy explicitly permits and redacts them.

## Common feature lanes

Classify the request so the work graph includes only relevant layers:

1. **Renderer-only:** visual or local presentation change with no privileged behavior.
2. **Renderer plus IPC:** UI invokes or observes a privileged application capability.
3. **Runtime integration:** new SDK behavior, tool, streaming event, permission, or session lifecycle.
4. **Durable feature:** persistence, migration, restart, recovery, or history.
5. **Cross-cutting:** coordinated contract, runtime, IPC, UI, observability, tests, and packaging change.

Do not force every feature through all five lanes.
