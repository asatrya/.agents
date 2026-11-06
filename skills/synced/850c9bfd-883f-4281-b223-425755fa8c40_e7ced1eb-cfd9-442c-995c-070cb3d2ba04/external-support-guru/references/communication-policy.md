# Customer communication

Support's own rules for customer communication. The drafts this skill produces must fit them.

## Over-communication is the default

> "It's better to reach out and provide an update — even if you're unsure — than to remain silent."

A blocked investigation still owes the customer a reply. When you cannot answer yet, say so in the chat report so the support engineer can tell the customer what is known, what is being checked, and what is needed from them.

## Update cadence by ticket status

| Status | Expected |
|---|---|
| New | Daily. Immediate during an active back-and-forth, in business hours. |
| Waiting for support | At least daily. Treat with the same urgency as New. |
| With Engineering | Immediate if the linked ticket needs Support to respond. Chase engineering after a few days of no progress, respecting their SLA first. |
| Waiting for customer | Update as soon as they reply; follow up weekly if they go quiet. |
| Escalated | At least daily, hourly if the customer asks. Meaningful updates, not noise. |
| Resolved | Confirm with the customer that it works before resolving. Leave open long enough for follow-ups. |
| Closed | Cannot be reopened. Only when nothing further is required. |

A customer asking for an update gets an answer as soon as possible, even when there is no news: status, plus when to expect more.

## Response times by severity

Contractual, and tighter than the cadence by status when the two differ.

| Severity | Initial | Follow-up |
|---|---|---|
| S1 | 30 minutes | every 4 hours |
| S2 | 4 hours | every 12 hours |
| S3 | 12 hours | every 2 business days |
| S4 | 24 hours | every 5 business days |

## Splitting a case

If triage uncovers a second, different problem, Support opens the new case — never the customer. The person who opens it owns it and does not return it to the queue. Flag this when your triage finds two problems in one ticket; recommend the split rather than quietly triaging both.

## Closing

Only when fully resolved. Two documented exceptions:

- **Customer unresponsive** — get an alternative contact from the OSM first, and if nobody responds for a week and they are not on leave, close it, telling the manager. Never recommend closing for silence without the OSM step.
- Fix is far off or unscheduled — resolve and explain, involving the Omnichannel Success Manager, rather than leaving the ticket open indefinitely. Only once an immediate fix or workaround is in place.

A ticket closed for inactivity with no investigation on it counts as a prior occurrence; say it was never diagnosed.

## Customer reply

Written only when the support engineer asks. Most customers need a plain explanation and the state of their ticket, not the investigation. Five sentences at most:

1. Answer any open question the customer asked.
2. What was found, in the customer's terms. No evidence narrative, no service names, no code, no internal ticket keys, no root cause speculation. Confirmed and still-being-checked stay distinct.
3. What happens next and who does it. No timelines, no promises about engineering work. If the request cannot be granted, say what will happen instead.

When the platform behaves as designed but differently from what the retailer expected, explain the designed behaviour and link the public documentation that describes it.

Write it to `customer-reply.txt`, plain text, nothing else in the file.

## What this skill may and may not write

- Never a customer-visible comment. No confirmation unlocks this and there is no exception.
- The internal note carries the severity assessment (one criterion per line, ➖ / ➕ / ❗ / ➿) and the documentation
  review with its verdict, for Support's own record. On a ticket answered without an investigation it carries the
  answer or the action taken instead. It may also carry a suggested customer reply.
  Label it AI-generated and unreviewed.
  A support engineer who wants it sent copies it into a public comment by hand.
- Feature requests go to the product feedback form. See references/forward-product-feedback.md.
- No timelines, no promises about engineering work, no internal detail.
