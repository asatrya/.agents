# Async Distributed-System Boundary Catalog

Use this catalog to build a boundary matrix. It is a discovery aid, not a requirement that every system implement every feature. A dimension may be marked not applicable only with a reason grounded in the system contract.

For hazards that come from sharing a limited resource rather than from the contract (starvation, blocked threads, deadlock, livelock, thundering herd, cascading failure, slow responses), see [hazard-catalog.md](hazard-catalog.md). Sections 4, 7, 10, and 11 below link to its matching entries.

## 1. Data and input boundaries

Test empty, missing, null, minimum, maximum, just-inside, just-outside, malformed, oversized, duplicate, and unknown values.

Check:

- validation occurs before enqueueing and again at trust boundaries where needed;
- malformed or poison data is rejected, isolated, or dead-lettered without wedging the consumer;
- serialization preserves precision, encoding, optional fields, and identifiers;
- a message that is valid at production time remains interpretable after schema or configuration changes.

For numeric or length limits, use boundary-value analysis: below minimum, minimum, normal, maximum, above maximum, and unbounded/omitted input where relevant.

## 2. Time, deadlines, and clocks

Test just before, exactly at, and just after:

- request, processing, lease, visibility, retry, acknowledgement, and shutdown deadlines;
- message TTL, event-time window, schedule time, and retention expiry;
- clock skew, future timestamps, stale timestamps, daylight-saving transitions, and monotonic-clock versus wall-clock usage.

Check timeout semantics separately from cancellation semantics. A timed-out task may have already performed a side effect. Verify whether the side effect is committed, rolled back, retried, or reconciled.

Prefer a fake clock or controllable scheduler. If the real broker owns the clock, use a focused integration test for the broker boundary and keep the rest deterministic.

## 3. Lifecycle and task state

Exercise states such as created, scheduled, running, blocked, completed, failed, cancelled, timed out, abandoned, redelivered, and terminally dead-lettered.

Inject failure or cancellation:

- before the first await;
- while waiting for a dependency;
- after validation but before the side effect;
- after the side effect but before persistence or acknowledgement;
- after acknowledgement or commit;
- during cleanup and shutdown.

Check that tasks are awaited or supervised, exceptions are not lost, cancellation propagates according to contract, and cleanup is idempotent. Do not swallow cancellation merely to make a test pass.

## 4. Concurrency and races

Test 0, 1, the configured maximum, and maximum-plus-one concurrent operations. Include simultaneous operations for the same key and for different keys.

Use barriers or events to force interleavings at critical points:

- read → await → write races;
- two workers claiming the same message;
- concurrent updates to the same aggregate or idempotency key;
- lock acquisition, timeout, cancellation while holding a lock, and waiter cancellation;
- starvation, unfairness, and tasks that never yield (for shared pools, deadlock, and livelock, see hazard-catalog.md entries 1 to 3).

Assert invariants rather than a particular scheduler order unless ordering is part of the contract.

## 5. Ordering, partitioning, and causality

Test:

- correct order, reversed order, partial order, and equal timestamps;
- duplicate events before and after their original event;
- delayed predecessors, missing predecessors, and late arrivals;
- ordering within a key/partition versus ordering across keys/partitions;
- concurrent updates that produce conflicting versions;
- replay and recovery from an earlier offset.

Verify whether the system rejects, buffers, reorders, compensates, or accepts out-of-order events. Do not claim global ordering when only per-key ordering is guaranteed.

## 6. Delivery, acknowledgement, and durability

Make the delivery guarantee explicit: at-most-once, at-least-once, effectively-once through idempotency, or another contract.

Test crash points around the acknowledgement/commit boundary:

1. receive but do not process;
2. process and fail before the business side effect;
3. perform the side effect and fail before durable state or acknowledgement;
4. persist state and fail before acknowledgement;
5. acknowledge and then fail before downstream publication;
6. restart and redeliver.

Check for silent loss, unsafe duplication, acknowledgement of partial work, offset advancement, replay behavior, and consistency between durable state and emitted events. If the design needs atomic publication, test the outbox/inbox or transaction boundary explicitly.

## 7. Retry, backoff, and poison messages

Test a success on the first attempt, transient failures followed by recovery, permanent failure, failure on the last permitted attempt, and failure during backoff.

Check:

- maximum attempts and maximum elapsed retry time;
- exponential backoff, jitter, and retry storms;
- retry classification and non-retryable errors;
- redelivery after consumer restart;
- dead-letter routing, retention, replay, and operator recovery;
- poison messages cannot block unrelated work or repeatedly consume all capacity (see hazard-catalog.md entries 3 and 8 for livelock and head-of-line blocking).

## 8. Idempotency, deduplication, and replay

Send the same message once, twice, many times, concurrently, after a timeout, after acknowledgement, and after a process restart.

Check idempotency at the actual side-effect boundary, not only in an in-memory handler. Test expired, reused, missing, malformed, and colliding idempotency keys. Verify the behavior when the idempotency record exists but the business effect is missing, and when the effect exists but the record is missing.

## 9. Batching and partial progress

Test empty, one-item, normal, maximum-size, maximum-plus-one, and mixed-validity batches.

Inject failure at the first, middle, and last item. Verify whether the contract is all-or-nothing, per-item acknowledgement, checkpointed progress, or retry of the complete batch. Check that a failed item does not cause successful items to be duplicated or silently skipped.

## 10. Backpressure, rate, and capacity

Test producer rate below, at, and above consumer capacity. Fill every bounded resource:

- queue capacity;
- worker slots and semaphores;
- task backlog;
- connection pool;
- broker partitions or consumer credits;
- memory, disk, and file descriptors where relevant.

Check whether producers block, shed work, reject, sample, or spill to durable storage. Measure queue depth, oldest-item age, processing latency, throughput, and recovery after overload. Include slow consumers, stalled dependencies, and capacity returning after a surge. For slow responses and unbounded growth, see hazard-catalog.md entries 7 and 9.

## 11. External dependencies and network failures

Exercise dependency success, timeout, connection refusal, connection reset, partial response, malformed response, rate limiting, authentication expiry, DNS failure, and recovery after reconnect.

Check connection-pool reuse and exhaustion, retry amplification, circuit-breaker transitions, hedging or duplicate requests, fallback correctness, and whether a dependency failure blocks unrelated work. That last check is the bulkhead question: see hazard-catalog.md entries 1, 5, and 6 for shared pools, thundering herd, and cascading failure.

## 12. Persistence and transactional boundaries

Test commit, rollback, deadlock, serialization conflict, lost connection, partial write, duplicate write, stale read, and restart during commit.

Verify the intended relationship among database state, offsets, acknowledgements, and outbound events. Test recovery when only one part of a multi-step operation succeeded. If compensation is used, test compensation failure and repeated compensation.

## 13. Schema, version, and compatibility boundaries

Run old producer → new consumer, new producer → old consumer where supported, mixed-version consumers, missing optional fields, unknown fields, enum additions, field renames, and incompatible type changes.

Check replay of historical messages, rolling deployment, migration rollback, dual-read/dual-write periods, and dead-letter messages created by version mismatch.

## 14. Security, tenancy, and data isolation

Test missing, expired, rotated, malformed, and insufficient credentials. Attempt cross-tenant object access, replay of another tenant's message, forged producer identity, altered routing keys, and duplicate delivery under a different authorization context.

Check that authorization is evaluated at the side-effect boundary and after redelivery, not only when a message first enters the system. Verify sensitive data is not leaked into logs, dead-letter payloads, retries, traces, or error responses.

## 15. Event time, windows, and scheduling

For time-windowed or scheduled systems, test events at the opening, closing, and just outside a window; late events; future events; empty windows; overlapping windows; repeated schedules; missed schedules; and restart around a scheduled boundary.

Check watermark, grace-period, deduplication, timezone, daylight-saving, and replay semantics. Distinguish event time, processing time, ingestion time, and wall-clock scheduling.

## 16. Shutdown, deployment, and recovery

Test graceful shutdown while idle, receiving, processing, waiting for a dependency, retrying, holding a lease, and draining a batch. Also test immediate termination and restart during each state.

Check stop-accepting-new-work behavior, in-flight completion or cancellation, lease/visibility renewal, offset safety, resource cleanup, and bounded shutdown time. During rolling deployment, test mixed versions, duplicate consumers, partition reassignment, and temporary loss of ownership.

## 17. Observability and operational boundaries

Verify metrics, logs, and traces at normal, slow, failed, retried, dead-lettered, cancelled, and overloaded paths.

At minimum, make it possible to identify:

- message or correlation ID;
- tenant and partition/key where safe;
- attempt number and delivery count;
- enqueue, start, side-effect, commit, acknowledge, and completion times;
- queue depth, oldest age, consumer lag, retry rate, dead-letter rate, and cancellation count.

Check cardinality limits, redaction, trace propagation across tasks and queues, and alerts for sustained rather than single-event noise.

## 18. Test-method boundaries

Use multiple layers:

- deterministic unit tests for state machines and idempotency decisions;
- component tests with controllable queues, clocks, and dependencies;
- integration tests for actual broker, database, and acknowledgement semantics;
- fault-injection tests for crash points and network failures;
- load and soak tests for lag, memory, resource exhaustion, and recovery;
- replay tests for historical and duplicate events.

Do not use arbitrary sleeps as proof of ordering or completion. Do not assert only that tasks finished; assert the durable and externally visible invariants. A passing unit test around `asyncio.gather()` does not establish broker delivery, retry, or recovery correctness.

## Suggested coverage report

For each dimension, record:

```text
Dimension: acknowledgement boundary
Contract: at-least-once delivery; business effect must be idempotent
Boundary: side effect committed, acknowledgement not committed
Injection: terminate consumer after commit and before ack
Expected: redelivery produces no duplicate effect; ack eventually advances
Layer: broker integration + fault injection
Status: covered / partial / absent / unknown
```

Prioritize absent boundaries that can cause data loss, duplicate financial or customer-visible effects, cross-tenant access, unbounded resource growth, or unrecoverable backlog.
