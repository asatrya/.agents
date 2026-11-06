# Forwarding product feedback

A `product-request`, and a works-as-designed finding the retailer wants changed, do not get an
engineering ticket. They reach the product team through the product feedback form, and this
reference prepares that submission.

# Route

Customer Success first. They check whether a best practice already covers the ask, and whether
Professional Services can deliver it. Only what survives both reaches the form. Say in your
report to the support engineer that this step is owed; do not skip to the form because the finding
looks obvious.

Form: https://forms.monday.com/forms/693a19fdcdfface0372e4cc9c87b8f66?r=use1
Open to anyone, no login. Every submission is validated by the Success Team.

Do not use ProductBoard.

# Never submit the form

Write the field values to `product-feedback.txt` at the top level of the ticket directory and hand the
support engineer the path and the form link. They submit it under their own name. The form asks
who is submitting, and an agent cannot answer that for someone else.

# Fields

All five are required.

| Field | Limit | What goes in it |
|---|---|---|
| Your Name | 255 chars | Leave as `<support engineer>`. Never fill it in. |
| Retailer | — | The retailer's name as they are known commercially, not the tenant slug. |
| Product / Module | select | Read the live option list on the form and name the closest. If none fits, say so in the file rather than guessing. |
| Topic | — | A short label, two or three words: "Stock on hand filters", "Returns flow". Not a sentence. |
| Feedback | 2000 chars | See below. |

2000 characters is the binding constraint. A triage record is far longer, so the feedback
field is written fresh, not pasted. Cover, in this order: what the user expected, what the
platform does instead, why that gap costs the retailer something, and how many retailers have hit
it. Cite prior ticket keys by number only.

# What never goes in

- Code paths, service internals, a proposed fix. Product decides what to build; this is a
  description of a gap, not a design.
- Personal data of any kind. Refer to stores and orders by ID.
- A severity or a deadline. The form is not a priority channel.

# After submitting

The support engineer records that it was submitted in the NCS internal note, so the next person
reading the ticket can see the feedback already has a home and does not re-raise it.
