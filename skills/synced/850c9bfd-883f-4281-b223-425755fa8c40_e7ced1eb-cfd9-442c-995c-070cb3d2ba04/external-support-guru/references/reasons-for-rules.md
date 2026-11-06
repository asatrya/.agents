# Reasons for rules

Sources behind the standards in this directory, for humans. The skill does not read this file.

- Customer communication (`communication-policy.md`): Support's [START HERE: Best Practices for Customer Communication and Case Management](https://goodscloud.atlassian.net/wiki/spaces/TS/pages/655163629/START+HERE+Best+Practices+for+Customer+Communication+and+Case+Management).
- How the engineering ticket is filed (`handover-template.md`, `filing-an-engineering-ticket.md`): Support's [How to request help from Engineering?](https://goodscloud.atlassian.net/wiki/spaces/TS/pages/5048270890/How+to+request+help+from+Engineering), refined against the six projects' create screens and 180 days of their tickets on 2026-09-21.
- Writing (`writing-standards.md`): the house rule on merge-request descriptions applied to tickets, which have the same reader and the same impatience. A ruled-out item names where Support looked because a bare "checked, fine" gives engineering nothing to decide with, and whether they re-check is their call.
- Rating Business Impact (`rating-business-impact.md`): the S1–S4 criteria and response times are the [SLA and Support Terms v25.10](https://drive.google.com/file/d/1TK62gR_qNfzh7KEdRmAoLDWr5N86EGm3/view), applied to every tenant regardless of contract date. The "looks like" examples come from THQ's [Proposal for Support Triage Rubric](https://docs.google.com/spreadsheets/d/1OXo_ES99VOpvg9UMhZ_mUMd8x1D5uUV7_MKWEViJeQg/edit), whose launch-blocker override and multi-retailer modifier were not adopted because they conflict with the contract wording: workaround is part of the S1 and S2 definitions, and severity is per retailer. Support has the last word on the rating because the support engineer holds context the classifier does not model, such as an upcoming renewal, escalation history or how frustrated the retailer is; the rubric is a suggestion. The response times by severity live in `communication-policy.md` with the cadence by status, so the rating standard does not repeat them. Non-production tenants are supported, and a blocked launch is potential GMV rather than current, which is why GMV only counts when the ticket names the launch. Decided 2026-10-29.
- Choosing the receiving team (`engineering-teams.md`): Support's [Which team in engineering do I need?](https://goodscloud.atlassian.net/wiki/spaces/TS/pages/3448766540/Which+team+in+engineering+do+I+need), now maintained in the event catalog's `docs/support-handover.mdx`.

## Skill rules without their reasons (`SKILL.md`)

- Find a control: a single failing case always contains things that look wrong, because there is nothing to compare them against.
- Code and components: a diagnosed guess gets the ticket dismissed, or argued with instead of read.
- Evidence ledger: a ledger that lists only what was checked is misleading; a confident triage with three sources unchecked is worse than none.
- Comments after filing: the urge to comment is strongest when there is nothing to deliver, and a comment explaining an absence costs the reader time to discover it contains nothing they can use.

## Permission tiers (`permissions.md`)

- Atlassian `createJiraIssue` (ask every time): Filing (A): one engineering ticket per confirmed triage
- Atlassian `createIssueLink` (ask every time): Filing (A): NCS 'contains' link
- Sentry `analyze_issue_with_seer` (ask every time): Starts a paid Seer analysis run
- Sentry `execute_sentry_tool` (ask every time): Generic dispatcher; can reach write tools
- Amplitude `run_amp` (ask every time): Runs an agent; may create content
- Amplitude `use_amp_*` (ask every time): Mixed read/write per call (dashboards, notebooks, flags, experiments, cohorts…)
- Atlassian `addCommentToJiraIssue` (block): Posts jsdPublic: true — visible to the retailer. Internal notes go through Chrome (filing-an-engineering-ticket.md)
- Atlassian `editJiraIssue` (block): Hard rule: never edit a ticket
- Atlassian `transitionJiraIssue` (block): Hard rule: never transition a ticket
- Atlassian `addWorklogToJiraIssue` (block): Not Support triage
- Atlassian `createConfluencePage` (block): Not Support triage
- Atlassian `updateConfluencePage` (block): Not Support triage
- Atlassian `createConfluenceFooterComment` (block): Not Support triage
- Atlassian `createConfluenceInlineComment` (block): Not Support triage
- Atlassian `createCompassComponent` (block): Not Support triage
- Atlassian `createCompassComponentRelationship` (block): Not Support triage
- Atlassian `createCompassCustomFieldDefinition` (block): Not Support triage
- Atlassian `addTeamworkGraphContext` (block): Not Support triage
- Sentry `update_issue` (block): Changes issue state in Sentry
- Amplitude `create_properties` (block): Writes taxonomy
- Amplitude `update_properties` (block): Writes taxonomy
- Amplitude `delete_event_properties` (block): Deletes taxonomy
- Amplitude `delete_user_properties` (block): Deletes taxonomy
- Amplitude `restore_event_properties` (block): Writes taxonomy
- Amplitude `restore_user_properties` (block): Writes taxonomy
- Amplitude `create_group_types` (block): Writes taxonomy
- Amplitude `manage_amp_entities` (block): Writes charts/dashboards
- Amplitude `manage_amp_events` (block): Writes taxonomy
- Amplitude `manage_amp_taxonomy` (block): Writes taxonomy
- Amplitude `share_amp_entities` (block): Changes sharing
- Claude in Chrome `form_input` (ask every time): Fills forms — NOM is read-only; only the confirmed internal-note flow needs it
- Claude in Chrome `file_upload` (ask every time): Only the confirmed screenshot-attach flow
- Claude in Chrome `upload_image` (ask every time): Only the confirmed screenshot-attach flow

## Link type (`filing-an-engineering-ticket.md`)

`Contains` is on every Support-filed THQ and CHEX ticket sampled on 2026-09-21 and is what Support's process page says; four FO and TDP examples used three different types, so it is a convention, not a rule.

## Inactivity closures count as occurrences (`communication-policy.md`)

NCS history contains tickets closed for inactivity with no investigation on them at all. That is within the letter of the closure rule and against its point: it makes a recurring problem look rare.

## ProductBoard (`forward-product-feedback.md`)

ProductBoard was deprecated on 2026-07-03 and access revoked; anything entered there is neither seen nor actioned. Product requests go to the Monday form, which the Success Team validates. The customer-facing roadmap is docs.newstore.com/docs/product-roadmap.

## An empty result is not an absence (`SKILL.md`)

A query that returns nothing has three explanations: the thing is absent, the signal never carried it, or the query never reached it. Dash0 shows all three — `otel.log.severity_text` is empty on Go-service errors, so a severity filter returns nothing on errors that are present (NCS-10114).

## Prior analysis is a lead, never a finding (`SKILL.md`)

The pre-triage poller posts its own internal notes, so the next pass over the same ticket reads this skill's earlier output back as if it were ticket evidence.

## The durable copy and its sidecars (`SKILL.md`, `investigation-record.md`)

Two things the record alone cannot do. A query plus a window stops being reproducible once Dash0's 30-day retention rolls past it, so a record that stores only the query describes evidence that no longer exists. And scoring a triage against what engineering eventually found needs both halves kept; without saved cases there is no corpus to score at all.

One sidecar per assertion rather than per query because the assertion is the unit an eval scores. Cleaning happens as the rows are written because `redact-investigation-files.py` cannot gate anything in Claude Desktop, where nothing checks an exit code — an allowlist applied at capture is the only version that runs, and a file saved unclean stays unclean.

The Drive connector cannot update a file's content, which is why the record carries a timestamp and the newest wins, and why the index points at sidecars by filename: every save mints a new id, so an id written into the record goes stale on the next one.

Drive is allowed for the case folder and for nothing else, and only on the Support shared drive. A record describes a retailer's orders, tenants and store operators even after redaction, so it belongs somewhere the team owns and can audit, not in the personal Drive of whoever happened to run the triage. Decided 2026-11-03.

The second half, storing the engineering ticket's eventual resolution, is deliberately not here. Jira cannot supply it: sampled on 2026-11-02, every closed ticket behind a Support triage resolves as `Done`, the confirmed defect indistinguishable from the works-as-designed. The verdict has to be read off the closed ticket, so it waits for a corpus worth reading.

## Claims carry their claimant (`SKILL.md`)

The retailer writes the description and Support writes the comments, so the mix of voices sits inside the comment thread. A carrier's or payment provider's statement reaches the ticket second-hand, and reconciling it against telemetry is often where the finding comes from.

## Ruling out carries a prediction (`handover-template.md`)

Ruling a cause out closes that door for everyone who reads the ticket afterwards, so it needs more evidence behind it than finding a cause does. A result read without a prediction can be made to fit either way. Naming the record, count or state the suspicion would have produced, before the result is read, is what makes an empty result mean anything — the same reason an empty result is not an absence, applied to the handover.

## The count is measured, never asked (`SKILL.md`)

A reporter asked whether other records are affected will usually agree, and agreement is not evidence. They see their own orders; the count across the tenant is a query Support can run. Their number stays a claim with them as its claimant.

## Two numbers only make a proportion (`SKILL.md`)

A count of failures and a count of orders look like a rate side by side, and engineering prioritises on the rate. If the two cover different populations or different windows, the rate is invented, and it is invented in the direction that makes the ticket look urgent.

## A failed call is a failed query until proved otherwise (`SKILL.md`)

A source recorded as tried-and-failed is a source nobody checks again, and the conclusion is discounted for an absence that may not exist. A connector reachable at probe time and failing an hour later has usually been handed a query it cannot answer. The known-good call separates the two, and it has to run in the same minute to mean anything.

## State what happened, not what did not (`writing-standards.md`)

"The capture call was not dropped" leaves the reader holding the suspicion it was meant to clear, and it reads as an answer to an accusation nobody made. What happened carries the same information with nothing left hanging. Ruled out is the exception, because there the absence is the finding and the reader came for it.

## NewStore's commitments carry a status (`SKILL.md`)

An NCS thread accumulates promises — someone will look, someone will come back with a date — and the retailer remembers every one. A promise that was overtaken by what the investigation found is not broken, but it has to be marked `superseded`, or the next reader re-commits to it. A status update is not a commitment, or every ping becomes a debt.

## Tried-and-failed says whether it mattered (`investigation-record.md`)

Not-checked already records whether a source is worth checking. Tried-and-failed needs the same judgment more, because the receiving engineer usually can reach what Support could not, and needs to know which of those sources would change the answer.

## The ask gate and its two new decision values (`SKILL.md`, `triage-decision-guide.md`)

Most of what reaches NCS is not a defect report. Access requests, "link this customer to the
order", "what is the GraphQL SLA", "can the app receive a whole delivery in one scan" — each one
used to start a full triage: seven connector probes, a control, an evidence ledger, all spent on
a question answerable in a sentence. The trigger pays per ticket, so the gate sits before the
probe rather than after it; the probe is the first call that costs anything.

The gate needed vocabulary the five outcomes did not have, because every one of them means "this
was a defect report, and here is the ruling". `service-request` is the Support team's and Jira
Service Management's own word, not an invented one. `product-request` is a separate value
because it has a different destination and because it is the only non-defect ending reachable
from both gates: obvious at the door for a feature nobody ever built, or visible only after the
documentation turns out never to have promised it. Without it, a missing feature had to be
recorded as `works-as-designed`, and the corpus could not tell a retailer who misread the product
from one who wanted something it never offered.

`evidence.checked` and `classification.severity` are exempted for these two in
`validate-record.py`. Those rules exist because an investigation that checked nothing is not a
triage and a severity must be defensible from its assessment; a ticket that never needed an
investigation is the one case where neither applies. The exemption keys off an empty ledger
rather than the decision alone, because `product-request` also arrives after a full
investigation. Decided 2026-11-03.
