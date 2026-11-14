---
name: liqo-update-berita-acara
description: Update the matching Liqo 1, Liqo 2, or Liqo 3 Berita Acara tab with Liqo N events after the last recorded date through current_date, including participant status mapping and cell notes for attendance explanations.
---

# Liqo Update Berita Acara

Use this skill when the user asks to add or synchronize a Liqo event into the Google Sheet tab `Berita Acara`. The source event must have a title beginning with `Liqo 1`, `Liqo 2`, or `Liqo 3` (the `Liqo N` prefix family).

## Mandatory request gate

- The user's request must explicitly state which Liqo to update: `Liqo 1`, `Liqo 2`, or `Liqo 3`. The event title, workbook URL, prior conversation context, or the presence of multiple matching events must not be used to infer a missing Liqo number.
- If the request does not clearly name exactly one of `Liqo 1`, `Liqo 2`, or `Liqo 3`, stop immediately and ask the user which Liqo should be updated. Do not search Calendar, read a workbook, or write any spreadsheet data before clarification.
- If the user's stated Liqo number conflicts with the event title prefix, stop and ask for confirmation; do not silently reroute based on the title.

## Scope and defaults

- Use the **Personal** context for this calendar and spreadsheet workflow.
- Use Google Calendar and Google Sheets connectors directly. Do not use a browser.
- Default source calendar: the authenticated user's primary calendar (`aditya.satrya@gmail.com`).
- Route the event to the target workbook from its title prefix:
  - `Liqo 1` -> `Buku Kendali Liqo Berlin 1`, ID `1veu0NFqMxTXe1_n1oXsD2qoxgDsNwv_NEVe8M0FNwIw`.
  - `Liqo 2` -> ID `149hxPTO9xCw7TwGfLtjrgh7EY_YrwxoMiO5eFRrVwU8`.
  - `Liqo 3` -> `Buku Kendali Liqo Berlin 3`, ID `11WSPd7rlaoU1gfq27lFE8cVy39eUJUdAXNPm57qdFHc`.
- The target tab is `Berita Acara` in each workbook. Resolve its actual `sheetId` from spreadsheet metadata before writing; a URL `gid` is only a hint, not the authority.
- A user-provided calendar, spreadsheet, tab, or event target overrides these defaults, but still use the event title to identify the Liqo N source unless the user explicitly supplies a different mapping.
- Post-filter Calendar results so the event summary matches `^Liqo [123]\b` (case-normalized only if needed). Do not accept an event that merely contains `Liqo` elsewhere in its title.
- If the title is only the literal `Liqo N`, uses a number other than 1, 2, or 3, or cannot be mapped unambiguously to one workbook, stop and ask the user instead of guessing.
- Do not create a duplicate record when the target date already has a row. Update the existing row.

## Header-first column addressing

- Do not assume that a semantic field is in a fixed A1 column such as `B`, `C`, `D:AB`, or `AC`.
- Read the relevant table header row first, identify columns by their header text, and only then convert the resolved positions to A1 letters (A, B, C, ...) or zero-based indexes for connector range requests.
- Use the same header-first lookup for `Basic Data`: locate the participant name and participant-code columns from that tab's header rather than assuming they are always B and C. The known starting range is only a scan area, not a static schema.
- For `Berita Acara`, resolve the date, held/status, count, attendance-code, and event-facts columns from the actual header row. Attendance columns are the columns whose headers match the codes read from `Basic Data`.
- Prefer exact trimmed, case-insensitive header matches. If a required header is missing, duplicated, or ambiguous, stop and ask before reading or writing dependent cells.
- After resolving headers, it is acceptable to refer to the resulting columns by their A1 letters in API calls and verification reports, but never derive those letters from this skill's hardcoded assumptions.

## Synchronization window

- The update window is dynamic for the explicitly requested Liqo: strictly after the last recorded date in that Liqo's routed `Berita Acara` table through `current_date`, inclusive.
- Determine `last_record_date` from the latest valid date in the existing records under the header-resolved date column. Do not use a hardcoded row number, an example date from the user's prompt, or a calendar search start date supplied by memory.
- Search Calendar only for dates satisfying `event_date > last_record_date` and `event_date <= current_date`. Interpret `current_date` at runtime using the task's current date and the calendar/workbook timezone.
- If no valid last record date exists, stop and ask the user for the intended starting date; do not perform an unbounded historical search.
- If `last_record_date` is already `current_date` or later, report that the synchronization window is empty and make no writes.
- A date that is already recorded is not part of this incremental window. Never overwrite it as part of this range update unless the user explicitly requests a correction to that existing record.

## Workflow

1. After the mandatory request gate passes, route the explicitly requested Liqo to its workbook. Confirm spreadsheet metadata and the exact visible `Berita Acara` tab; use its resolved `sheetId`, not a guessed tab name or `gid`.
2. Read the `Berita Acara` header and all existing record dates with `google_drive_get_spreadsheet_cells`. Include `userEnteredValue`, `effectiveValue`, `formattedValue`, `dataValidation`, `note`, and `userEnteredFormat`. Resolve the date column from the header, find `last_record_date`, and apply the synchronization-window rules above.
3. Search the primary Calendar with a bounded range from the day after `last_record_date` through `current_date`. Query the explicitly requested prefix (`Liqo 1`, `Liqo 2`, or `Liqo 3`), post-filter so each summary starts with that same prefix (`^Liqo [123]\b`), and keep only events in the inclusive window. Read each retained event with `google_calendar_read_event` so its description, location, start/end, and attendees are available. Do not use an event title to infer a missing Liqo selection.
4. If no matching events are found, report that no records need updating and make no writes. If more than one matching event exists for the same Liqo and date, stop and ask which event to use before writing. Otherwise process retained events chronologically.
5. Read the participant data directly from the selected workbook's `Basic Data` tab before parsing attendance. Start by scanning the expected participant area around rows 4–28, then use that tab's header to locate the name and code columns and inspect all populated participant rows. Treat the current full-name/code pairs there as authoritative for this run; no participant roster or aliases are known statically from this skill. In `Berita Acara`, use the header-derived attendance columns whose headers match those codes. Use shortened forms only when they resolve unambiguously against the freshly read mapping.
6. For each retained event, read its candidate date row and nearest complete row with `google_drive_get_spreadsheet_cells`. If no matching date exists, use the next row after the last populated date at that point in the incremental run. Prefer an already preformatted row. If structure must be extended, preserve the formula, validation, formatting, and row shape before writing row-specific values. Never use a values-only append into a populated structure.
7. Parse each event description into event facts and participant records. Do not infer a status that is not explicitly present. Write the date as a typed spreadsheet date in the header-resolved date column, set the header-resolved held/status column to `Ya` when the event was held, preserve the formula in the header-resolved count column, write participant statuses to their header-resolved attendance columns, write the requested event facts to the header-resolved event-facts column, and add notes with a targeted `updateCells` batch.
8. Re-read every written row and verify values, formulas, validation, notes, and formatting. Report the tab, rows, and event dates changed, along with any events intentionally skipped or cells left blank.

## Participant mapping

- Do not use a hardcoded participant list, code list, or alias list from this skill.
- Read the current populated participant rows from the selected workbook's `Basic Data` tab. Use the name/code pairs returned by that read as the only authoritative mapping for the current update.
- Use the `Berita Acara` header row to map each code to its attendance column; do not assume a fixed range such as `D1:AB1`.
- If a participant name or shortened source form cannot be matched unambiguously to the freshly read `Basic Data` mapping, stop before writing that participant's cell and ask for clarification.

## Attendance and notes rules

- Valid attendance codes are the existing dropdown values: `H`, `I`, `A`, `S`, and `-`.
- A code immediately associated with a participant is written to that participant's column.
- Parenthetical or trailing explanations are written as cell notes, not appended to the visible status cell. Keep the note concise and retain the source wording where practical.
- If the explanation means the participant is in Indonesia, such as `mudik`, `di indo`, `ke indo`, `pulang ke Indonesia`, or an equivalent phrase, the participant status cell must be empty and the explanation must be stored as a cell note. This rule takes precedence even if the source also contains `I`.
- If a participant has an explanation but no explicit valid status code, leave the status cell empty and add the note.
- If neither a status nor an explanation is present, leave the status cell unchanged/empty. Never convert missing data into `A`, `I`, or `-`.
- For note-only writes, use `updateCells` with `fields: "note"` so the status and validation are preserved. For a status cell that must be cleared while adding a note, update `userEnteredValue` and `note` together with the precise field mask.

## Event-facts column

For this workflow, write only the requested event facts in the column whose table header designates the event facts/details field, using the established semicolon-separated style:

`Tempat: <location>; Tilawah/tadabbur: <value>; Materi: <value>`

Use the exact location and description facts from the event. Omit a label only when that fact is genuinely absent. Do not put participant explanations in the event-facts column; those belong in cell notes.

## Write and verification safeguards

- Use `google_drive_batch_update_spreadsheet` with precise `updateCells` ranges and exact `fields` masks. Grid indexes are zero-based and end-exclusive.
- Do not overwrite the formula in the header-resolved count column, dropdown validation, formatting, or unrelated rows.
- When adding a row, clear copied row-specific statuses and notes before applying the new event data. Preserve the row's existing date format, borders, alignments, and dropdown validation.
- After writing, read the complete affected row with `google_drive_get_spreadsheet_cells`. Confirm the header-resolved event-facts column, all status cells, note text, the count formula, the computed count, and the valid dropdown rule.
- If the event description is ambiguous, stop before writing the ambiguous participant cells and ask for clarification. Summarize any cells intentionally left blank.
