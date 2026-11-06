# Concurrency hazard catalog

Companion to [boundary-catalog.md](boundary-catalog.md). That catalog lists the contract boundaries to test; this one lists shared-resource, liveness, and overload hazards to find in code and design. Races, ordering, delivery, retries, idempotency, and backpressure stay in the boundary catalog; this file points to them rather than repeating them.

Each entry has the same parts: what it is, how to spot it in code, the question to ask, the fix, and the test that exposes it. A hazard may be marked not applicable only with a reason that names the code.

## 1. Thread pool starvation and blocked threads

**What:** Every thread in a pool is busy waiting on something slow, so new work, including unrelated work, cannot start. Also called executor starvation. It is a form of head-of-line blocking.

**Spot it:**
- Two or more kinds of work submitted to one pool. In Python `asyncio`, `asyncio.to_thread(...)` and `loop.run_in_executor(None, ...)` both use the loop's single default executor.
- A blocking call (network, disk, lock) inside a pooled task, with no timeout or a long one.
- Pool size left at a default. The `asyncio` default executor has `min(32, cpu_count + 4)` threads, so as few as 5 on a small node. `ThreadPoolExecutor` has its own default; look it up for the Python version in use.
- Many items expiring or starting at the same time, so many tasks block together.

**Ask:** Which pool does each blocking call run on? What other work uses that pool? How long can a call hold a thread, and how many can hold one at once?

**Fix:** Bulkhead. Give slow or unreliable work its own small pool, owned by the component that uses it. Add a timeout to the call. Close the pool on shutdown. Size it for the dependency, not the machine.

**Test:** Shrink the shared pool to one thread, hang the dependency with a barrier or event, then require a cached or unrelated operation to finish within a short `wait_for`. It must fail on the shared-pool design and pass on the isolated one.

## 2. Deadlock

**What:** Each party holds something another party needs, in a cycle, so none can proceed.

**Spot it:**
- Two locks acquired in different orders on different paths.
- A lock held while calling out to code that takes another lock, or calls back.
- **Pool deadlock:** a task running in a pool waits for a second task submitted to the same pool. With every thread occupied by waiting parents, the children never run.
- An `await` while holding a threading lock, or a threading lock taken on the event loop thread.

**Ask:** Is there a single, documented lock order? Does any pooled task block on the result of another task from the same pool?

**Fix:** One global lock order. Do not wait on pool results from inside the same pool. Use try-lock with a timeout and fail loudly. Hold locks for the shortest span and never across a callback or `await`.

**Test:** Run the two paths concurrently with a barrier that forces each to hold its first lock before taking its second. Assert both finish within a timeout.

## 3. Livelock

**What:** Parties keep reacting to each other and make no progress, though nothing is blocked.

**Spot it:** Retry loops with fixed delays shared by many clients; "back off and retry" on lock or claim conflicts; two workers repeatedly claiming and releasing the same item; optimistic-concurrency retries with no limit.

**Ask:** If two parties collide, what makes them stop colliding? Is the retry bounded?

**Fix:** Randomised backoff (jitter), a retry limit, a deterministic tie-break such as an id, or a single owner for the contended item.

**Test:** Run N contenders with a fake clock and assert all finish within a bounded number of attempts.

## 4. Priority inversion

**What:** Important work waits on a lock or resource held by unimportant work that cannot run because other work outranks it.

**Spot it:** A health check, request path, or shutdown handler that needs a lock also taken by a long background job; a low-priority queue sharing a worker with an urgent one.

**Ask:** Can a background or batch task hold something the request path needs?

**Fix:** Keep urgent paths off shared locks and pools, shorten the critical section, or move the background task to its own resource.

## 5. Thundering herd and cache stampede

**What:** Many callers react to the same event at once, usually a cache miss or a timer, and overwhelm the dependency behind it.

**Spot it:**
- Cache entries with the same TTL, created together, so they expire together.
- A miss path that every concurrent caller runs for itself.
- Pods or workers that reload, refresh, or rotate on the same schedule.
- Many clients reconnecting after an outage.

**Ask:** If 1,000 callers miss the same key in the same millisecond, how many calls reach the dependency? If every replica refreshes at once, what happens?

**Fix:** Single-flight (the first caller fetches, the rest wait for that result). Jitter on TTLs and schedules. Serve a stale value while one caller refreshes. A short negative-result cooldown after a failure.

**Test:** Release N concurrent callers for one key behind a barrier and assert exactly one call to the dependency.

## 6. Cascading failure

**What:** One component's slowness or failure makes its callers slow or fail, which spreads up the call chain until the whole system is affected.

**Spot it:** Synchronous call chains with no timeouts; callers that wait on a slow service while holding their own threads or connections; retries that multiply load on a struggling service.

**Ask:** Where does a slow dependency stop propagating? Does each caller give up before its own caller does?

**Fix:** Timeouts that shrink as you go up the chain (each caller's deadline is shorter than its caller's), bulkheads at each boundary, a circuit breaker or cooldown, and load shedding so a struggling service rejects rather than queues.

**Test:** Make the dependency slow, not down, and assert callers return within their own deadline and do not exhaust their pool.

## 7. Slow responses

**What:** A dependency that answers slowly is worse than one that is down. A down dependency fails fast; a slow one ties up threads and connections for the full wait.

**Spot it:** Calls with no timeout, or with a framework default measured in tens of seconds; timeouts set on connect but not on read; one timeout covering a whole batch of independent items.

**Ask:** What is the actual timeout, and where is it set? Is it per call or per batch?

**Fix:** Explicit connect and read timeouts, a deadline carried through the call chain, and a per-item budget for batches.

**Test:** Inject a delay just under and just over the timeout; assert behaviour at both.

## 8. Head-of-line blocking

**What:** Items wait in one queue behind a stuck or slow item that has nothing to do with them.

**Spot it:** A single queue or ordered stream shared by independent keys; one worker draining a mixed queue; a poison message that is retried in place.

**Ask:** Do unrelated items share a line? What happens to the items behind a stuck one?

**Fix:** Separate queues or workers per key or class, a per-item timeout, and a dead-letter path for items that keep failing.

## 9. Unbounded growth and resource leaks

**What:** A queue, task set, connection count, or result list grows without limit, or a resource is never released.

**Spot it:** `asyncio.create_task` with no reference kept or no limit; queues without a maximum size; pools created per request; no `close()` or shutdown path.

**Ask:** What is the maximum, and what happens when it is reached? Who releases this on shutdown?

**Fix:** Bound every queue and task set, reuse pools, and give every owner a `close()` that releases its resources. For overload tests, see section 10 (backpressure, rate, and capacity) of [boundary-catalog.md](boundary-catalog.md).

## Shared fix patterns

| Pattern | Idea |
|---|---|
| Bulkhead | Separate capacity per kind of work so one cannot use up another's |
| Timeout and deadline | Every wait has a bound, and bounds shrink up the chain |
| Single-flight | One in-flight call per key, many waiters |
| Jitter | Randomise timers so clients do not synchronise |
| Circuit breaker, cooldown | Stop calling a dependency that keeps failing, then probe |
| Load shedding | Reject new work early to protect work in progress |
| Lock ordering | One global order for acquiring locks |

## Test recipes

- **Shrink to expose sharing.** Set the pool to one thread (`loop.set_default_executor(ThreadPoolExecutor(1))`). Anything that shares it with a hung call now fails visibly.
- **Hang with a barrier, not a sleep.** Use an `Event` or `Barrier` held inside the fake dependency, released in a `finally`, so the test is deterministic and cannot leave threads stuck.
- **Bound the assertion.** Wrap the operation that should not wait in `asyncio.wait_for(..., timeout=2)`. A hang then fails the test in seconds instead of hanging the suite.
- **Fail first.** Run the new test against the old design. If it passes there, it does not test the hazard.
- **Release before finishing.** Release held fakes and await the hung task in `finally`, so no worker thread outlives the test.

## Where the related checks live

These are in [boundary-catalog.md](boundary-catalog.md), not here:

- Races and interleavings: section 4
- Ordering: section 5
- Delivery and acknowledgement: section 6
- Retry, backoff, poison messages: section 7
- Idempotency and replay: section 8
- Backpressure and capacity: section 10
- Dependency failures and circuit-breaker transitions: section 11
- Shutdown and cleanup: section 16
