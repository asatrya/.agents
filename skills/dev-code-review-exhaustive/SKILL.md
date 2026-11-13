---
name: dev-code-review-exhaustive
description: Evaluates code diffs or files exclusively for functional correctness, mapping every execution branch, edge case, and failure path. Use when code logic requires mathematical certainty, zero-regression security, or deep path validation before merging.
---

# Exhaustive Correctness Code Review Playbook

Act as a deterministic, zero-compromise correctness-verification agent. Your only review concern is whether the implementation behaves exactly as specified across its reachable states, inputs, and environments. Do not evaluate style, aesthetics, naming, formatting, or refactoring opportunities unless they change behavior.

Do not imply that a review is mathematically exhaustive when the available code, specification, tests, or runtime context leave a state unobservable. State the coverage boundary, distinguish verified behavior from inference, and mark missing evidence as a finding when it prevents a correctness claim.

## Review contract

Before reviewing, identify:

- The change surface: files, symbols, entry points, callers, dependencies, and state mutations.
- The authoritative specification: ticket, acceptance criteria, API contract, invariant, or user-provided requirement. If none is supplied, say that spec alignment cannot be proven.
- The observable result: return value, persisted state, emitted event, response, side effect, or error contract.
- The review boundary: what is in scope and what cannot be verified from the supplied material.

Review only functional correctness. Every conclusion must be tied to a concrete execution path, state configuration, or missing proof obligation.

## Phase 1: Context and constraint mapping

1. **Identify core invariants.** List the state conditions and business rules that must never be broken. Include data integrity, authorization, idempotency, ordering, atomicity, and error-contract invariants where applicable.
2. **Trace intent against implementation.** Cross-reference each changed behavior with the ticket or specification. Flag any mismatch as **CRITICAL**.
3. **Map boundaries.** Identify every entry point, network or process boundary, serialization/deserialization step, external dependency, persistence operation, shared mutable object, retry path, and state mutation.
4. **Locate proof obligations.** For each boundary and mutation, state what must be true before and after it, and which test or code path establishes that fact.

## Phase 2: Complete execution-path profiling

Traverse each relevant possibility systematically. Do not collapse distinct branches into a summary such as “edge cases handled.” Record the actual permutation and its result.

### 1. Control flow and logical combinations

- Evaluate every compound conditional across all boolean combinations, including `True/True`, `True/False`, `False/True`, and `False/False` where both operands are reachable.
- Trace short-circuit behavior and prove that it prevents unsafe dereferences, unintended side effects, or skipped required operations.
- Check switch, match, enum, type, and status handling for every known variant, unknown values, malformed values, and resilient fallback behavior.
- Follow early returns, retries, loops, recursion, cancellation, and timeout branches to their postconditions.
- Verify that each branch preserves the same required invariants or explicitly documents the permitted difference.

### 2. Edge-case matrix

Force-test the structural limits of every parameter and state field:

- **Numeric boundaries:** `0`, `-1`, maximum and minimum representable integers, floating-point values, infinities, `NaN`, rounding boundaries, overflow, underflow, and division by zero.
- **Collections and strings:** `null`/missing values, empty arrays or maps, empty strings, whitespace-only strings, malformed encodings, duplicate lookup keys, unexpected ordering, and massively oversized payloads.
- **Types and schemas:** missing fields, extra fields, wrong types, default values, version skew, invalid enum values, and serialization round trips.
- **Temporal state:** out-of-order events, stale reads, rapid duplicate requests, retries after partial completion, clock skew, time zones, daylight-saving transitions, leap days, and boundary timestamps.
- **Concurrency:** interleavings of shared mutations, lost updates, double application, non-atomic check-then-act sequences, and visibility of partially written state.
- **Environment:** unavailable dependencies, partial network failure, process restart, interrupted I/O, configuration absence, permission errors, and resource exhaustion.

If a value is impossible by contract, cite the contract and verify the enforcement point; do not silently omit the path.

### 3. Failure paths and side effects

- Confirm that caught exceptions are either fully recovered from or propagated with the required error contract. A swallowed exception is a finding unless silent recovery is explicitly specified.
- Check transaction boundaries and partial-failure behavior: no externally visible state may be left corrupted or half-applied.
- Verify deterministic cleanup of file descriptors, database connections, locks, network streams, temporary files, tasks, and other allocated resources through `finally`, `using`, context managers, or equivalent guarantees.
- Check retries, backoff, cancellation, and timeouts for duplicate side effects, leaked work, and incorrect final status.
- Check helper methods for unintended mutation or aliasing that escapes into callers, global state, caches, or shared collections.
- Verify logging, metrics, and error reporting only as they affect behavior, observability required for recovery, or security-sensitive information flow.

## Phase 3: Verification gate

Do not recommend approval when any of the following applies:

- A functional bug, spec mismatch, security-impacting correctness issue, unhandled exception, corrupted state, or unreleased resource is identified.
- A bug fix lacks an automated regression test that reproduces the reported failure path and proves the corrected behavior.
- A missing edge-case handler or state leak prevents deterministic correctness.
- A newly introduced third-party dependency or lockfile change is unvetted, or its behavior is relied upon without isolated validation.
- The implementation contains deferred cleanup, a placeholder such as `TODO` for required behavior, or an explicit “fix/test later” path.

Do not invent tests, runtime results, contracts, or dependency behavior. If evidence is unavailable, report the exact proof gap and the deterministic evidence or code change required to close it.

## Severity flags

Tag every finding with exactly one severity:

- 🟥 **CRITICAL** — Functional bug, broken specification, security issue, corrupted state, or unhandled exception that can crash or misbehave in production.
- 🟨 **REQUIRED** — Missing edge-case handling, missing regression coverage, state/resource leak, unverified dependency, or proof gap that blocks a correctness claim.
- 🟦 **OPTIONAL** — Behavior-preserving improvement, optimization vector, or structural simplification. Optional findings must not be used to block approval.

Use file and line references whenever available. If line information is unavailable, identify the symbol and exact condition instead.

## Required report format

Always use these sections and keep the path table concrete:

### 1. System Invariant & Spec Alignment Analysis

State whether the code fully addresses the stated requirements with no correctness-relevant side effects. List the invariants, the specification evidence, the review boundary, and any unproven assumptions. If approval is blocked, say so explicitly.

### 2. Exhaustive Path Execution Table

| Execution Path / Permutation | Status | Specific Vulnerability / Edge Case Identified |
| :--- | :--- | :--- |
| Payload is null or missing | 🟥 CRITICAL / ✅ VERIFIED | State the exact behavior, including the relevant file and line when applicable. |
| Compound condition: `True/False` | 🟨 REQUIRED / ✅ VERIFIED | State the resulting branch, postcondition, or proof gap. |

Include every reachable branch and each material edge-case permutation. Use `✅ VERIFIED` only when the implementation and available evidence establish the expected behavior. Use a severity flag when a defect or proof gap remains.

### 3. Severity Breakdowns & Action Items

For each finding, write one item in this form:

- **[CRITICAL / REQUIRED / OPTIONAL] [file:line or symbol]:** State the exact state configuration and input needed to trigger the issue, the observed incorrect behavior, why it violates the invariant or specification, and the mandatory deterministic code or test fix. For verified paths, do not create a finding.

End with a concise decision: **APPROVE**, **APPROVE WITH OPTIONAL FOLLOW-UPS**, or **DO NOT APPROVE**. Never recommend approval when a CRITICAL or REQUIRED finding remains.
