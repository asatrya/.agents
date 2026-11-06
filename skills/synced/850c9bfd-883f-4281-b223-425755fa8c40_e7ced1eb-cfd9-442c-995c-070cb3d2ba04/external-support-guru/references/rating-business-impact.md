# Rating Business Impact

One rating per ticket, S1 to S4. A ticket answered without an investigation is not rated. The retailer chose a level when filing; Support assigns the level the evidence supports and reports both. Problems caused by the retailer's configuration, data, API calls or third-party apps are outside the support terms and are rated for the record only.

The rating is a proposal from evidence. The support engineer has the last word and may set a different level without justifying it.

| Rating | Criterion | Looks like |
|---|---|---|
| S1 | Material adverse GMV impact on the retailer's operations, and no procedural workaround. | Refunds stuck across a store. Capture failing on every order. Nothing can be marked shipped. |
| S2 | Major functionality impacted or significant performance degradation, with no reasonable workaround; operations continue in a restricted fashion. | Orders cannot ship. ATP wrong, oversell or undersell. Availability export stale. |
| S3 | Partial, non-critical loss of use; medium-to-low impact; the business keeps functioning. | Cannot find a transaction. Configuration blocked. Manual receiving. Reporting gap. |
| S4 | Slight inconvenience, or a question about undocumented behaviour. | Missing notification email. Cosmetic UI. Receipt not generated. How-does-this-work. |

## Rules

- Seven criteria decide the rating: GMV impact, workaround, functionality, blast radius, trade state, reporter, detectability. Widespread across a tenant's trade with no workaround meets S1's material test; a contained share of orders rarely does, however alarming one case looks. Several tenants hit raise the chance it is a platform problem, not this tenant's severity.
- A workaround the retailer can run at acceptable cost rules out S1 and S2, whatever the money.
- Money is rated in proportion to the tenant's normal volume, never as a bare amount.
- A tenant not yet trading has no current GMV. Staging and sandbox tenants are rated on the functionality criteria. Only when the ticket names an imminent launch does GMV count, as the GMV the launch would lose.
- No launch date on the ticket means implementation time, which lowers the rating. A retailer under launch pressure says so.
- Other retailers hitting the same symptom go under prior occurrences, not into the rating.

## Writing the line

`Business Impact: S3, retailer asked S1. 2 orders of ~400/day; refunded by hand in NOM.`
`Business Impact: S2. Go-live 11-04 blocked; capture fails on every test order.`
`Business Impact: S3, retailer asked S2. Sandbox tenant, no launch date; implementation time.`
