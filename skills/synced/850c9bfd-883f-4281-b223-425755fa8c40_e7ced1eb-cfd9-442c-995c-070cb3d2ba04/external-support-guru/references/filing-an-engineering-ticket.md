# Filing the engineering ticket

Status: enabled for engineering tickets (A) and for the NCS internal comment (B).

Support leadership approved filing on 2026-09-21. What that permits: create a Support Request on an engineering project, post evidence comments, link it to the NCS ticket — each after an explicit per-ticket confirmation from the support engineer.

Writing to NCS is limited to one internal comment, after explicit per-ticket confirmation. Post it through Chrome against the Service Desk API — never with `addCommentToJiraIssue`, whose `commentVisibility` leaves the comment `jsdPublic: true` and visible to the retailer:

```
POST /rest/servicedeskapi/request/<KEY>/comment   { "body": "<plain text>", "public": false }
GET  /rest/servicedeskapi/request/<KEY>/comment?public=true&internal=true   → values[].public
```

`body` is a plain string, not ADF, so `format-jira-comment` output does not go here. Always run the GET afterwards and confirm `public: false`. If it is true or missing, tell the support engineer the comment is customer-visible. Demonstrated on NCS-9789; see `docs/adr/003-filing-engineering-tickets.md`.

Everything below was verified against live Jira on 2026-09-21: create-screen metadata, recent Support-filed tickets, and changelogs. Where a decision rests on inference rather than a changelog, it says so.

# Fields

The receiving team's page in the event catalog (`teams/team-<slug>.mdx` in `newstore/engineering/hq/tools/event-catalog`, read through the GitLab MCP) carries a `supportHandover` block: project, issue type, whether Business Impact is set at create, labels, parent, and the status a new ticket lands in. `docs/support-handover.mdx` in the same repository lists the fields Support never sets and the Business Impact option ids. Read both before building the payload. The hook enforces the same rules.

# Payload

```jsonc
// 1. create
{
  "projectKey": "FO",
  "issueTypeName": "Support Request",
  "summary": "[marine-layer] Payment stuck in Authorized after in-store purchase; Adyen shows it settled",
  "description": "<investigation/redacted/engineering-handover.md, minus the filing preamble>",
  "additional_fields": {
    "customfield_14665": { "id": "<Business Impact option id, from the catalog page>" },
    "labels": ["payments"]
  }
}

// 2. one evidence comment per source or finding (see _Comments_ in the skill)
// 3. link, from the NCS side, as a separate call
{ "inwardIssueKey": "<new key>", "outwardIssueKey": "NCS-9718", "linkTypeName": "Contains" }
```

Summary: the handover title, as @handover-template.md says.

**Link type**: `Contains` (`10400`) by default. Do not treat a differing existing link as an error.

Linking switches on the automation that copies internal NCS comments to the engineering board and syncs status back. Say so when you ask.

# Every posted artifact labels itself

The description and each comment open with:

```
🤖 AI-generated · external-support-guru <version> · <date> · from NCS-<n>
Reviewed and filed by <display name from atlassianUserInfo>. Findings are observations, not a diagnosis.
```

Use emoji as section markers in the description body only — 🔎 Investigation in short · 🔎 What happens · 🧪 How to reproduce · 📊 Scope · 🩺 Support triage · 📎 Evidence ledger · ❓ Open questions · 🧩 Observations. They are signposts for someone scanning a long ticket, not decoration, and never a substitute for a clear heading.

Never put an emoji in a field value. Jira shows emoji in some option names and statuses, but those are stored values with exact spellings; a decorated copy will be rejected or silently create the wrong thing. The issue type is the trap — see the top of this file.

# Before you file

Redact first. Where scripts run, `python3 scripts/redact-investigation-files.py <ticket dir>` writes `investigation/redacted/` and exits non-zero if anything survived: post nothing unless it exits 0. Where they do not (Claude Desktop), write the redacted copies under `investigation/redacted/` yourself, applying every pattern in `scripts/pii-patterns.json`, then re-read each copy for anything that survived. Post nothing until that read finds nothing.

Evidence comments are written from the redacted files, never pasted from them.

Never ships to engineering: `customer-reply.txt` (correspondence), `investigation/TODO.md`, `investigation/skill-notes.md` (working notes), `investigation/access-log.md` (who signed in where).

Screenshots are attached, not described. The Atlassian MCP has no upload tool, which is not
the same thing as there being no way to attach a file. Open the ticket in Chrome and use
`file_upload` against the page's file input:

1. `navigate` to `https://goodscloud.atlassian.net/browse/<KEY>`.
2. The input is `input[type=file]`, present but hidden, so `find` will not return it. Give it an
   `aria-label` with `javascript_tool`, then `find` that label to get a ref.
3. `file_upload` with the ref and the absolute paths. It takes several files in one call.
4. Verify through the API, not the page — `getJiraIssue` with `fields: ["attachment"]`. The
   issue view does not always render a new attachment without a reload, so the screen is not
   evidence either way.

If the upload fails, say so to the support engineer in chat and leave the ticket alone. See
_Comments_ in the skill.

# Confirm, then act

Show project, issue type, summary, Business Impact, labels, the comment list, the redaction summary, the link and its automation consequence, and the screenshots to be uploaded. Then wait for an explicit yes.

One yes authorises one create, its comments and its link. It never carries to the next ticket.

# Refuse when

- The redactor did not exit 0
- The routing call is uncertain — ask another support engineer first, that is the documented answer
- The evidence ledger has an unexplained "not checked" that would change the severity
- The triage outcome is works-as-designed
- The body contains a proposed fix or a code-level diagnosis
- The AI-generated header is missing from anything about to be posted
- Anything would be written to NCS that is not an explicitly confirmed internal comment

# If create fails

Report the error verbatim and stop. Do not retry with fields removed until it succeeds — that produces a ticket missing the thing the team needs. A rejected field means the profile above is wrong for that project, which is a finding worth reporting rather than working around.
