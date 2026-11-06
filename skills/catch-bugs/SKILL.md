---
name: catch-bugs
description: >-
  Catches logic bugs that leave a result stale, partial, frozen, or wrong
  while the caller still succeeds and health stays green. Use when
  implementing or reviewing control flow, background work, caches, retries,
  readiness, optional fields, deletes, shared settings, and tests. Use when
  the user asks to catch bugs or review failure modes.
---

# Catch bugs

Ask one question: **can the caller keep succeeding while this state is wrong?**

A crash, a stuck backlog, or a failed health check is safer. The bug is a wrong result while the health check stays green.

Title each hit as:

`[Severity] – [Finding one-liner]`

Severity is **Blocker** or **Should-fix**.

- **Blocker**: the result can be wrong or stale while the caller still succeeds, or a failed attempt is never tried again.
- **Should-fix**: the same kind of mistake, on a path that already fails visibly, or a test that does not prove what it claims.

A domain story (a consumer, a cache, a reload) is only an example of the finding. Say what is wrong in plain language.

## Procedure

1. Name each output and the state it reads (memory, cache, background loop, last saved value).
2. For each piece of state, check the findings below. Skip any that cannot apply.
3. Report hits only.

If the code and the contract do not say whether a source is bounded, or whether a payload is a plain string or a structure, say that is unknown. Do not fill it in.

## Blocker – Health stays green after the helper dies

The main job keeps running. A helper that keeps a lookup table up to date can crash, and nothing is watching it. The ready flag was turned on at startup and is never turned off. Callers keep reading the last saved table, so fields quietly disappear, and the health check stays green.

A log line that says the helper stopped is not enough. Keep a handle to the helper, notice when it dies, and fail the health check for as long as that helper is required. If the main job itself dies, the missing output is obvious. If only the helper dies, the main job keeps publishing from old data.

```text
start() -> ready = true
spawn(loop)          # handle thrown away; the error stays on the task
ready stays true after the loop dies
readers keep serving the last snapshot
```

## Blocker – A failed step is still marked successful

Setup can stop because it ran out of time, found nothing, or hit an error. The next line still sets "ready." The service then answers from an empty or half-loaded table, and nothing reports a failure.

Only the path that actually finished may set success. A timeout, an empty result, and an error must leave the service not ready. Test each way setup can stop early. An untested early return ships as a silent success.

A time limit copied from a quick check (open a connection, send a ping) is the same bug when it is used for a much bigger job (replay a whole log). Size the limit for this job.

```text
catch_up():
  if timed_out: return
  if nothing_assigned: return
ready = true                 # both stops land here
```

## Blocker – A cleared value is kept because it looks like bad data

"Missing," "null," and "garbage" all become the same empty result. Garbage is skipped so the old value stays. A real clear looks the same, so the old value stays forever and later requests keep returning it.

Keep three separate outcomes, and test each one:

- cannot be read: keep the previous value
- can be read, and the field is absent, null, or the wrong type: delete it
- an explicit delete marker: delete it

A test that says "garbage does not delete" does not prove either delete path. Warn only when the old value is kept. A warning on every record during a full reload floods the log.

```text
decode(cleared_record) -> null
decode(garbage) -> null
on null: skip              # a clear never removes the old value
```

## Blocker – Leaving a setting blank stores a different kind of value

With the setting filled in, the stored value is one field inside a structure. With it left blank, the stored value is the whole body. Docs, config, and the real payload can each describe a different choice. Copying the setting from the neighbor can store the wrong thing, or reject every record.

Let the payload contract decide. A plain string is stored as-is. A structure must name the field. If both shapes are possible, test the blank setting against a plain string and against a structure. If you cannot tell whether the source is empty or unbounded, say that is unknown.

```text
neighbor: field = "email"     # body is an object
this one: field left blank     # body is a raw string
doc: field = "id"              # a third story
copying the neighbor's field rejects every raw string
```

## Blocker – One shared switch controls two jobs that need different rules

Two jobs talk to the same system, so they share a setting, a name, a saved position, or a "start from where?" policy. One job should resume where it left off. The other must rebuild a full local copy every time. Changing the shared switch changes both.

The job that needs a full copy must own that rule. A saved position and a split across workers are right when the work is meant to be divided. They are wrong when every worker must hold every key: each worker then silently holds only a fraction. A fallback name that everyone shares causes that split by accident. A "start from the beginning" rule that applies only when no position has been saved stops working after the first save.

```text
full_copy_worker uses pipeline.offset_policy
pipeline.offset_policy flips to "latest"
every copy rebuilds from an empty position and serves misses
```

## Should-fix – The test passes for a second, hidden reason

The check passes, and the branch named in the test never had to run.

- The sample data already lacks the value for a second, unrelated reason, so the rule under test is not what produced the result.
- The test name says "missing record," but the body uses a special placeholder that takes a different branch.
- The setup always installs the happy-path data, so every saved example includes it. The output for "lookup missed" is never checked.
- The test only covers the opposite case (garbage does not delete). The real delete path has no test.

The result needs one cause, and that cause must be the branch the test name claims. Check the degraded output on its own.

```text
# test name: skip when channel is web
fixture.channel = web
fixture.store_id = null      # the output is already missing for this reason
assert output has no location
```

## Blocker – Starting with nothing shuts the worker down for good

If there is nothing to do at startup, the worker returns and finishes. It is started only once. Later, when work appears, the program loads one snapshot, marks itself ready, and has no loop left to apply new updates or deletions. The table freezes, and the health check stays green.

The worker has to stay alive while the list is empty, then start processing when items appear. "Ready" means updates are still being applied.

```text
run():
  if not inputs: return      # the task finishes at startup
later, inputs appear:
  load_once(); ready = true  # nothing reads after that
```

## Blocker – Work is marked done before it finishes

The new desired state is saved first. Then the step that can fail runs. On failure, a different piece of state is rolled back. The next try sees "desired matches saved" and skips the work. The failure is never retried.

Save the new state only after the step succeeds. On failure, put back the previous state so the next try runs again. Rolling back one piece and leaving the other makes the comparison look clean.

```text
recorded = desired          # saved first
try: apply(desired)
except: rollback(config)   # recorded stays at desired
next time: desired == recorded -> return
```

## Should-fix – Bad config crashes the process instead of failing the health check

The intended policy is: bad input keeps the process up and fails the health check. The check lives in a helper the error handler does not cover. The process crashes instead.

Run that check inside the handler that implements the policy.

```text
try: load()
except ConfigError: stay_up(); ready = false
state = cache.fields          # raises ConfigError here, outside the try
```

## Out of scope

A style rule the existing tests already break (a bare `assert` versus `raise AssertionError`) is a convention choice. Mention it only when the task is to change that convention.

## Report

Use this shape. The heading is the finding title.

```markdown
### [Severity] – [Finding one-liner]
- Where it shows up:
- What goes wrong:
- Why it still looks healthy:
- Missing test:
```
