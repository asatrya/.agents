---
name: immobilienscout24-contact-inquiry
description: Send a tailored inquiry on ImmobilienScout24 from a property link copied from WhatsApp Web, using user-provided contact details and message content.
---

# Immobilienscout24 Contact Inquiry

Use this skill when the user wants to contact a landlord or listing provider on ImmobilienScout24 from one or more property URLs. Use Chrome with Computer Use for the browser interaction.

## Communication and browser

- Always communicate with the user in English, regardless of the language used in the listing or inquiry message.
- Always use the user's authenticated Google Chrome session to open ImmobilienScout24 and the supplied property link. Do not switch to another browser unless the user explicitly asks.

When in doubt, ask the user before proceeding. Do not guess which listing, account, recipient, form choice, personal detail, or action the user intended.

## Inputs

Obtain or confirm these before sending:

- One or more property URLs supplied by the user. Do not retrieve them from WhatsApp unless the user specifically asks for that.
- The inquiry text or permission to use the user's approved template.
- The desired salutation (for example, Herr, Frau, or Divers) when the form requires it. Use `Herr` by default unless the user specifies otherwise.
- If the form asks about pets, select `keine Haustiere` by default unless the user specifies otherwise.
- Any profile fields the form asks for that are not already populated.

Treat names, addresses, employment, income, family details, and other personal information as private. Never invent or expose them in a summary; use values supplied in the current task or already populated in the authenticated form.

## Default landlord message

Use this message unless the user supplies different wording. If the landlord's specific name is clearly known from the listing, replace only “Vermieter/in” with the appropriate name and salutation. When the name or salutation is uncertain, ask the user rather than guessing.

```text
Sehr geehrte/r Vermieter/in,

mein Name ist Aditya Utama. Ich bin fest angestellt als Senior Data Engineer bei der Newstore GmbH. Zurzeit wohnen wir in der Bürgerstraße, 12347 Berlin.

Wir suchen nun ein langfristiges Zuhause, in dem sich unsere Familie – meine Frau, unser 12-jähriges Kind und unser 8-jähriges Kind – für viele Jahre niederlassen kann.

Wir sind zuverlässige Mieter mit einem stabilen Einkommen (4.882 € netto pro Monat, exklusive Boni) und kümmern uns stets gut um unsere Wohnung. Wir haben keine Haustiere, rauchen nicht und führen einen ruhigen, entspannten Lebensstil ohne Partys – wir legen großen Wert auf eine friedliche Wohnumgebung.

Falls die Wohnung noch verfügbar ist, würde ich mich sehr freuen, einen Besichtigungstermin zu einem für Sie passenden Zeitpunkt zu vereinbaren.

Mit freundlichen Grüßen
Aditya Utama
```

## Workflow

1. Use the authenticated Google Chrome session (the `[@Chrome](plugin://browser@openai-bundled?browserFamily=chrome)` browser) to open `https://www.immobilienscout24.de/` and then the supplied property URL.
2. Verify that the active account is signed in through Google as `aditya.satrya@gmail.com`. If the account is not signed in or a different account is active, pause and ask the user to complete the Google sign-in; never request, record, or repeat passwords or one-time codes.
3. After the signed-in state is verified, open each property URL supplied by the user, one at a time. Verify that each page is an ImmobilienScout24 listing before continuing.
4. Select the listing’s contact/message action and open the inquiry form.
5. Fill the message field with the user-approved text. Preserve paragraph breaks and do not alter personal claims without confirmation.
6. Complete only the required form fields, including the user-selected salutation. If a pet field is present, select `keine Haustiere` by default. Leave optional marketing, provider-follow, or moving-service offers disabled unless the user explicitly requests otherwise.
7. Before each irreversible send action, show the user the intended listing and a privacy-safe summary of the message, then ask for confirmation if they have not already explicitly authorized sending in this task.
8. Submit the form only after confirmation. Verify the form closes or displays a success state, then close the dialog/page and continue with the next supplied property URL.
9. After each successful submission, always report the submitted property's key details (including title, location, rent if visible, provider, and Scout-ID if visible) and every form field value submitted. Include values the agent entered or selected and clearly label any values that were pre-populated and left unchanged. Do not omit personal fields merely because they are sensitive; the user explicitly requested the complete field-value report.

## Verification and stopping conditions

- Confirm the URL/title still identifies the intended listing immediately before sending.
- If the listing is unavailable, the form is materially different, required data is missing, or the recipient cannot be verified, stop and ask the user.
- If the site presents a CAPTCHA, unexpected security check, or authentication challenge, pause for the user rather than bypassing it.
