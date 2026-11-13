# Security Requirements

## Authentication

- Private routes require a valid authenticated identity.
- Session handling follows the chosen authentication system.

## Authorization

- Every protected resource has an ownership or role check.
- Hiding a UI button is not authorization.

## Secrets

- Real secrets never enter source control.
- Browser code receives only values intended for public use.
- Logs do not contain passwords, tokens, secret keys, or private payloads.

## Input Validation

- Validate request bodies, path values, query values, and form input.
- Reject unexpected types and invalid ranges.
- Run server-side validation even where the UI validates input.

## Database

- Use parameterized queries or the framework's safe query API.
- Grant only the database permissions the application needs.
- Review destructive operations before release.

## APIs

- Define authentication per route.
- Define authorization per route.
- Validate input before business logic.
- Return safe error messages.

## File Uploads

Check file type, size, filename, storage destination, and access permission. Do not trust a browser-provided content type by itself.

## Dependencies

- Review a new package before adding it.
- Test dependency updates before release.

## Release Security Check

- [ ] No secrets committed
- [ ] Authentication checks tested
- [ ] Authorization checks tested
- [ ] Input validation tested
- [ ] Upload rules tested
- [ ] Error responses reviewed
- [ ] Logs checked for private data
