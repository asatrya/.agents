# Deciding what kind of problem this is

Pick one outcome. A service request is always settled without an investigation. A product request may be settled at the ask gate, or be what the investigation finds.

| Outcome | What it means | Where it goes |
|---|---|---|
| Service request | The ticket asks for information, or for an action Support performs. Nothing is claimed broken. | Chat report carrying the answer or the action taken. Never an engineering ticket |
| Product request | The ticket asks for behaviour the platform does not have — stated plainly, or as an expectation the documentation never promised. | Chat report; the support engineer decides whether to forward it. Never an engineering ticket |
| Works as designed | The platform did what it is built to do. The retailer expected something else. | Chat report; the customer reply and the internal note on request. Never an engineering ticket |
| Documentation gap | The platform did what it is built to do, but the public documentation does not say so, or says the opposite. | Chat report, plus a handover to the team that owns the feature |
| Tenant configuration | A setting, feature flag, integration credential, store or routing setup on this tenant produces the behaviour. | Chat report with the correction, or a handover if Support cannot change it |
| Data issue | The platform behaved correctly, but a specific record is in a state it cannot leave on its own. | Handover, with the record IDs and whether a self-service API exists |
| Platform problem | The platform did something it is not built to do, or failed to do something it is built to do. | Handover |

## How to tell them apart

Ask, in this order:

1. What does the platform promise? Find the public documentation for the feature, API or flow. The documented contract is what the retailer is entitled to. If observed behaviour matches it, this is works-as-designed or a documentation gap, not a defect — regardless of how reasonable the retailer's expectation was.
2. Does it reproduce on a clean tenant? If the same steps on the retailer's sandbox tenant produce the same result, it is platform behaviour. If they do not, it is tenant configuration or data.
3. Is it one record or a pattern? One record in a bad state with everything else fine points to a data issue. The same symptom across records, tenants or time points to a platform problem.
4. Did it change? If the retailer did this successfully before and cannot now, find when it changed. A start date turns a vague report into something engineering can bisect.

## Causes to check for

Observations to check, not conclusions. Not exhaustive.

- A write that failed: the record never reached the state the action should have produced
- A message that was never produced or never consumed: the next step in the flow has no trace
- A read model behind its source: NOM shows one state, the record's events show another
- Tenant configuration or a feature flag: the behaviour differs from a tenant where it works
- Tenant data: one record in a state the others never enter
- A legacy UI page: the same data looks right on the new page or in the API
- An expectation the platform never promised
- Documentation that is wrong, stale or silent

## Not a triage outcome

- "The customer is wrong." Even when the platform is right, the report tells you the documentation or the interface misled someone. Record that.
- An engineering ticket for behaviour that works as designed. It is closed as won't-do.
  Documentation, interface and product-gap feedback goes in the internal note, and the support
  engineer decides whether to forward it.
- "Needs engineering to investigate." That is what the handover is for, but it still needs the outcome above, your evidence, and your best hypothesis. Handing over an unexamined ticket is forwarding, not triage.
- A remedy the customer proposed, adopted as the diagnosis. "Please mark the payment as captured" is a request; whether capture failed, and why, is the triage.

## Before a handover

A handover is the last outcome, not the default. Engineering takes a ticket when Support has run out of evidence to collect, not when Support has run out of ideas.

Before writing `engineering-handover.md`, rule out the outcomes Support closes alone, in this order, and record each verdict under `hypotheses` in `record.md`:

1. Works as designed. The documentation describes what the retailer saw. Quote the sentence.
2. User error. The steps the reporter followed differ from the documented ones. Repeat the documented steps on the retailer's sandbox tenant, or on `dodici`, and record the result.
3. Missing feature. The retailer expects something the platform never promised. That is `product-request`, not a defect.
4. Tenant configuration. A setting, feature flag, credential, store, routing or integration setup explains it. Compare with a tenant where the flow works. If Support can change the setting, that is the resolution.
5. Data Support can fix. A self-service API or a NOM action puts the record right.

Each one is ruled out by evidence: a documentation quote, a reproduction, a comparison with a working tenant, a configuration read. "Unlikely" is not a verdict.

Write the handover only when every one of the five carries `ruled-out`, or `needs-evidence` naming a tool Support never has, and no check Support could still run would change the call. If one more query, one more tenant comparison or one more reproduction attempt could still point to an outcome Support closes alone, run it first.

A hypothesis that stays `plausible` because a source Support does have was tried-and-failed in this session is not ruled out. Stop, tell the support engineer which source and which question, and do not write the handover around the gap.

## Confidence

State it, and state what would change it:

- **Confirmed** — reproduced, or the evidence is unambiguous
- **Plausible** — consistent with the evidence, not reproduced
- **Needs-evidence** — needs a tool or access Support does not have; name the tool and the question

Never present Plausible as Confirmed in the chat report or the customer reply.
