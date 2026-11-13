# Development Rules

## General

- Follow the existing language and framework conventions.
- Reuse existing components, services, types, and helpers.
- Keep functions focused and avoid duplicating business logic.
- Do not edit unrelated files.
- Check the current stack before adding a package.
- Record approved structural changes in `docs/DECISIONS.md`.

## Before Coding

1. Read the relevant project documents.
2. Read the current task and its acceptance criteria.
3. Inspect the existing implementation.
4. Search for reusable code and existing tests.
5. List the files that need to change.
6. Present a plan before a large change.

## Frontend

- Follow `docs/DESIGN.md`.
- Reuse shared UI components.
- Handle loading, empty, error, and success states where relevant.
- Keep API and database details out of presentation components.
- Preserve responsive behavior and keyboard accessibility.

## Backend

- Validate request input at the server boundary.
- Check authentication and authorization where required.
- Keep business rules in services or the existing domain layer.
- Keep database operations behind the data-access boundary.
- Return consistent, safe error shapes.

## Security

- Never commit secrets or send server-only values to browser code.
- Validate untrusted input, including uploaded files.
- Apply least privilege.
- Keep passwords, tokens, and private payloads out of logs.

## Testing

- Add or update tests for changed behavior.
- Run narrow relevant checks during development.
- Run all required checks before completion.
- Do not declare completion while required checks are failing.

## Git

- Keep commits focused.
- Use descriptive commit messages.
- Review the diff before committing.

## Completion Report

Report:

1. Files changed
2. Behavior changed
3. Checks run
4. Known issues
5. Documentation changed
