# AGENTS.md

## Project

[Project name]

[Two or three sentences describing what this application does and who uses it.]

## Tech Stack

- Frontend: [framework and language, or not applicable]
- Backend: [framework and language, or not applicable]
- Database: [database, or not applicable]
- Authentication: [provider or method, or not applicable]
- Testing: [tools]
- Deployment: [target]

## Read Before Coding

Read the documents that apply to the task:

1. `docs/PRD.md` - product scope and acceptance boundaries
2. `docs/ARCHITECTURE.md` - system structure and ownership boundaries
3. `docs/DESIGN.md` - interface and accessibility rules, when applicable
4. `RULES.md` - coding and repository rules
5. `docs/SECURITY.md` - security requirements
6. `TASKS.md` - current work and acceptance criteria
7. `docs/MEMORY.md` - current project state
8. `docs/DECISIONS.md` - accepted technical decisions

Do not begin a large change until its relevant context is loaded.

## Important Directories

- `src/` - application code
- `tests/` - automated tests
- `docs/` - project context and operational documentation
- [path] - [purpose]

## Development Commands

Install:

```text
[command]
```

Development:

```text
[command]
```

Lint:

```text
[command]
```

Type check:

```text
[command]
```

Tests:

```text
[command]
```

Build:

```text
[command]
```

## Working Rules

- Inspect the current implementation before editing.
- Reuse existing components, services, types, and helpers.
- Keep unrelated files out of the change.
- Check the current stack before adding dependencies.
- Keep business logic outside presentation code.
- Validate untrusted input on the server boundary.
- Keep secrets out of source control and logs.
- Add or update tests for changed behavior.

## Task Flow

1. Read the task and the relevant project documents.
2. Inspect the existing implementation and search for reusable code.
3. State the planned files and change for a substantial task.
4. Implement the smallest complete change.
5. Run the required checks.
6. Review the diff and update affected documentation.

## Definition of Done

- Acceptance criteria pass.
- Required lint, type, test, and build checks pass.
- Security impact has been considered.
- No unrelated files changed.
- Documentation matches the code.
- The final diff has been reviewed.

## Do Not Change Without Approval

- [Critical configuration or folder]
- [Public API contract]
- [Database schema area]
- [Authentication flow]
- [Deployment configuration]

## Current Work

See `TASKS.md` and `docs/MEMORY.md`.
