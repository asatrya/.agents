---
name: newstore-git
description: >-
  Newstore/TIDE Git and GitLab–Jira hygiene: branches, commits, merge requests, and
  attaching MR URLs as Jira web links (including the parent ticket when the issue is
  a sub-task). Use for TDP-/NCS-, gitlab.com/newstore, or tasks mentioning merge
  request, web link, or remote link on a Jira ticket. Enforces keyword(TICKET-ID)
  commit and MR subjects. Before git push, reads CI pipeline config and runs
  local lint/test (or make check) matching MR pipelines. Opening any MR is not
  finished until its Jira web link is attached automatically, with no extra
  request or confirmation from the user. Not for personal or unrelated Git work.
---

# Newstore Git

Use this skill in the Newstore context whenever the workflow touches Git/GitLab naming **or** Jira **web links** for MRs. It defines **required** naming for commits and MRs and **required** Jira remote-link steps.

**Invoke it first.** Load this skill with the Skill tool before the first commit, push, branch or MR of the task, even when the user only says "commit", "push" or "open MR". Do not work from memory of it.

## Opening an MR: the full sequence

"Open an MR" (or "commit, push and open MR") always means all of these steps, in order. The user does not have to list them, and none of them is an optional follow-up:

1. Commit with a valid subject (see Naming rules).
2. Run the pre-push checks and fix failures (see Pre-push checks).
3. Push.
4. Create the MR with a valid title, by any means (GitLab MCP, `glab`, the URL `git push` prints).
5. **Attach the MR to the Jira ticket as a web link, automatically (see MR link on the ticket). Do this immediately after step 4, in the same turn, without asking.** Also do it for the parent when the ticket is a subtask.
6. Report the MR URL and the Jira link result (added, already present, or failed) in the final message.

The task is **not done** while step 5 is missing. Never end with "say so if you want the Jira link" or any other offer to do it later: the user's request to open the MR already authorizes it. The same applies to any MR on a `TDP-`/`NCS-`/... ticket that this task pushes to or touches and that is found without its link.

**Precedence:** For commit and MR **subjects**, this skill overrides generic instructions to “match `git log`” or “follow repository style” when those would produce a different format (for example `TDP-3449 Add something` without a conventional keyword).

## When to apply

Read this skill **before** you:

- Create a commit (including when the user only says “commit”)
- Create or title an MR
- Create a branch (unless only pushing existing valid names)
- Run **`git push`** (or push as part of commit/MR workflow)
- Attach, list, or sync **GitLab MR URLs** on a Jira ticket (web links / remote links), with or without a new commit

Derive `TICKET-ID` from the branch name, user message, or active ticket. Do not invent one. If the keyword or ticket cannot be determined without guessing, ask the user before committing or opening an MR.

## Naming rules

### Branches

- Pattern: `TICKET-ID-short-description`
- `short-description`: lowercase, hyphen-separated, concise

### Commits and MRs (subject line)

- Pattern: `keyword(TICKET-ID): short description`
- `keyword` must be one of: `feat`, `fix`, `chore`, `test`, `refactor`, `docs`
- Text after the colon: concise, sentence-style (lowercase start is fine)

| Keyword   | Use when |
|-----------|----------|
| `feat`    | New behavior or capability |
| `fix`     | Bug fix or incorrect behavior |
| `chore`   | Tooling, config, deps, no product behavior change |
| `test`    | Tests only (or test-focused change) |
| `refactor`| Structure change without intended behavior change |
| `docs`    | Documentation only |

### Forbidden commit/MR subjects

Do **not** use:

- `TICKET-ID: description` or `TICKET-ID description` (ticket prefix without keyword)
- Subjects that omit `(TICKET-ID)` when a ticket applies
- Copying recent branch commits if they violate the pattern above

### Validation

Before `git commit`, confirm the subject matches:

```text
^(feat|fix|chore|test|refactor|docs)\([A-Z]+-\d+\): .+
```

Examples:

```text
Branch: TDP-4090-load-test-new-event-stream
Commit: feat(TDP-4090): add load test for new event stream
MR: feat(TDP-4090): add load test for new event stream
Commit: refactor(TDP-3449): extract sales order jsonata library
Commit: test(TDP-3449): cover sales order library helpers
```

For a **push** only: keep existing branch and commit names as-is. Apply these rules to any **new** branch, commit, or MR created in that workflow.

`git log` may still inform **body** text or scope of the change; it must **not** override the subject-line format in this skill.

## Pre-push checks

Before **`git push`**, run the repository’s local quality gate and fix failures (or report them) before pushing. Goal: catch the same failures CI would catch on the MR pipeline.

### 1. Read the CI pipeline definition

From the **repository root** (the tree you are pushing from), inspect how merge-request pipelines are defined. Typical locations:

- **GitLab** (most Newstore repos): `.gitlab-ci.yml`, included templates under `.gitlab/`, and any `extends` / `rules` that apply to MR pipelines
- **GitHub Actions**: `.github/workflows/*.yml`
- **Other**: `Jenkinsfile`, `circleci/config.yml`, etc.

Identify jobs or stages that run on MRs (lint, format, typecheck, unit tests, integration tests, build, security scan). Note the **exact commands** or scripts each job runs (for example `make lint`, `npm run test:ci`, `poetry run pytest`).

For GitLab projects on `gitlab.com/newstore`, use local files first; use GitLab MCP to read pipeline config from the remote only when the branch you are pushing does not yet contain the relevant CI changes.

### 2. Run checks locally

Execute everything from step 1 that can run on the developer machine without cloud-only resources (no deploy, no shared integration environments unless the user already has them configured).

**Preferred shortcut:** if the root `Makefile` defines **`check`** and it matches (or is documented as matching) the MR pipeline gate, run **`make check`** and wait for it to finish.

Otherwise, in order:

1. Run the same commands (or documented wrappers) as the MR pipeline jobs—especially **lint**, **format**, **typecheck**, and **test** jobs.
2. If CI uses a composite script (for example `scripts/ci.sh`), run that script when it is intended for local use.
3. Fall back to README or `make` targets named as the pre-merge gate (`make test`, `make lint`, and similar).

Skip or call out jobs that cannot run locally (Docker-only integration suites without local docs, cloud credentials, paid runners). List what you skipped and what still only runs in CI.

### 3. Push policy

- Do **not** push while local checks are failing unless the user explicitly asks to push anyway (for example a WIP branch).
- If CI is ambiguous or local reproduction is unclear, say what you read in the pipeline definition and ask which gate to run before pushing.

This applies to every push, including push-only workflows and pushes that follow a new commit or MR.

## MR link on the ticket

**Required and automatic.** The moment an MR exists, attach its URL to the Jira ticket as a **web link** (remote link), in the same turn, without asking and without waiting to be told. Opening the MR is what authorizes it. That is the Links / Web links panel, not a comment and not a Jira-to-Jira issue link. This holds for every MR, including one in a different repository than the code you were editing (for example a data-contract MR opened for a data-mapper ticket): the ticket key from the branch name decides where the link goes.

The Atlassian tools may be deferred. Load them in a single ToolSearch call before step 1 (`getAccessibleAtlassianResources`, `getJiraIssueRemoteIssueLinks`, `getJiraIssue`, `addGraphContext`), then get the `cloudId` from `getAccessibleAtlassianResources`.

1. Call `getJiraIssueRemoteIssueLinks` (with the `cloudId` and the ticket key; `getJiraIssue` evidence also works) on the ticket. Skip the add if the same MR URL is already present.
2. Create the web link with Atlassian MCP `addGraphContext` (pass the `cloudId` at the top level):
   - `relationshipType`: `jira-work-item-links-jira-work-item-remote-link`
   - `objectIdentifier`: the ticket key (e.g. `TDP-4090`)
   - `targetObjectIdentifier`: the GitLab MR URL
   - `title`: `MR !<iid> - <MR title>` (do not paste the raw URL as the title). Example: `MR !28 - fix(TDP-4090): keep two event-receiver replicas via autoscaler`
3. If the ticket is a subtask, get its parent and repeat steps 1–2 on the parent. Do not guess the ticket ID or parent.
4. Say what happened in the final message: link added (ticket, and parent if any), already present, or failed.

Do **not** substitute:

- `addCommentToJiraIssue` — a comment is not a web link
- `createIssueLink` — that only links two Jira issues

If `addGraphContext` fails, say so after creating the MR. Do not fall back to a comment.

### Do not ask, do not defer

- Never ask "do you want the Jira link?" and never mention it as an offer. It is part of the work, like the push.
- Never skip it because the user's words were only "commit, push and open MR". That wording includes it.
- Never leave an MR unlinked at the end of a turn. If you notice an MR from this task without a link (for example one you opened earlier, or one a push updated), add it then.
- The Jira web link is a pre-authorized write for this workflow. It does not conflict with the general rule not to write to other systems without being asked.
