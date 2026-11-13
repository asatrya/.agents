# Test Plan

## Test Strategy

- Unit tests: business rules and helpers
- Integration tests: API, database, and service boundaries
- End-to-end tests: critical user flows

## Authentication

### Signup

- A valid user can create an account.
- Invalid input shows a useful error.
- Duplicate identity is handled safely.

### Login

- Valid credentials create an authenticated session.
- Invalid credentials do not reveal private account details.
- Logged-out users cannot open protected pages.

## Authorization

- A user can access permitted resources.
- A user cannot access another user's private resource.
- Protected API routes reject missing or invalid identity.

## [Core Feature]

- User can create [record].
- User can read [record].
- User can update [record].
- User can delete [record].
- Invalid input is rejected.
- Missing records return the defined result.

## UI States

- Loading state works.
- Empty state works.
- Error state works.
- Success state works.

## Responsive Checks

- 375px
- 768px
- 1440px

## Accessibility Checks

- Keyboard navigation
- Visible focus
- Form labels
- Error association
- Text alternatives for meaningful images

## Release Checks

- [ ] Lint passes
- [ ] Type checking passes
- [ ] Required automated tests pass
- [ ] Production build passes
- [ ] Preview deployment passes the core end-to-end flow
