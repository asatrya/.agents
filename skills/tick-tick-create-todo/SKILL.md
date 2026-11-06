---
name: tick-tick-create-todo
description: Create a to-do item in TickTick from a natural-language request, including its list, due date, priority, tags, notes, and subtasks when specified.
---

# TickTick Create Todo

Use this skill when the user asks to add, create, or capture a task in TickTick. The user’s current instruction is the source of truth for the item; do not invent task details from an inaccessible or unrelated conversation.

## Parse the request

Extract only details the user supplied or that are unambiguous:

- Task title: preserve the user’s intent, but remove conversational filler.
- List/project, due date, time, recurrence, priority, tags, notes, and subtasks when explicitly requested.
- Interpret relative dates using the user’s timezone and the current date. If a date or time is ambiguous and would materially change the task, ask before creating it.
- If the user does not provide a due date, ask for the due date before creating the task. Do not create the task until the user answers; if they confirm that no due date is intended, proceed without one.
- If no list is named, use TickTick’s currently selected/default list only when that choice is obvious; otherwise ask which list to use.
- If a family or school-related task clearly belongs to Hana or Hafidz but the child is not identified, ask which child before creating it. Do not resolve the ambiguity by omitting the person-specific prefix.
- Do not add a due date, reminder, recurrence, priority, tag, or note merely because it seems useful.

## Assign labels

Apply every label that is clearly supported by the request; do not guess when the meaning is unclear. Use these meanings exactly:

- `blocked`: blocked by another to-do/task.
- `delegated`: someone else is responsible for doing it.
- `focused`: important and intended to be a focus on its due date.
- `pending`: to be done at an unspecified time.
- `routine`: a recurring/routine task.
- `waiting`: completion depends on another party.

`blocked` refers to dependency on another task, while `waiting` refers to waiting for another person or party. `delegated` may coexist with `waiting` when both are true. Do not add `pending` when the user has supplied a definite due date.

## Choose the TickTick space

If Newstore/TIDE context is active (`newstore-context`: Newstore, TIDE, Event Stream, GraphQL, SFCC, Airflow/dbt at Newstore, Dash0, Document360, gitlab.com/newstore, or tickets TDP-/NCS-/SR-/SD-/THQ-/FO-/CHEX-/CAM-), use only space `Work`. Do not list, search, read, or create items in any other space, and do not ask which space to use.

Otherwise, place the to-do in the primary space implied by its subject:

1. `Personal`: matters concerning the user alone, outside work and money.
2. `Family`: matters concerning family—Hana, Hafidz, or Listya.
3. `Work`: work-related matters.
4. `Money`: financial matters.
5. `Mission`: da'wah, community contribution, or the user’s higher-purpose mission.
6. `Social`: ignore this space; never place tasks there.
7. `Wellbeing`: Quran interaction and exercise.
8. `Hana & Hafidz study`: school-related matters for Hana or Hafidz, including school applications and registrations, school programs and events, educational workshops/classes, and direct study activities.
9. `Listya career`: Listya’s career or study progress.

Use the most specific existing space: tasks concerning Hana’s or Hafidz’s school or a school-organized educational program—including optional school workshops, school-event registrations, applications, and other school administration—go to `Hana & Hafidz study`. Use `Family` for non-school activities, family logistics, and activities not organized by a school. Listya career/study progress goes to `Listya career`, rather than the broader `Family` space. If a task genuinely spans spaces, choose the space that owns the next action; ask only when that choice is materially ambiguous.

## Prefix the task title

When a task belongs to a named context, prefix its title with the context followed by ` // `, preserving the user’s wording after the prefix. A prefix is a reusable sub-context, not necessarily a person’s name.

- Hana: `Hana // `
- Hafidz: `Hafidz // `
- Listya: `Listya // `
- Home: `Home // `

Observed prefix catalog from the current TickTick items:

- Personal: `PR`, `Shopping`, `Self-care`, `Vacation`.
- Family: `Hana`, `Hafidz`, `Home`, `Kids`, `Vacation`.
- Work: `Think strategic`, `Gio 1:1`, `Writing`.
- Money: `Tax`, `Investment`, `Finance`, `Infaq`.
- Mission: `Charity`, `Liqo 1`, `Liqo 2`, `Liqo 1 & 2`, `PPMI`, `Tadabbur Project`, `MuDe`, `P - Amerop`, `MU DE`, `Liqo Azubi`, `Writing`.
- Wellbeing: `Workout`, `Quran`.
- Listya career: `Deutschekurs`, `Training`, `Job applications`.

When a new request clearly matches one of these sub-contexts, reuse the exact existing spelling and capitalization. Prefixes can occur in more than one space when the same activity spans contexts—for example, `Writing` appears in Work and Mission, and `Vacation` appears in Personal and Family—so choose based on the task’s space rather than prefix alone. If no established prefix fits, create a concise title without a new prefix unless the user explicitly names a context or a new recurring grouping is clearly intended. Do not duplicate a prefix already present in the user’s title. For Hana, Hafidz, Listya, and other family-related tasks, apply the relevant person/context prefix even if the space is a more specific study or career space. When a task in `Hana & Hafidz study` concerns one child but the request does not identify Hana or Hafidz, ask before creating; do not invent the child or silently omit the prefix. If the task genuinely applies to both children, use no single-child prefix unless an established shared prefix exists.

## Create the item

Use the connected TickTick integration when available. Before creating a task, list the projects and inspect the undone tasks in the candidate project when needed to resolve the exact project name and an established prefix. If no direct integration is available, use the browser/app control capability with the user’s existing logged-in TickTick session. Do not ask the user to expose credentials or paste access tokens.

1. Open TickTick and navigate to the requested list/project.
2. Create one task with the parsed title and requested fields.
3. Add requested notes and subtasks without silently converting them into separate top-level tasks.
4. Before submitting, re-check the title, list, date/time, recurrence, and priority against the user’s request. If a required field is still uncertain, pause and ask a concise question.
5. After submission, verify every created task is visible in the intended list and that the key fields match. For batch creation, collect every returned task ID and read each task back with the task/project read operation; do not verify only the first item or rely solely on the batch response. If verification fails for any item, report that item and the failed field clearly instead of claiming full success.

## Response

After successful verification, confirm every created to-do item individually. For each item, include:

- Name/title.
- Description/notes, or `none` when absent.
- Tags, or `none` when absent.
- Space/list/project name.
- Due date, or `none` when absent.

Use a compact table or equivalent item-by-item format. Report the values read back from TickTick, including explicit `none` values; do not omit fields just because they were not supplied. If TickTick cannot be reached or the session is not authenticated, explain the blocker and provide the exact task details that are ready to be entered; never claim that the task was created.

Creating a task is an external state change. A clear user request to add the item authorizes that mutation, but do not create anything when the target task or destination remains materially ambiguous.
