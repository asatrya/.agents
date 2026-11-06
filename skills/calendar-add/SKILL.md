---
name: calendar-add
description: Add or modify Google Calendar events with consistent ownership prefixes, explicit timing, verified addresses, and clear formatted descriptions.
---

# Calendar Add

Always use this skill when the user asks to create, add, update, edit, or otherwise modify an event in Google Calendar. Use the connected Google Calendar app/capability available in the current environment; the skill defines event content and validation, while the actual calendar action remains an external mutation that requires the user's explicit request.

## Required event rules

- Determine who the event is primarily for. If it is primarily for Hana, start the event title exactly with `Hana //`. If primarily for Hafidz, use `Hafidz //`. If primarily for Listya, use `Listya //`. If primarily for the user, do not add a prefix. Do not add multiple prefixes. Preserve the user's meaningful event title after the prefix.
- Never add `aditya.satrya@gmail.com` as an attendee or guest. Treat it as the calendar account/owner rather than an attendee, and do not add or re-add it when creating or modifying an event. If an existing event already lists this address as a guest, do not remove it unless the user explicitly asks for that change.
- After every event creation, re-read the newly created event and inspect its attendee/guest list. The calendar owner `aditya.satrya@gmail.com` must not be reported as a guest. If the connector represents that address as an actual removable guest/attendee, remove it with the Calendar update action (`attendees_to_remove`) and re-read the event to verify the removal. Do not remove the organizer identity itself; if Google Calendar automatically includes or re-inserts the owner as the organizer/self, report that provider behavior and distinguish the organizer from true guests.
- Choose the destination calendar based on whether the user must attend in person: use the `Pribadi` calendar when the event requires the user's direct physical presence, and `Pribadi - Indirect` when it does not. If it is unclear whether the user needs to attend directly, ask the user before creating the event.
- A timed event must have an unambiguous start time and end time or duration, including the relevant date and timezone when ambiguity is possible. Never silently convert a timed event into an all-day event.
- Only make an event all-day when the user explicitly says it is all-day, spans a whole day/date, or otherwise clearly intends an all-day event. If an event is not clearly all-day and its time is missing or ambiguous, ask for the missing time before creating it.
- The location must be a clear physical address whenever a place is specified. If the place is known but the address is missing, search the internet to verify the address before creating the event. If the place cannot be identified confidently, ask the user rather than guessing. For remote events, use the supplied link or platform details as the location when appropriate; do not invent a street address.
- Write a useful description with clean formatting, especially newlines. Include the purpose/context, agenda or tasks, participants, preparation/items to bring, links, and practical notes when provided. Keep distinct pieces of information on separate lines or under short labels; do not collapse the user's details into an unreadable paragraph. Do not invent facts.
- Before creating or modifying the event, show the user a complete confirmation containing every event field: calendar, title, date, start and end time or all-day status, timezone, location/address, description, recurrence, attendees, reminders, and any other configured details. Do not create or modify the event until the user explicitly confirms that the complete summary is correct. If the user requests a change, update the summary and ask for confirmation again.
- After creation or modification, report every event that was successfully created or changed, individually and with all of its data: calendar, title, date, start and end time or all-day status, timezone, location/address, full description, recurrence, attendees, reminders, other configured details, and the calendar event link or ID when available. Do not reduce this post-action report to only a title and time. If multiple events were requested, list all successfully created or modified events and clearly identify any event that was not created or modified.

## Workflow

1. Extract the event title, primary person, required-attendance status, date, time or all-day status, timezone, location, description details, recurrence, attendees, and reminders from the request. For modifications, also identify the target event and which fields should change.
2. Resolve relative dates and times using the user's locale/timezone and the current date. If the request remains ambiguous, ask a concise clarification before creating the event.
3. Apply the title prefix rule and normalize the title without duplicating an existing correct prefix.
4. Verify or look up the full address when a named place lacks one. Treat the verified address as the event location and retain useful venue details in the description if relevant.
5. Draft the final event fields mentally and check that no required timing or location detail is missing. Ask for clarification instead of making a risky assumption.
6. Select `Pribadi` or `Pribadi - Indirect` according to the attendance rule.
7. Present a complete confirmation summary with all event data. Wait for an explicit confirmation; a prior general request to add the event does not replace this confirmation step.
8. Only after confirmation, create or modify the event in Google Calendar.
9. For every newly created event, re-read it. If `aditya.satrya@gmail.com` appears as an actual removable attendee/guest, remove it with `attendees_to_remove`, then re-read and verify. Preserve the organizer identity if the provider requires it, and report it as the owner/organizer rather than a guest. After this verification/cleanup, report each event with all event data and any available calendar link or ID. Clearly distinguish successful and unsuccessful actions, and include important assumptions or lookup results.

## Description format

Prefer a compact structure such as:

`Tujuan: ...`

`Rencana/agenda:
- ...`

`Peserta: ...`

`Persiapan:
- ...`

`Catatan: ...`

Include only sections supported by the user's information. Preserve links on their own lines when that improves usability.
