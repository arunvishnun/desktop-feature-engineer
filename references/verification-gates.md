# Verification gates

Use the smallest relevant gate set, then run broader integration checks after the vertical slice works. Deterministic evidence precedes qualitative review.

## Contents

- Evidence rules
- Layer matrix
- Canonical check order
- Claude Agent SDK scenarios
- Electron security review
- Recovery and lifecycle review
- UX consistency review
- Acceptance trace
- Final diff and scope review

## Evidence rules

- Map every acceptance criterion to at least one check or direct inspection.
- Record the command or inspection, exit status or result, and relevant scope.
- Distinguish **passed**, **failed**, and **not checked**.
- Never describe a model review, code reading, or absence of errors as proof that executable behavior passed.
- Do not hide warnings that materially affect the feature.
- Re-run relevant regression checks after repair.

## Layer matrix

| Layer | Minimum applicable evidence |
|---|---|
| Domain/core | Focused unit tests for normal, boundary, invalid, cancellation, and failure behavior |
| Runtime adapter | Contract tests with deterministic SDK fakes; event normalization; abort and permission paths |
| IPC/preload | Payload validation, allowed channels, error serialization, listener cleanup, unauthorized input rejection |
| Renderer state | Reducer/store/hook tests for ordered, duplicated, delayed, failed, cancelled, and resumed events |
| UI | Component interaction, loading, empty, error, blocked, completion, keyboard, and accessibility behavior |
| Persistence | Migration, transaction, restart, partial write, stale state, retention, and workspace scoping |
| Observability | Correlation and terminal events without secret or sensitive content leakage |
| Packaging | Production build and packaged-path behavior for changed native, worker, preload, or asset code |
| Security | Context isolation, Node exposure, navigation, CSP, permissions, path validation, and untrusted content handling |
| Integration | Main-to-preload-to-renderer or UI-to-runtime vertical path using controlled fixtures |

## Canonical check order

Discover actual project commands; do not invent command names. Prefer:

1. Format or targeted syntax validation.
2. Focused unit or contract tests.
3. Type-check changed packages.
4. Lint changed packages.
5. Related integration tests.
6. Renderer or Electron end-to-end tests when behavior crosses processes.
7. Production build.
8. Packaging smoke test when packaging-sensitive code changed.
9. Security and final diff inspection.

If the repository lacks a check, report the gap instead of introducing a testing framework unless the task authorizes that scope.

## Claude Agent SDK scenarios

When the feature affects agent behavior, verify applicable scenarios with deterministic fakes before live-model testing:

- Session creation and resume.
- Fork or branch behavior when supported.
- Streaming text and structured tool events.
- Permission request, approval, denial, timeout, and cancellation.
- Duplicate active-query prevention.
- User cancellation and process shutdown.
- SDK error, malformed event, and partial stream.
- Workspace identity and path boundary enforcement.
- Correlation from request through terminal state.

Use live SDK calls only when they are necessary, authorized, stable enough to interpret, and do not expose sensitive data. Do not make a live model's favorable response the only correctness test.

## Electron security review

For changes crossing a trust boundary, verify:

- The renderer cannot access Node.js, filesystem, credentials, or SDK clients directly.
- The preload bridge exposes only named typed operations.
- The privileged handler validates runtime payloads and authorization.
- Event subscriptions have deterministic cleanup.
- Untrusted content is not executed or interpolated into unsafe HTML, shell commands, paths, or URLs.
- Path access is workspace-scoped and resistant to traversal and symlink escape according to repository policy.
- New permissions are visible, deliberate, and least-privileged.
- Existing context isolation, sandbox, CSP, navigation, and window-open restrictions remain intact.

## Recovery and lifecycle review

When state or long-running work changes, verify:

- Cancellation reaches the owning operation and produces one terminal state.
- Restart does not leave work falsely active.
- Partial completion is recoverable or clearly terminal.
- Duplicate delivery is idempotent or safely rejected.
- Listeners, timers, workers, handles, and SDK sessions are cleaned up.
- Shutdown does not corrupt durable state.

## UX consistency review

Verify against existing screens rather than personal preference:

- Components and tokens match the current design system.
- Progress and status language are consistent.
- Errors explain the failed action and recovery path.
- Long-running work can be cancelled where appropriate.
- Focus order, keyboard interaction, labels, contrast, reduced motion, and screen-reader semantics are preserved.
- New UI fits current layout density and desktop resizing behavior.

Use screenshot or rendered visual comparison when layout materially changes and the environment supports it.

## Acceptance trace

Before completion, create a compact trace:

| Criterion | Implementation location | Evidence | Status |
|---|---|---|---|
| Observable requirement | Relevant files or component | Command or inspection result | Passed / Failed / Not checked |

Do not mark the feature complete while a required criterion is failed or unverified. State why a check is unavailable and the exact follow-up needed.

## Final diff and scope review

Check:

- No unrelated user changes were overwritten.
- No debug logs, temporary bypasses, fixtures, secrets, generated debris, or dead code remain.
- Public contracts and migrations are intentional and compatible.
- The implementation reuses existing harness and UI patterns.
- Claude-specific and Electron-specific coupling is contained at the proper adapter boundaries.
- Documentation is changed only where the repository convention or feature requires it.
- Deferred work is not required for current acceptance.
