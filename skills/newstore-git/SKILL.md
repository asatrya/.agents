---
name: newstore-git
description: >-
  Newstore/TIDE Git and GitLab–Jira hygiene: branches, commits, merge requests, and
  attaching MR URLs as Jira web links (including the parent ticket when the issue is
  a sub-task). Use for TDP-/NCS-, gitlab.com/newstore, or tasks mentioning merge
  request, web link, or remote link on a Jira ticket. Enforces keyword(TICKET-ID)
  commit and MR subjects. Before git push, reads CI pipeline config and runs
  local lint/test (or make check) matching MR pipelines. Not for personal or
  unrelated Git work.
---

# Newstore Git

Use this skill in the Newstore context whenever the workflow touches Git/GitLab naming **or** Jira **web links** for MRs. It defines **required** naming for commits and MRs and **required** Jira remote-link steps.

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

After the MR exists, attach its URL to the Jira ticket as a **web link** (remote link). That is the Links / Web links panel, not a comment and not a Jira-to-Jira issue link.

1. Call `listJiraIssueRemoteIssueLinks` (or `getJiraIssue` evidence) on the ticket. Skip if the same MR URL is already present.
2. Create the web link with Atlassian MCP `addGraphContext`:
   - `relationshipType`: `jira-work-item-links-jira-work-item-remote-link`
   - `objectIdentifier`: the ticket key (e.g. `TDP-4090`)
   - `targetObjectIdentifier`: the GitLab MR URL
   - `title`: `MR !<iid> - <MR title>` (do not paste the raw URL as the title). Example: `MR !28 - fix(TDP-4090): keep two event-receiver replicas via autoscaler`
3. If the ticket is a subtask, get its parent and repeat steps 1–2 on the parent. Do not guess the ticket ID or parent.

Do **not** substitute:

- `addCommentToJiraIssue` — a comment is not a web link
- `createIssueLink` — that only links two Jira issues

If `addGraphContext` fails, say so after creating the MR. Do not fall back to a comment.
