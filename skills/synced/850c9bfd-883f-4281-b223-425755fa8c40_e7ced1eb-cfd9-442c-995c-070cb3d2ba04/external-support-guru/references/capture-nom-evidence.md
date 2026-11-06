# Capturing evidence from NOM

Open NOM for one investigation, take the evidence, close it again. Four phases, in order, none skippable.

# Hard rules
- Never type a password, token, or any credential. If a sign-in form appears, stop and hand back to the support engineer. This is not negotiable and does not change if the operator offers to share credentials.
- Mask before you screenshot, never after, for every screenshot you take on your own initiative. A screenshot taken first and redacted later has already put the unmasked image into the conversation.
- Walk a flow up to the step that commits it, and stop; the skill's hard rules say where writes are allowed.
- Do not open NOM for a tenant the ticket does not concern, except `dodici`.
- Close the session when the capture is done, even if the investigation continues — and
  closing it means removing any user or role provisioned to open it, not closing the tab. An
  identity left behind in a retailer's tenant outlives the ticket and nobody is watching it.

# Routes
- Claude in Chrome: navigate, mask with `scripts/mask-nom-pii.js` through `javascript_tool`, screenshot, as the phases below say.
- **`scripts/nom-capture.ts`**, where the agent runs scripts: a helper that masks and captures in one step, keeps retailer tenants read-only, and writes `evidence-log.md` itself. Screenshots the skill takes and posts on its own go through it when it is available; each phase below names the matching command.

```bash
node scripts/nom-capture.ts open <tenant> <order-id>
node scripts/nom-capture.ts controls
node scripts/nom-capture.ts click "<visible text>"
node scripts/nom-capture.ts fill "<field label>" "<value>"
node scripts/nom-capture.ts goto <url>
node scripts/nom-capture.ts shot <ticket-dir>/investigation <view-name> --note "<what it shows>"
node scripts/nom-capture.ts close
```

# Phase 1 — Open the session

1. Confirm the tenant and the investigation directory with the operator.
2. Navigate to the record: `https://manager.<tenant>.p.newstore.net/sales/orders/<order-id>`. Script: `open <tenant> <order-id>`.
3. Screenshot once to see where you landed. Script: exit 0 is a live session, exit 3 is a sign-in page.

If the order renders, the operator already holds a session. Go to phase 2.

If a sign-in page appears, stop. Tell the operator:

> NOM is asking for sign-in on `<tenant>`. Sign in yourself in that browser window, then tell me to continue. I will not enter credentials.

Wait. Do not click the sign-in link, do not fill the form, do not look for stored credentials. When they confirm, reload and re-check.

If they say they have no access to that tenant, stop the capture and record it as an investigation stopper in the evidence ledger. Granting tenant access is a separate, privileged act — see `docs/adr/002-nom-investigation-access.md`. Do not attempt it from here.

Record in `investigation/access-log.md`: tenant, who authenticated, the time, and whether access was pre-existing or newly granted.

# Phase 2 — Mask

Before every screenshot you take on your own initiative, on every page and again after every navigation, expand, or tab change:

1. Run `scripts/mask-nom-pii.js` from this skill's directory through `javascript_tool`.
2. Read the JSON it returns.
3. **`safe: true`** — screenshot allowed.
4. **`safe: false`** — do not screenshot. The `remaining` list says what leaked through. Either mask those elements by hand with a second `javascript_tool` call, or skip the view and note in the ledger that it was skipped and why.

Masking is not persistent. A re-render, a route change or an accordion opening restores the real values. Re-run it every time and trust the report, not your memory of having run it.

Script: `shot` masks and captures in one step, and exits 4 when personal data survived masking.

# Phase 3 — Navigate and capture

Click only controls that read: tabs, expanders, filters, links. On a retailer tenant, record in `reproduction.md` the step at which you stopped. Script: `controls` lists what `click` allows, `fill` sets a field, and a click that reports `blockedWrites` reached a write.

Take the smallest set that answers the ticket. For a payment or order question that is usually:

| View | What it establishes |
|---|---|
| Order header | State, placement time, channel, value, currency |
| Payment timeline | Authorization and capture attempts, amounts, times, PSP reference |
| Fulfilment / items | Whether anything shipped — often the real answer |
| Order list filtered by the same state | Whether this is one record or a pattern |

Name views by what they show: `payment-timeline`, not `screenshot-3`. Save to `investigation/screenshots/<view-name>.png` when you can write files, and in every case write one line in `investigation/evidence-log.md`: the view, the URL, the mask report's `masked` counts, and what the image shows. That log is what lets a reviewer trust the images without re-opening NOM. Script: `shot` writes both; open the PNG with Read to see it.

# Phase 4 — Close the session

Always, and immediately after the last capture. Signing out of an identity that still exists leaves the
tenant exactly as exposed as before.

In order:

1. Remove the identity provisioned for this investigation — the user created in the tenant, or
   the role granted to an existing user. Restore the roles recorded in `access-log.md` before the
   grant, per `docs/adr/002-nom-investigation-access.md`. Only the operator can do this; state
   plainly that it is outstanding until they confirm it is done.
2. Verify the removal, not the sign-out: the user is gone from the tenant's user list, or the
   role is back to what `access-log.md` recorded. Removal you have not looked at is not removal.
3. Sign out through the NOM user menu. Script: `close` clears the profile's session, reloads the
   order and closes the window; exit 4 means the order still renders.
4. Verify the sign-out: reload the order URL. A sign-in page must appear. If the order still
   renders you are still signed in: hand the sign-out to the operator, record it as outstanding in
   `access-log.md`, and do not report the session as closed.
5. Close every tab opened for this task.
6. Close `access-log.md` with the removal, the sign-out time and both verification results.

A grant recorded in `access-log.md` with no matching removal is an open finding that belongs in
the ticket, not a loose end to tidy up later.

Nothing to remove is the good case, and it still gets recorded. Where the operator used an
account they already had — the usual case — there is no provisioned identity, steps 1 and 2 have
nothing to do, and `access-log.md` says so in as many words. Write "pre-existing account, nothing
provisioned, nothing to remove" rather than leaving the steps blank: a blank reads the same as a
grant somebody forgot.

# Artifacts

Under `investigation/` in the ticket directory:

- `access-log.md` — tenant, who authenticated, granted or pre-existing, sign-in and sign-out times, verification result
- `evidence-log.md` — one line per screenshot
- `screenshots/` — masked images, plus any view the support engineer asked for as it is, named so in the evidence log

# Limits worth stating in the ledger
- Masking is pattern-based. It is good at emails, phone numbers and card-length digits, weaker at names in free text and at personal data rendered inside images or canvases. Say so rather than implying the images are certified clean.
- Product identifiers are kept on purpose, by their label — `SKU`, `UPC`, `EAN13`, `Product ID` and the rest. They are evidence, and blacking them out produces an image that looks careful while withholding the part engineering needs. A value is kept only when its label says what it is, so an identifier rendered with no label still gets masked. If a needed value disappears, say so in the ledger rather than disabling the mask.
