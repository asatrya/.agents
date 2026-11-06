---
name: dev-async-boundary-test
description: "Design and review tests for asynchronous distributed systems by systematically covering time, ordering, concurrency, delivery, retry, idempotency, backpressure, shutdown, schema, security, and operational boundaries. Also find and prevent liveness and overload hazards: thread pool starvation, blocked threads, deadlock, livelock, priority inversion, thundering herd, cache stampede, cascading failure, slow responses, and head-of-line blocking."
---

# Async Distributed-System Boundary Testing

Use this skill when designing, reviewing, or auditing tests for an asynchronous distributed system: queues, brokers, event streams, workers, schedulers, async APIs, WebSockets, workflows, or pipelines.

The goal is to expose incorrect behavior at transition points and failure boundaries, not merely to exercise the happy path or prove that coroutines run concurrently.

Two catalogs back this skill:

- [references/boundary-catalog.md](references/boundary-catalog.md): contract boundaries to test (time, lifecycle, races, ordering, delivery, retry, idempotency, backpressure, shutdown).
- [references/hazard-catalog.md](references/hazard-catalog.md): shared-resource, liveness, and overload hazards to find in code and design (starvation, deadlock, herd, cascade).

Also use this skill when writing or reviewing code that makes different kinds of work share a thread pool, executor, event loop, lock, connection pool, or cache, or that calls a dependency that can hang, even if no tests are being designed yet.

## Workflow

1. Model the system contract before writing tests.
   - Identify producers, consumers, brokers/queues, persistence, external services, acknowledgements, retries, and the delivery guarantee.
   - Record what is guaranteed and what is explicitly not guaranteed: ordering scope, duplication, latency, durability, visibility, cancellation, and recovery.
   - Treat unspecified behavior as a design question. Do not silently assume exactly-once delivery, global ordering, or lossless shutdown.

2. Enumerate the applicable boundaries.
   - Read [references/boundary-catalog.md](references/boundary-catalog.md).
   - Mark each dimension as covered, partially covered, not applicable, or unknown. For every not-applicable dimension, record why.
   - Prioritize boundaries where a side effect, message loss, data leak, unbounded work, or irreversible state transition can occur.

3. Find shared-resource and overload hazards.
   - Ask: **if this dependency hangs for 60 seconds, what else stops working?** A crash is visible; a hang is not. The process stays up, health stays green, and unrelated requests quietly wait.
   - Inventory every pool, executor, lock, semaphore, connection pool, queue, cache, and the event loop, with its size and whether it is bounded. The event loop's default executor is shared by everything that does not name another one.
   - Map each blocking call to the resource it holds while it waits. Assume each dependency hangs until its timeout (or forever if it has none) and list every other path that needs the same resource. That list is the blast radius.
   - Read [references/hazard-catalog.md](references/hazard-catalog.md) and check each hazard that can apply. Mark each covered, partial, absent, unknown, or not applicable with a reason, as in the boundary matrix.
   - Do not fix starvation by only enlarging a shared pool; that moves the limit without removing the shared dependency. Do not add a retry without a limit, backoff, and jitter. Look up a library's real default timeout and pool size instead of assuming it is safe.

4. Turn each boundary and hazard into an observable test.
   - Define the setup, injected condition, expected state transition, externally visible result, and cleanup.
   - Test just-before, exactly-at, and just-after values for numeric and temporal boundaries.
   - Test both directions of state transitions, such as healthy → timeout and timeout → recovery.
   - Combine boundaries when production failures require their interaction, for example max concurrency + timeout + redelivery.
   - For a hazard, write a test that fails on the old design: shrink the shared pool, hang the dependency, and require unrelated work to finish within a bound. A test that passes on both the old and new code proves nothing.

5. Make async tests deterministic.
   - Prefer fake clocks, controllable schedulers, barriers, events, and deterministic queues over arbitrary sleeps.
   - Control task release points so races can be reproduced: before side effect, after side effect, before acknowledgement, and after acknowledgement.
   - Assert completion, cancellation, cleanup, queue state, persisted state, and emitted messages; do not rely on logs or timing alone.

6. Validate the delivery and recovery contract.
   - Exercise duplicates, out-of-order delivery, redelivery, retries, poison messages, partial batch failure, consumer crashes, broker disconnects, and restart.
   - Verify idempotency or deduplication at the business side-effect boundary.
   - Verify that acknowledgement/commit ordering cannot silently lose work or repeat unsafe effects.

7. Review coverage as a matrix, not a test count.
   - Separate unit, component, integration, fault-injection, load, and soak tests.
   - Include a small set of high-value cross-product scenarios rather than every theoretical combination.
   - Report uncovered assumptions, not only failing assertions.

## Required output

When asked to design tests, produce:

- The system contract and assumptions.
- A boundary matrix with status: covered, partial, absent, or unknown.
- A hazard list. Title each hit `[Blocker|Should-fix] – Hazard: what waits behind what`, with the file and line, the shared resource, the numbered trigger sequence (three to five steps), and the fix. Blocker: unrelated work can stall or fail with no bound on how long. Should-fix: the same shape on a short, bounded wait, or a missing test that would catch it. Do not report a hazard you cannot trace to a specific shared resource and a specific hung call.
- Concrete test cases with trigger, observation, and expected invariant.
- The highest-risk boundary combinations.
- Test-fixture and determinism requirements.
- Any contract or implementation decision needed before testing.

## Non-negotiable invariants

Apply only the invariants that the system promises, but check them explicitly when applicable:

- No silent loss of accepted work.
- Duplicate delivery cannot duplicate a non-idempotent business effect.
- Retry limits, backoff, and dead-letter behavior are bounded and observable.
- Ordering is preserved at the promised scope, or reordering is handled explicitly.
- Backpressure prevents unbounded memory, task, connection, and queue growth.
- A hung or slow dependency cannot stall unrelated work: slow or unreliable calls run on their own bounded capacity, and every blocking call has a timeout.
- Concurrent misses for one key cause one dependency call, and timers and retries are jittered so clients do not synchronise.
- Locks are taken in one order and never held across a callback or `await`; no pooled task waits on another task from the same pool.
- Cancellation and shutdown release resources and leave durable state consistent.
- Partial failures cannot acknowledge work that was not durably completed.
- Tenant, authorization, and data-retention boundaries hold under retries and redelivery.
- Recovery converges to a known state after restart, reconnect, or delayed dependencies.

For the detailed boundary dimensions, boundary points, invariants, and example test forms, read [references/boundary-catalog.md](references/boundary-catalog.md). For the hazards, their code signs, fixes, and test recipes, read [references/hazard-catalog.md](references/hazard-catalog.md).
