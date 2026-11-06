# Engineering handover

A draft ticket for the receiving team, written so an engineer who has never seen this can start without asking Support anything. Written only once the handover gate in @triage-decision-guide.md is passed. Fill every section; where you have nothing, write what you tried and why it failed rather than deleting the section.

Filed as @filing-an-engineering-ticket.md says; the draft must fit its fields.

```md
# <Team project key>: [<tenant>] <the problem, as the retailer experiences it, in one line>

Source: NCS-<n> · Tenant: <tenant> · Environment: production · Reported: <date>
Business Impact: <S1-S4 and a short phrase, e.g. "S2. Orders cannot ship from 3 of 41 stores; no workaround.">
Action required: <one short sentence, the retailer's demand only — e.g. "match the (claimed) settled payment in Adyen with NewStore". Anything else engineering should look into goes under Open questions>

## 🔎 Investigation in short
- <five or six bullets that carry the whole finding: what the platform did, where it broke, what is confirmed, what is still open>
- <the Support-closable outcomes ruled out — works as designed, user error, missing feature, tenant configuration, data Support can fix — and the evidence that ruled each out>

## 🔎 What happens
<Observed behaviour in two or three sentences. What the platform did, not what the customer wants.>

Expected: <what should happen, and what says so — documentation, the UI, prior behaviour>
Actual: <what happens>

## 🧪 How to reproduce
Tenant: <dodici if it reproduces there, otherwise the retailer's tenant>
Preconditions: <configuration, feature flags, payment provider, store, order type — everything that had to be true>

1. <step>
2. <step>
3. <step>

Result: <what you saw>
Reproduced: <yes, on which tenant / no, and why not>

Known affected record: <ID and NOM link>

## 📊 Scope
- Affected records: <count, over what period, how identified>
- Affected tenants: <count and names>
- Prior NCS tickets with the same symptom: <keys, dates, how they were resolved — same symptom, not necessarily same cause>
- First seen: <date, and what changed then if known>
- Error signal: <Dash0 or Sentry counts and timeframe, or "not measured: <reason>">

## 🩺 Support triage
Assessment: <works as designed | documentation gap | tenant configuration | data issue | platform problem>
Confidence: <confirmed | plausible | needs-evidence>
Reasoning: <two or three sentences>

Ruled out — where we looked, what would have shown it, and what we saw. One line per row; only suspicions engineering would otherwise chase:

| Ruled out | Where we looked | What would have shown it | What we saw |
|---|---|---|---|
| <suspicion> | <tool, query or filter, window, and the control compared against> | <the record, count or state the suspicion predicts> | <the observation, quoted or counted> |

A row with no prediction is not a ruling out — move it to Open questions.

## 📎 Evidence ledger

| Source | State | What it gave, or why not |
|---|---|---|
| NOM | checked / tried and failed / not checked | |
| Jira history (NCS) | | |
| Public documentation | | |
| Dash0 | | |
| Sentry | | |
| Amplitude | | |

Add or remove rows to match what the ticket needed. A source that was not relevant is left out; a source that was relevant and went unchecked stays in, marked "not checked".

## ❓ Open questions for engineering
<Each one: the question, and the tool or access Support lacked to answer it.>

## 🧩 Observations surfaced by the evidence
<Services, constraints, queues, error strings and structural differences from the control, quoted exactly, each with its timestamp. Observations only, as _Code and components_ in the skill says. Omit the section if the evidence named none.>

## 📁 Attachments
<Screenshot paths, NOM links, the customer's own evidence.>
```

## Rules

- Emoji section markers belong in the description body and nowhere else. Never put one in a field value — `issueTypeName` is `"Support Request"`, not `"🛟 Support Request"`, and a field that wants an exact option value will reject a decorated one.

- Every claim is something you observed or counted. Mark anything else as an assumption. The severity assessment and the documentation review go in the NCS internal note; the ticket carries only the Business Impact line.
- Written to @writing-standards.md.
- Observations are named, never diagnosed: _Code and components_ in the skill.
- Reproduction steps are numbered, start from a logged-out state, and name the tenant. "Place an order" is not a step.
- The title is the problem, never the diagnosis: `[marine-layer] Payment stuck in Authorized after in-store purchase; Adyen shows it settled`, not `Capture requested but payment_account never captured — no payment_captured event`. No component, event or error names. The lowercase tenant slug comes first in square brackets, keeping any `-staging` suffix; never append the NCS key.
