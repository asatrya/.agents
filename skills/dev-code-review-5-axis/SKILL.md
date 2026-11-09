---
name: dev-code-review-5-axis
description: Conducts multi-axis code review. Use before merging any change. Use when reviewing code written by yourself, another agent, or a human. Use when you need to assess code quality across multiple dimensions before it enters the main branch. Use when asked to review a diff or a pull request, even when the diff is pasted inline. Runs one subagent per axis, plus a tests subagent, in parallel, then merges and verifies their findings. When the repository keeps Allium specs (*.allium), adds a spec-alignment reviewer that runs /allium:weed in check mode.
---

# Dev Code Review — 5 Axis

## Overview

Multi-dimensional code review with quality gates. Every change gets reviewed before merge — no exceptions. Review covers five axes: correctness, readability, architecture, security, and performance. Each axis gets its own subagent, and a sixth runs the tests. If the repository keeps Allium specs, a seventh checks spec alignment (see Spec Alignment). All of them run in parallel, and the orchestrator merges and verifies their findings (see Review Process).

**The approval standard:** Approve a change when it definitely improves overall code health, even if it isn't perfect. Perfect code doesn't exist — the goal is continuous improvement. Don't block a change because it isn't exactly how you would have written it. If it improves the codebase and follows the project's conventions, approve it.

## When to Use

- Before merging any PR or change
- After completing a feature implementation
- When another agent or model produced code you need to evaluate
- When refactoring existing code
- After any bug fix (review both the fix and the regression test)

## The Five-Axis Review

Every review evaluates code across these dimensions. Each one is handed to its own reviewer subagent (Review Process, Step 2), so each section has to stand on its own.

### 1. Correctness

Does the code do what it claims to do?

- Does it match the spec or task requirements?
- Are edge cases handled (null, empty, boundary values)?
- Are error paths handled (not just the happy path)?
- Does it pass all tests? Are the tests actually testing the right things?
- Are there off-by-one errors, race conditions, or state inconsistencies?
- Where else is the same syntax parsed or validated (templates, paths, identifiers, patterns)? Do all of them accept the same grammar? Find what the looser one accepts that the stricter one passes through untouched.

**Lifecycle and state** (for services, background tasks, consumers, caches, anything with a start/stop):

- Draw the lifecycle (start → ready → reload → stop → crash). For each pair of transitions that can overlap, what happens?
- For each object that two concurrent tasks can reach — a client, connection, consumer, cursor, iterator, buffer, or cache — list every code path that reads, advances, reassigns, or closes it. Can two of those paths run at the same time? If so, which one assumes it is the only user, and what breaks when it isn't? A guard on one path, such as an event or lock at startup, says nothing about the others, such as reload or shutdown. If you decide the sharing is safe, say what that rests on: the library's documented contract, or your own model of its internals. If it's your model, read the source or report the concern as unverified, not as fine.
- For every readiness or health signal, what does it report in each phase that isn't steady state: startup, reload, retry, recovery, shutdown? A flag that only tracks the startup path is wrong during reload. Phases that run on a fixed schedule (rule reload, cache refresh, credential rotation) line up across replicas, so what happens to the fleet when every pod is in that phase at once?
- When an update runs several steps in order (resubscribe, swap config, rebuild an engine) and one step fails or rolls back, which later steps should still run? Is the system consistent in each outcome, and does the caller learn which outcome happened, or does a rollback return as if it succeeded?
- When a background task dies, what keeps running against its stale output?
- Are "none → some" and "some → none" transitions handled like "some → more"? At each entry point (start, reload, per-record handling), what happens with an empty set, a null key, or a timeout?
- If only one config field changes, does it trigger the right side effect?
- Does every acquire path release on *every* exception type, not just the expected one?
- For each new call that can raise on the startup or reload path — including property getters and validators, not just I/O — find the `try` it actually lands in. Is it the handler that implements the documented degraded mode (for example "stay up, report not-ready"), or a broader one that re-raises into a crash loop? Is the call placed outside the `try` it was meant to be inside?
- When one time or retry budget covers a batch of independent items, is it set once for the batch or fresh for each item? If one item uses it all up, do the rest fail loudly or get skipped quietly? Trace a skipped item back to where its budget was computed, not just to how the skip is handled.
- When the feature degrades silently, how would anyone notice? Can a log or metric tell "lookup missed" apart from "nothing expected"?
- For every third-party attribute or private API touched: does it exist in the pinned version? Read the installed source, not memory.

**Shared resources and hazards** (for any change that runs work on a thread pool, executor, event loop, lock, connection pool, or cache, or calls a dependency that can hang):

- Which pool, executor, or loop does each blocking call run on, and what else uses it? The event loop's default executor is shared by everything that does not name another one.
- If this dependency hangs until its timeout, what unrelated work stops? Compare the threads, connections, or permits that hung calls can hold at once with the pool's real size.
- Does every blocking call have a timeout, and what is its real value? Read the installed library's default, not memory.
- If many callers miss the same key, or every replica refreshes at the same moment, how many calls reach the dependency?
- Are locks taken in one order and never held across a callback or `await`? Does a pooled task wait on another task from the same pool?
- Read `../dev-async-boundary-test/references/hazard-catalog.md` (relative to this file) and answer each entry that can apply to this change: starvation, deadlock, livelock, priority inversion, thundering herd, cascading failure, slow responses, head-of-line blocking, unbounded growth. An entry with nothing in this change to check it against goes under "Not applicable", with the reason.

### 2. Readability & Simplicity

Can another engineer (or agent) understand this code without the author explaining it?

- Are names descriptive and consistent with project conventions? (No `temp`, `data`, `result` without context)
- Is the control flow straightforward (avoid nested ternaries, deep callbacks)?
- Is the code organized logically (related code grouped, clear module boundaries)?
- Are there any "clever" tricks that should be simplified?
- **Could this be done in fewer lines?** (1000 lines where 100 suffice is a failure)
- **Are abstractions earning their complexity?** (Don't generalize until the third use case)
- Would comments help clarify non-obvious intent? (But don't comment obvious code.)
- Are there dead code artifacts: no-op variables (`_unused`), backwards-compat shims, or `// removed` comments?
- **Is a new conditional bolted onto an unrelated flow?** That's a design smell, not a nit — push the logic into its own helper, state, or policy instead of tangling an existing path.
- **Do repeated conditionals on the same shape appear?** They signal a missing model or dispatcher. A "temporary" branch is usually permanent debt.
- Do docs describe what was built, or still describe it as "proposed"/planned?

### 3. Architecture

Does the change fit the system's design?

- Does it follow existing patterns or introduce a new one? If new, is it justified?
- Does it maintain clean module boundaries?
- Is there code duplication that should be shared?
- Are dependencies flowing in the right direction (no circular dependencies)?
- Is the abstraction level appropriate (not over-engineered, not too coupled)?
- **Does this refactor reduce complexity or just relocate it?** Count the concepts a reader must hold to follow the change. If a "cleaner" version leaves that count unchanged, it isn't cleaner — prefer the restructuring that makes whole branches, modes, or layers disappear over one that re-centralizes the same logic. Prefer deleting an abstraction to polishing it.
- **Is feature-specific logic leaking into a shared or general-purpose module?** Keep logic in its owning layer, reuse the existing canonical helper instead of a near-duplicate, and don't normalize architectural drift.
- **Are type boundaries explicit?** Question gratuitous `any`/`unknown`/optional/casts and silent fallbacks that paper over an unclear invariant — making the boundary explicit often makes the surrounding control flow simpler.
- **Does the library already provide what the hand-written code does?** Prefer deleting the loop to patching it.
- **Does the change alter a contract other teams or tenants consume** (topic, API, schema)? Is it registered, versioned, and signed off?
- **Is each path live today or only under a planned deployment change?** Label findings "live" or "latent" so severity is honest.
- **Does the change depend on, or get depended on by, a change in another repo** (infra, IAM, topic or queue provisioning, schema registry, config)? What is the safe deploy order, and what breaks if they go out the other way round? Does anything the code needs at startup (a topic, table, bucket, permission) exist in every environment before the first deploy?
- **What do the repo's own rules require?** Read `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING`, and lint or test conventions before reviewing, and check the new code against them. If the existing code already breaks a rule, say whether the change widens that drift and which should win.
- **Which conventions apply from outside this repo?** Sibling services, a parent workspace, or a team rules directory may hold conventions the team expects here too. Say which ones apply, whether this repo's lint actually enforces them, and whether the new code is at least consistent with itself.

### 4. Security

For detailed security guidance, see `security-and-hardening`. Does the change introduce vulnerabilities?

- Is user input validated and sanitized?
- Are secrets kept out of code, logs, and version control?
- Is authentication/authorization checked where needed?
- Are SQL queries parameterized (no string concatenation)?
- Are outputs encoded to prevent XSS?
- Are dependencies from trusted sources with no known vulnerabilities?
- Is data from external sources (APIs, logs, user content, config files) treated as untrusted?
- Are external data flows validated at system boundaries before use in logic or rendering?
- Does any new output carry personal data? Who approved that exposure?
- Do config/schema models reject unknown keys? Check by experiment: misspell one optional key in a sample config and load it. If it loads, what does the output become with that field left at its default?

### 5. Performance

For detailed profiling and optimization, see `performance-optimization`. Does the change introduce performance problems?

- Any N+1 query patterns?
- Any unbounded loops or unconstrained data fetching?
- Any synchronous operations that should be async?
- Any unnecessary re-renders in UI components?
- Any missing pagination on list endpoints?
- Any large objects created in hot paths?
- Does new in-memory state fit the deployment's resource limits? Read the manifest for the actual number, then size the state: records today × average record size, and what drives growth. "Bounded" is not a number.

## Spec Alignment (Allium)

Applies only when the repository keeps Allium specs. Detect that in Step 1: `git ls-files '*.allium'` lists files, a file carries an `-- allium:` version marker, or `CLAUDE.md` / `AGENTS.md` mention Allium. If none of these holds, skip this section, the spec-alignment reviewer, and its checklist block, and write "no Allium specs" in the context packet.

Where specs exist they are the source of truth for behaviour. A change that alters behaviour without changing the spec is drift. A change to a spec with no matching code or tests is a promise nothing keeps. Both belong in the same change unless the repo's own rules say otherwise.

The spec-alignment reviewer runs the `allium:weed` skill in **check** mode over every spec the change touches or implements, and answers:

- For each behaviour the diff adds or changes, does a spec rule, entity, config value, invariant, or guarantee state it? If the diff edits a `.allium` file, does the code do what the edited text says?
- Where the spec says X and the code does Y, which is right? Classify each divergence as code bug, spec bug, aspirational design, or intentional gap, with the reasoning.
- Process-level: transitions declared in the spec that no code path produces, code transitions the spec does not declare, surface triggers with no entry point, invariants nothing enforces.
- If the diff edits a spec, run `allium check` on it and compare with the base ref. A new warning or any error is a finding. A repo may document a known baseline in `CLAUDE.md` / `AGENTS.md`; read it before counting.

Check mode changes nothing. The update-spec and update-code modes of weed belong to the author, after the review.

Severity of a divergence:

| Divergence | Severity |
|---|---|
| Introduced or widened by this change: code bug | Required (Critical if it breaks a guarantee consumers rely on) |
| Introduced or widened by this change: spec bug (behaviour changed, spec not updated) | Required |
| Already there, in code this change does not touch | FYI, listed so the author can decide; not blocking |
| Aspirational design | FYI |
| Intentional gap | "Checked, fine", with the reason |

## Structural Remedies

When you flag a structural problem, propose the move — not just the problem. A review that only says "this is complex" leaves the author guessing. Reach for a named restructuring:

- **Replace a chain of conditionals** with a typed model or an explicit dispatcher.
- **Collapse duplicate branches** into a single clearer flow.
- **Separate orchestration from business logic** so each reads on its own.
- **Move feature-specific logic** out of a shared module into the package that owns the concept.
- **Reuse the canonical helper** instead of a bespoke near-duplicate.
- **Make a type boundary explicit** so downstream branching disappears.
- **Delete a pass-through wrapper** that adds indirection without clarifying the API.
- **Extract a helper, or split a large file** into focused modules.

Prefer the remedy that removes moving pieces over one that spreads the same complexity around.

## Plain-Language Findings

Make every issue and recommendation understandable to a capable engineer who did not write the change. Technical precision and plain language are both required:

- Start with the practical problem, then name the technical concept if it helps. Do not write only "race condition," "N+1," "injection," or "type leak"; explain what can happen in this code.
- State the impact in concrete terms: who or what is affected, under which condition, and what the result is (for example, stale data, a failed request, exposed information, or slower processing).
- Make the recommendation actionable. Say what to change and where, using a named restructuring when one applies. Avoid vague advice such as "handle this better" or "improve performance."
- Define acronyms and specialist terms on first use when the audience may not know them. Keep exact identifiers, API names, and file/line references unchanged so the finding remains verifiable.
- Use this order in each finding: issue in plain language → why it matters → evidence and failure scenario → recommended fix.

Example:

> Required live `src/cache.ts:42`: Two requests can update the same cache entry at the same time. In simple terms, the later write can erase the earlier one and leave callers with stale data. Evidence: ... Failure scenario: ... Remedy: serialize updates with the existing per-key lock.

Do not remove technical evidence to make a finding simpler; explain it. The reader should be able to answer three questions without guessing: “What is wrong?”, “Why should I care?”, and “What should I do?”

## Change Sizing

Small, focused changes are easier to review, faster to merge, and safer to deploy. Target these sizes:

```
~100 lines changed   → Good. Reviewable in one sitting.
~300 lines changed   → Acceptable if it's a single logical change.
~1000 lines changed  → Too large. Split it.
```

**Watch file size, not just diff size.** A small diff can still push a file past a healthy boundary — around 1000 *total* lines in a single file (distinct from the ~1000 *changed*-lines threshold above) is a common inspection signal, not a hard cap. When a change materially grows an already-large file, ask whether to extract helpers, subcomponents, or modules *first*, before piling more on. Decompose, then add.

**What counts as "one change":** A single self-contained modification that addresses one thing, includes related tests, and keeps the system functional after submission. One part of a feature — not the whole feature.

**Splitting strategies when a change is too large:**

| Strategy | How | When |
|----------|-----|------|
| **Stack** | Submit a small change, start the next one based on it | Sequential dependencies |
| **By file group** | Separate changes for groups needing different reviewers | Cross-cutting concerns |
| **Horizontal** | Create shared code/stubs first, then consumers | Layered architecture |
| **Vertical** | Break into smaller full-stack slices of the feature | Feature work |

**When large changes are acceptable:** Complete file deletions and automated refactoring where the reviewer only needs to verify intent, not every line.

**Separate refactoring from feature work.** A change that refactors existing code and adds new behavior is two changes — submit them separately. Small cleanups (variable renaming) can be included at reviewer discretion.

## Change Descriptions

Every change needs a description that stands alone in version control history.

**First line:** Short, imperative, standalone. "Delete the FizzBuzz RPC" not "Deleting the FizzBuzz RPC." Must be informative enough that someone searching history can understand the change without reading the diff.

**Body:** What is changing and why. Include context, decisions, and reasoning not visible in the code itself. Link to bug numbers, benchmark results, or design docs where relevant. Acknowledge approach shortcomings when they exist.

**Anti-patterns:** "Fix bug," "Fix build," "Add patch," "Moving code from A to B," "Phase 1," "Add convenience functions."

## Review Process

The review runs in three phases. You, the orchestrator, set the context. Six subagents then review in parallel: one per axis, plus one for tests, and a seventh for spec alignment when the repository has Allium specs. You merge their reports into a single review. Subagents start with no memory of this conversation, so everything they need goes into their prompt.

### Step 1: Understand the Context (orchestrator)

Before looking at code, understand the intent:

```
- What is this change trying to accomplish?
- What spec or task does it implement?
- What is the expected behavior change?
```

Then write down the change's surface before reading any line in detail. Each item on this list is something a later checklist question must be checked against. A question with nothing listed to check it against gets skipped without anyone noticing.

```
- Outputs: every topic, API, table, file, log, or metric the change writes to, and who consumes each
- Shared objects: every client, connection, consumer, iterator, cache, or store reachable from more than one task
- Limits and budgets: every timeout, deadline, retry count, memory or CPU limit, and queue size the change sets or relies on
  (read the deployment manifest for the real numbers)
- Failure handlers: every try/except, error callback, or readiness gate on the paths the change touches
- External dependencies: everything that must exist outside this repo (infra, IAM, schemas, other services) and its deploy order
- Repo rules: CLAUDE.md / AGENTS.md / CONTRIBUTING and lint or test conventions that apply,
  plus conventions from sibling services or the parent workspace that the team expects here
- Allium specs: every `.allium` file in the repo, which of them the diff touches or implements, and any known `allium check` baseline the repo documents (or "none")
- Changed files: every file in the diff, including docs, fixtures, config, and rule files
```

Mark each item you noticed but have not resolved. Before finishing, every marked item either becomes a finding with a severity or gets an explicit "checked, fine".

Write the result down as the **context packet**: the intent, the surface list above, how to get the diff (repo path plus base and head refs), the deployment manifest's real numbers, and the repo rules you found. Every reviewer gets the same packet. A fact you leave out of it is a fact no reviewer has.

If the change has uncommitted edits, save them as a patch (`git diff HEAD > <scratch>/change.patch`) and put its path in the packet. The tests reviewer works in a separate worktree that starts from the last commit.

### Step 2: Dispatch the Reviewers in Parallel

Send all the Agent calls (six, or seven with the spec-alignment reviewer) in **one message**, so they run concurrently. Use a general-purpose subagent that can read files and run shell commands. A search-only agent can find code but won't review it.

| Reviewer | Applies these sections of this skill | Edits files? |
|---|---|---|
| Correctness | 1. Correctness, including Lifecycle and state | No |
| Readability | 2. Readability & Simplicity; Dead Code Hygiene (identify only, never delete) | No |
| Architecture | 3. Architecture; Structural Remedies; Change Sizing | No |
| Security | 4. Security | No |
| Performance | 5. Performance | No |
| Tests | Step 3: The Tests Brief | Yes, only in its own worktree |
| Spec alignment (only if the repo has Allium specs) | Spec Alignment (Allium), run through `allium:weed` in check mode | No |

If a `security-and-hardening` or `performance-optimization` skill is installed, add its path to that reviewer's prompt.

When the surface list includes a thread pool, executor, event loop, lock, connection pool, cache, or a dependency that can hang, add the absolute path of `../dev-async-boundary-test/references/hazard-catalog.md` to the Correctness reviewer's prompt. Resolve it from this file's location, because the reviewer has no other way to find it.

The tests reviewer edits source files to run its mutation experiments. Give it `isolation: "worktree"`, so no other reviewer reads a file while it is mutated. In its prompt, tell it to apply the patch from the packet if there is one, and to install dependencies first, because a fresh worktree has none. If worktree isolation isn't available, run the tests reviewer after the other five have returned, never alongside them.

**Spec-alignment reviewer.** Use the `allium:weed` agent type if it is listed, otherwise a general-purpose subagent told to invoke the `allium:weed` skill. Either way its prompt must say: "Mode: check. Do not edit specs or code. You are not inside the Allium loop, so return the sections below, not the typed JSON." Put weed's Spec / Code / Classification triple in each finding's Evidence line. The `allium:weed` agent has Edit and Write tools, so the no-edit rule has to come from the prompt. Give it the spec files from the packet and the diff. If the Allium plugin is not installed, do not improvise a comparison: put "spec alignment not run, plugin missing" under Unverified in the review.

While the reviewers run, don't review the axes yourself. Wait until all of them have reported. If one fails or returns a malformed report, send it a follow-up message or run it again. Don't fill in its axis from your own reading.

**Reviewer prompt.** Fill in the braces. Keep the rules and the return format word for word, because Step 4 depends on them.

```
You are the {axis} reviewer for one code change. The other reviewers cover the
other axes in parallel. Stay on your axis; if you come across something severe
outside it, report it under "Outside my axis".

Context packet:
{intent, ticket or MR link}
{repo path; diff command or patch path}
{surface list: outputs, shared objects, limits with real numbers, failure
 handlers, external dependencies and deploy order, repo rules, changed files}

Read {absolute path to this SKILL.md} and apply these sections in full:
{sections}. Answer every question in them against this change, file by file.
A question with nothing in this change to check it against goes under
"Not applicable", with the reason.

Rules:
- Do not edit, create, or delete files in the repo, commit, push, or post
  anything. Scratch files go in {scratch dir} only.
- Every claim cites file:line and what you read or ran. If a verdict rests on
  how a library behaves, read its installed source; if you didn't, put the
  item under Unverified.
- Write every finding and remedy in plain language as well as technical terms.
  Explain what can happen, who or what is affected, and the concrete change
  that would fix it. Define jargon or acronyms on first use, but preserve
  exact identifiers and file:line references.

Return exactly these sections:
## Findings
- {Critical|Required|Consider|Nit|FYI} {live|latent} path:line: the claim in plain language;
  in simple terms, why it matters and what can happen
  Evidence: ...  Failure scenario: ...  Remedy: ...
## Checked, fine
- item: evidence
## Unverified
- item: what would settle it
## Not applicable
## Outside my axis
## Files opened
## Files in the diff I did not open
```

For the tests reviewer, replace the first rule with: "Work only in your worktree. Apply {patch path} first if given, and install dependencies. Restore every mutated file from a copy before the next mutation." Also add this section to its return format: `## Mutations`, with one line per mutation saying KILLED (and by which test) or SURVIVED (and which test is missing).

**Small changes.** For a diff under about 50 changed lines in one or two files, six reviewers cost more than they find. Review all the axes yourself in one pass, still answering every section's questions, and still run the Tests Brief's mutation experiments. Say in the review that you used this exception. The exception does not drop spec alignment: if the repository has Allium specs and the diff touches code or specs they cover, run `allium:weed` in check mode yourself and apply the Spec Alignment section.

### Step 3: The Tests Brief (tests reviewer)

Tests reveal intent and coverage:

```
- Do tests exist for the change?
- Do they test behavior (not implementation details)?
- Are edge cases covered?
- Do tests have descriptive names?
- Would the tests catch a regression if the code changed?
```

Answer the last question by experiment, not by reading. Invert one condition the change adds (drop a negation, swap `&&` for `||`), run the suite, then restore the file from a copy. A mutation that stays green is a finding: name the test case that is missing. For a project-wide mutation score, see `constraint-driven-development`.

- Mutate error, rollback, and degraded branches specifically, not only the happy-path conditions.
- Mutate the declarative logic too (rules, templates, queries, config conditions), not only the host code. A guard in a rule file goes untested as easily as one in code.
- Does each test isolate the one condition its name claims, or could it pass for an unrelated reason?
- Do golden/snapshot fixtures pin both the full output and the degraded output?
- For each new lookup against external data (cache, table, remote call), is there an end-to-end test for each outcome: hit, miss, key that can't be built, source unavailable?
- If the repo has Allium specs: for each spec rule, invariant, or transition the change touches, `allium plan <spec>` lists the test obligations. Is each one covered by a test? Name the ones that are not.

Run the repo's lint, type check, and test commands the way CI runs them, and report the results. Then check the author's verification story:

```
- What tests were run?
- Did the build pass?
- Was the change tested manually?
- Are there screenshots for UI changes?
- Is there a before/after comparison?
```

### Step 4: Merge, Verify, and Categorize (orchestrator)

The user sees your review, not the reviewers' reports. Merge them into one:

1. **Deduplicate.** When several reviewers report the same root cause, keep one finding with the strongest evidence. Agreement across axes raises confidence, so note it.
2. **Resolve conflicts.** When one reviewer marks something fine and another flags it, read the code yourself, and the library source if that's what the question turns on. Decide, and record why.
3. **Verify every Critical and Required finding yourself.** Open the cited line and walk through the failure scenario. Drop or downgrade anything that doesn't hold up, and say so. Subagents sound confident and plausible even when they're wrong.
4. **Place the "Outside my axis" items** under the right axis, and verify them the same way.
5. **Check coverage.** Together, the reviewers' "Files opened" lists must cover every changed file. Open any file that no reviewer opened, or say in the review that nobody did.
6. **Carry the lists forward.** Each reviewer's "Checked, fine" and "Unverified" items go into the review, so nothing anyone reasoned about disappears.

Write the merged review for both the author and the person deciding whether to merge. Every finding must follow the Plain-Language Findings guidance: explain the issue and its practical impact before or alongside the technical detail, then give a concrete recommendation. Preserve the evidence, severity, and `live`/`latent` label; simpler wording must not weaken the claim.

Then label every finding with its severity so the author knows what's required vs optional:

| Prefix | Meaning | Author Action |
|--------|---------|---------------|
| *(no prefix)* | Required change | Must address before merge |
| **Critical:** | Blocks merge | Security vulnerability, data loss, broken functionality |
| **Nit:** | Minor, optional | Author may ignore — formatting, style preferences |
| **Optional:** / **Consider:** | Suggestion | Worth considering but not required |
| **FYI** | Informational only | No action needed — context for future reference |

This prevents authors from treating all feedback as mandatory and wasting time on optional suggestions.

**Lead with what matters.** Order findings by leverage: correctness and security first, then structural regressions and missed simplifications, then everything else. Don't bury a real issue under cosmetic nits — a few high-conviction comments beat a long list. If you have one structural problem and ten nits, the structural problem *is* the review.

**Check the write-up against your working notes and the reviewers' reports.** Everything you or a reviewer reasoned about must appear either as a finding or in a "checked, fine" list with its evidence. Items that get dropped between analysis and report are an easy gap to miss: a concern someone judged minor, or something sized in someone's head and never written down.

## Multi-Model Review Pattern

Use different models for different review perspectives:

```
Model A writes the code
    │
    ▼
Model B reviews for correctness and architecture
    │
    ▼
Model A addresses the feedback
    │
    ▼
Human makes the final call
```

This catches issues that a single model might miss — different models have different blind spots. The axis reviewers in Step 2 can run on a different model from the one that wrote the code, using the Agent tool's `model` parameter.

**Example prompt for a review agent:**
```
Review this code change for correctness, security, and adherence to
our project conventions. The spec says [X]. The change should [Y].
Flag any issues as Critical, Required, Optional, or Nit.
```

## Dead Code Hygiene

After any refactoring or implementation change, check for orphaned code:

1. Identify code that is now unreachable or unused
2. List it explicitly
3. **Ask before deleting:** "Should I remove these now-unused elements: [list]?"

Don't leave dead code lying around — it confuses future readers and agents. But don't silently delete things you're not sure about. When in doubt, ask.

```
DEAD CODE IDENTIFIED:
- formatLegacyDate() in src/utils/date.ts — replaced by formatDate()
- OldTaskCard component in src/components/ — replaced by TaskCard
- LEGACY_API_URL constant in src/config.ts — no remaining references
→ Safe to remove these?
```

## Review Speed

Slow reviews block entire teams. The cost of context-switching to review is less than the waiting cost imposed on others.

- **Respond within one business day** — this is the maximum, not the target
- **Ideal cadence:** Respond shortly after a review request arrives, unless deep in focused coding. A typical change should complete multiple review rounds in a single day
- **Prioritize fast individual responses** over quick final approval. Quick feedback reduces frustration even if multiple rounds are needed
- **Large changes:** Ask the author to split them rather than reviewing one massive changeset

## Handling Disagreements

When resolving review disputes, apply this hierarchy:

1. **Technical facts and data** override opinions and preferences
2. **Style guides** are the absolute authority on style matters
3. **Software design** must be evaluated on engineering principles, not personal preference
4. **Codebase consistency** is acceptable if it doesn't degrade overall health

**Don't accept "I'll clean it up later."** Experience shows deferred cleanup rarely happens. Require cleanup before submission unless it's a genuine emergency. If surrounding issues can't be addressed in this change, require filing a bug with self-assignment.

## Honesty in Review

When reviewing code — whether written by you, another agent, or a human:

- **Don't rubber-stamp.** "LGTM" without evidence of review helps no one.
- **Don't soften real issues.** "This might be a minor concern" when it's a bug that will hit production is dishonest.
- **Quantify problems when possible.** "This N+1 query will add ~50ms per item in the list" is better than "this could be slow."
- **Push back on approaches with clear problems.** Sycophancy is a failure mode in reviews. If the implementation has issues, say so directly and propose alternatives.
- **Accept override gracefully.** If the author has full context and disagrees, defer to their judgment. Comment on code, not people — reframe personal critiques to focus on the code itself.

## Dependency Discipline

Part of code review is dependency review:

**Before adding any dependency:**
1. Does the existing stack solve this? (Often it does.)
2. How large is the dependency? (Check bundle impact.)
3. Is it actively maintained? (Check last commit, open issues.)
4. Does it have known vulnerabilities? (`npm audit`)
5. What's the license? (Must be compatible with the project.)

**Rule:** Prefer standard library and existing utilities over new dependencies. Every dependency is a liability.

**Upgrading an existing dependency** is a code change like any other, and the riskiest upgrades are the ones merged in bulk with a message like "bump deps." Review them with the same discipline:

1. **Read the changelog, not just the version number.** Semver is a promise the maintainer may not have kept — a "patch" can carry a behavioral change. For a major bump, read the migration notes and find what breaks.
2. **One dependency per change.** Upgrade and merge them individually (or in small related groups). When a bulk bump breaks the build, you've lost which package did it; a single-package change makes the cause obvious and the revert clean.
3. **Let the tests decide.** The upgrade is verified by a green suite before *and* after, not by "it installed." If coverage around the dependency's behavior is thin, that gap is the real finding — add a test first.
4. **Mind the transitive graph.** Most installed packages are ones nobody chose directly. Review the lockfile diff, not just `package.json`; a single direct bump can pull in dozens of indirect changes.
5. **Keep the lockfile honest.** Commit it, review its diff, and never hand-edit it. The lockfile is the thing that actually pins what ships.

For triaging `npm audit` findings and supply-chain risk (typosquatting, compromised maintainers), follow the `security-and-hardening` skill — this section covers the upgrade *workflow*, that one covers the security verdict.

## The Review Checklist

```markdown
## Review: [PR/Change title]

### Context
- [ ] I understand what this change does and why
- [ ] Surface listed: outputs, shared objects, limits, failure handlers, external dependencies, repo rules, changed files
- [ ] Context packet written and given to every reviewer
- [ ] Six reviewers (seven if the repo has Allium specs) dispatched in one message, tests reviewer in its own worktree (or the small-change exception used and stated)
- [ ] Every changed file opened by at least one reviewer, including docs, fixtures, config, and rule files
- [ ] Every item I or a reviewer noticed or reasoned about is either a finding with a severity or listed as checked and fine, with evidence

### Correctness
- [ ] Change matches spec/task requirements
- [ ] Edge cases handled
- [ ] Error paths handled
- [ ] Tests cover the change adequately
- [ ] Overlapping lifecycle transitions (start/reload/stop/crash) are safe
- [ ] A dead background task doesn't leave others running on stale output
- [ ] "None → some", "some → none", and single-field config changes trigger the right side effects
- [ ] No shared object (client, consumer, iterator, cache) is used by two paths that each assume they are its only user; any "safe" verdict rests on documented behaviour or source I read
- [ ] A hung or slow dependency cannot stall unrelated work: each blocking call's pool is named, its timeout is the real value, and concurrent misses for one key make one call
- [ ] Locks are taken in one order, never held across a callback or `await`, and no pooled task waits on another task from the same pool
- [ ] Readiness and health signals are right in every phase (startup, reload, retry, shutdown), including when every replica is in that phase at once
- [ ] A multi-step update that fails partway leaves a consistent state, and the caller can tell
- [ ] Every parser or validator of the same syntax accepts the same grammar
- [ ] Every acquire path releases on every exception type
- [ ] Each new startup/reload failure lands in the handler that implements the documented degraded mode
- [ ] Time/retry budgets are scoped per independent item, or a shared budget's exhaustion fails loudly instead of skipping the remaining items
- [ ] Silent degradation is observable (log or metric)
- [ ] Third-party APIs checked against the pinned version's source

### Readability
- [ ] Names are clear and consistent
- [ ] Logic is straightforward
- [ ] No unnecessary complexity
- [ ] Docs describe what was built, not what was proposed

### Architecture
- [ ] Follows existing patterns
- [ ] No unnecessary coupling or dependencies
- [ ] Appropriate abstraction level
- [ ] Refactors reduce complexity rather than relocate it
- [ ] No feature logic in shared modules; file stays within a healthy size
- [ ] No hand-written code for what the library already provides
- [ ] Contract changes for downstream consumers are registered, versioned, and signed off
- [ ] Findings labeled live or latent
- [ ] Cross-repo dependencies and deploy order are identified; startup prerequisites exist in every environment
- [ ] New code follows the repo's own rules (CLAUDE.md / AGENTS.md / CONTRIBUTING) and any sibling or workspace conventions that apply

### Security
- [ ] No secrets in code
- [ ] Input validated at boundaries
- [ ] No injection vulnerabilities
- [ ] Auth checks in place
- [ ] External data sources treated as untrusted
- [ ] Personal data in new outputs is approved
- [ ] Config/schema models reject unknown keys (checked by loading a misspelled key)

### Performance
- [ ] No N+1 patterns
- [ ] No unbounded operations
- [ ] Pagination on list endpoints
- [ ] New in-memory state fits the deployment's resource limits (sized as record count × record size, not "bounded")

### Spec alignment (only if the repo has Allium specs)
- [ ] `allium:weed` run in check mode over the specs the change touches or implements
- [ ] Every changed behaviour is stated in the spec, and every edited spec is matched by the code
- [ ] Each divergence classified (code bug, spec bug, aspirational, intentional gap) and rated by whether the change introduced it
- [ ] `allium check` on edited specs shows no new warning or error against the base ref
- [ ] Test obligations from `allium plan` for the touched rules are covered

### Verification
- [ ] Every Critical and Required finding verified by the orchestrator against the code
- [ ] Reviewer conflicts resolved by reading the code, with the reason recorded
- [ ] Every finding explains the issue, practical impact, and recommendation in plain language without dropping technical evidence
- [ ] Mutating error, rollback, and degraded branches makes a test fail
- [ ] Declarative logic (rules, templates, queries) mutated, not only host code
- [ ] Each test isolates the condition its name claims
- [ ] Golden/snapshot fixtures pin both full and degraded output
- [ ] Each new lookup has end-to-end tests for hit, miss, unbuildable key, and source unavailable
- [ ] Tests pass
- [ ] Build succeeds
- [ ] Manual verification done (if applicable)

### Verdict
- [ ] **Approve** — Ready to merge
- [ ] **Request changes** — Issues must be addressed
```
## See Also

- For detailed security review guidance, see `../../references/security-checklist.md`
- For performance review checks, see `../../references/performance-checklist.md`
- For spec alignment in repos with Allium specs, see the `allium:weed` skill (and `allium:propagate` for generating tests from the spec)

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "It works, that's good enough" | Working code that's unreadable, insecure, or architecturally wrong creates debt that compounds. |
| "I wrote it, so I know it's correct" | Authors are blind to their own assumptions. Every change benefits from another set of eyes. |
| "We'll clean it up later" | Later never comes. The review is the quality gate — use it. Require cleanup before merge, not after. |
| "AI-generated code is probably fine" | AI code needs more scrutiny, not less. It's confident and plausible, even when wrong. |
| "The tests pass, so it's good" | Tests are necessary but not sufficient. They don't catch architecture problems, security issues, or readability concerns. |
| "The refactor makes it cleaner" | Relocating complexity isn't reducing it. If the reader still holds the same number of concepts, the structure didn't improve — look for the version where branches disappear. |
| "It's only a small addition to this file" | Small diffs still push files past a healthy size and bolt branches onto unrelated flows. Judge the resulting structure, not the diff size. |
| "It's just a version bump" | A bump is a behavior change you didn't write. Read the changelog; semver doesn't guarantee no breakage. |
| "I'll upgrade everything in one PR to save time" | A bulk bump that breaks the build hides which package did it. One dependency per change keeps the cause and the revert clean. |
| "Another reviewer said the library behaves like X" | Check the library source yourself before you change a severity in either direction. |
| "I noticed it but it's probably minor" | Report it with a severity label. A finding you drop is the same as one you missed. |
| "I reasoned it through, so the shared use is safe" | Reasoning about a library's internals isn't evidence. Read the source, or report the concern as unverified. |
| "The memory is bounded" | Bounded isn't a size. Multiply record count by record size and compare against the limit. |

## Red Flags

- PRs merged without any review
- Review that only checks if tests pass (ignoring other axes)
- "LGTM" without evidence of actual review
- Security-sensitive changes without security-focused review
- Large PRs that are "too big to review properly" (split them)
- No regression tests with bug fix PRs
- Review comments without severity labels — makes it unclear what's required vs optional
- Accepting "I'll fix it later" — it never happens
- A refactor that moves code around without reducing the number of concepts a reader must hold
- A change that grows an already-large file instead of decomposing it
- New conditionals scattered into unrelated code paths (a missing abstraction)
- A bespoke helper that duplicates an existing canonical one, or feature logic placed in a shared module
- A bulk "bump dependencies" PR with no changelog review and no per-package isolation
- A lockfile change that's hand-edited, uncommitted, or merged without reviewing its diff
- Findings about a third-party API made without checking the pinned version's source
- A behaviour change in a repo with Allium specs, with no spec change in the same change
- A spec edit that the code and tests do not follow

## Verification

After review is complete:

- [ ] All Critical issues are resolved
- [ ] All Required (no-prefix) changes are resolved or explicitly deferred with justification
- [ ] Tests pass
- [ ] Build succeeds
- [ ] The verification story is documented (what changed, how it was verified)
- [ ] Dependency upgrades were reviewed against their changelog, isolated per package, and verified by a green suite with the lockfile diff reviewed

**Presumptive blockers:** surface and propose the simpler design for each of these; escalate to Required only when the change actively makes structure worse: a refactor that relocates complexity instead of reducing it; a change that pushes a file past the size boundary with no decomposition; feature logic added to a shared module; a near-duplicate of an existing canonical helper; a silent fallback that hides an unclear invariant.
