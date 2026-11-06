# The investigation record

One file per investigation: `<investigation>/investigation/record.md`. YAML frontmatter for the facts, markdown below for the parts that need sentences.

It carries the full working for whoever needs it: the facts, the timeline, the evidence ledger, the hypotheses, the severity assessment, the documentation review, and the assessment with its reasoning. The ticket description carries only what changes an assessment, and evidence comments describe the evidence; neither pastes this file.

## Why frontmatter and not a prose file

- A later agent can parse it. The next investigation of the same symptom reads `classification`, `entities` and `hypotheses` without re-deriving them from prose.
- A person can read it unrendered. YAML keys are English; no tooling required.
- It is diffable. Two investigations of the same defect can be compared field by field.
- It is one file, so it can be attached, pasted, or linked as a whole.

## Schema

```yaml
---
schema: newstore-support-investigation/v1
ticket: NCS-9718                  # the NCS key
tenant: marine-layer
environment: production           # always production for support work
opened: 2026-09-18                # ticket created
triaged: 2026-09-21
skill_version: 0.2.2

classification:
  decision: platform-problem      # works-as-designed | documentation-gap |
                                  # tenant-configuration | data-issue | platform-problem |
                                  # service-request | product-request
  confidence: confirmed           # confirmed | plausible | needs-evidence
  severity: S3                    # Support's, measured
  customer_severity: S3           # what the ticket asked for
  severity_basis: >-              # one line; the criterion met; why they agree or differ
    One record; capture normal on the tenant; manual capture available.
  reasoning: >-                   # why this decision over the runner-up, one paragraph
    Capture was dispatched and never reached the PSP; the order is complete,
    the tenant captures normally, and no configuration differs from the control.
  routed_to: FO
  engineering_ticket: FO-2268

severity_assessment:              # one entry per criterion, in this order; the NCS internal note is composed from it
  - criterion: gmv_impact         # current money, in proportion to the tenant's volume
    sign: "➖"                     # ➖ lowers · ➕ raises · ❗ would raise further · ➿ not measured
    finding: One order of 403.95 USD against ~400 orders/day; immaterial
    data_points:
      - source: dash0
        value: "payment-account captured 40/hour on marine-layer, 2026-09-12 to 09-18"
      - source: nom
        value: "order ML006537457, 403.95 USD, Authorized since 09-12"
  - criterion: workaround         # exists, and what it costs the retailer
    sign: "➖"
    finding: Manual capture in NOM, ~1 minute per order
    data_points:
      - source: docs.newstore.com
        value: "Payments > Capture a payment manually, quoted in documentation.quotes"
  - criterion: functionality      # major | partial non-critical | inconvenience; business continues?
    sign: "➖"
    finding: Capture works on every other order; business continues normally
    data_points:
      - source: dash0
        value: "0 capture errors on the tenant in 7 days"
  - criterion: blast_radius       # extent, tenants, dependency, rough projection
    sign: "➖"
    finding: One record, this tenant only; depends on adyen in-store capture; projection ~0/day
    data_points:
      - source: dash0
        value: "payment-account errors, no tenant filter, 14 days: 1 hit, marine-layer"
      - source: ncs
        value: "summary ~ 'stuck in Authorized', 90 days: 2 tickets, both marine-layer"
  - criterion: trade_state        # live and trading | implementation time | launch named on the ticket
    sign: "➖"
    finding: Live, trading; 12 stores with daily till counts
    data_points:
      - source: amplitude
        value: "Associate App closeTill, 12 stores, daily, 30 days"
  - criterion: reporter           # retailer | store-operator | integration-partner, and ticket history
    sign: "➖"
    finding: Integration partner, API tickets across 3 retailers
    data_points:
      - source: ncs
        value: "reporter account: 11 tickets, 3 tenants, 180 days"
  - criterion: detectability      # would the platform find this without the customer?
    sign: "❗"
    finding: No error logged, no retry, no alert; found only by reconciliation
    data_points:
      - source: dash0
        value: "no ERROR record for the order uuid in any namespace; same query without the uuid returns 94 in the window, so the signal was live"
      - source: sentry
        value: "no event for payment-account in the window; project received 212 events over it"

reporter:
  kind: integration-partner       # retailer | store-operator | integration-partner
  note: >-
    API and documentation tickets across several retailers.

claims:                           # one per factual assertion made on the ticket
  - claimant: retailer            # retailer (incl. its store operators and the
                                  #   integration partners filing for it) |
                                  # support | engineering |
                                  # third-party (carrier, PSP, tax provider)
    claim: Adyen settled the payment on 2026-09-12
    status: contradicted          # confirmed | contradicted | unverified
    basis: payment-account dispatched no capture call in the window

entities:                         # whatever the ticket is about; keys are free
  sales_order: bb751ea1-e0e1-4355-9d83-c2795563d5b4
  external_order_ref: ML006537457
  psp: adyen
  psp_instrument: CK9CSL2MMV254W25
  amount: 403.95
  currency: USD
  placed_at: 2026-09-12T20:37:11Z
  channel: in-store
  store: SDL

timeline:                         # short steps, one per row; no pasted log blocks
  - at: 2026-09-12T20:37:11.601Z
    service: payment-account
    step: processing add_financial_instrument
    outcome: ok                   # ok | fail | absent | unknown

evidence:
  checked:
    - source: dash0
      query: otel.log.body contains <order uuid>
      found: 50 records across 7 namespaces
      file: claim-03-capture-dispatch.md    # the sidecar holding the rows, if one was saved
  tried_failed:
    - source: payment-api
      blocker: agent permission controls
      worth_checking: true            # would a successful call change the conclusion?
  not_checked:
    - source: adyen
      why: retailer-only
      worth_checking: true

hypotheses:
  - id: H1
    statement: Order never reached a state that triggers capture
    verdict: ruled-out            # confirmed | plausible | ruled-out | needs-evidence
    basis: CompleteCashAndCarryOrder fired at 20:37:14; order reached Complete

open_questions:
  - question: Why did the dispatched capture never call the PSP?
    needs: knowledge of the capture path
    owner: engineering

documentation:
  verdict: silent                 # matches | contradicts | silent
  quotes:                         # the sentences relied on, with their page
    - page: https://docs.newstore.com/docs/payments/capture
      text: "Payments are captured when the order is fulfilled."
  gaps:
    - Authorization validity period is undocumented
---
```

Below the frontmatter, three sections in this order, each only as long as it needs to be:

- **Assessment** — the outcome, the runner-up and why it lost, and for a handover the Support-closable outcomes ruled out with the evidence that ruled each out.
- **Documentation** — what the pages promise against what was observed, where they are silent, and what that means for the ticket.
- **Customer-facing explanation** — the finding in the retailer's terms. The customer reply is written from it when the support engineer asks.

## Rules

- Frontmatter is facts, body is sentences. If something fits a key, it goes in a key.
- `outcome`, `verdict`, `sign`, `criterion`, `claimant` and `status` are closed vocabularies. Do not invent values; a new one means the schema needs changing.
- A triage that stops before the handover gate records its best-supported outcome so far under `decision`, with `confidence: needs-evidence`. There is no undecided value.
- A record with nothing under `evidence.checked` was answered without an investigation: it carries no `timeline`, `claims`, `hypotheses`, `severity_assessment` or `classification.severity`, and its `routed_to` is empty. `documentation` holds the pages and earlier tickets the answer came from.
- In every other record all seven criteria appear in `severity_assessment`, in that order, even when the answer is "not measured" (sign ➿, finding says why).
- Every data point names its source and the query window or record it came from. A finding with no data point is an opinion.
- `classification.severity` must be defensible from the ➕ and ➖ lines alone; ❗ lines explain why a low rating still warrants a fix.
- Timeline steps are short. Full log strings belong in the engineering ticket's Observations section, not here.
- No self-narration (@writing-standards.md). `hypotheses[].verdict: ruled-out` carries what "I was wrong earlier" was trying to say.
- Redact before sharing. `record.md` goes through redaction like everything else; see filing-an-engineering-ticket.md.
- Keep `skill-notes.md` separate. That file is about the skill; this one is about the ticket.

## Evidence sidecars

A data point names the query; the sidecar holds what it returned.

One sidecar per assertion that cites a data point — a claim, a severity criterion, a hypothesis — not one per query.

```
evidence/claim-01-adyen-settlement.md
evidence/claim-02-no-capture-call.md
```

```markdown
---
backs: claims[0]                  # or severity_assessment.detectability, hypotheses.H1
source: dash0
query: otel.log.body contains <order uuid>
window: 2026-09-12T00:00Z..2026-09-19T00:00Z
captured: 2026-09-21
---

<the rows as they came back>
```

- A sidecar is never rewritten; a later query is a later sidecar.
- Anything not matching `keep_identifiers` in `scripts/pii-patterns.json` is masked in the row before it reaches the file.
- The record points at a sidecar by **filename**, never by a Drive id.

## What goes where

| | `engineering-handover.md` | `record.md` | `skill-notes.md` |
|---|---|---|---|
| The finding | ✅ | ✅ | |
| Assessment and reasoning | ✅ | ✅ | |
| What was ruled out | ✅ | ✅ | |
| Severity and its assessment | Business Impact line only | ✅ | |
| Documentation review | open question only | ✅ | |
| Full timeline | short version | ✅ | |
| Every source consulted | summary | ✅ | |
| Queries used | | ✅ | |
| What misled the investigator | | | ✅ |
| Candidate skill changes | | | ✅ |

Comments on the engineering ticket: see _Comments_ in the skill.
