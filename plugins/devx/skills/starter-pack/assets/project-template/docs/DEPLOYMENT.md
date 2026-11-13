# Deployment Guide

## Environments

- Local: [URL or notes]
- Preview or UAT: [URL or notes]
- Production: [URL or notes]

## Release Flow

```text
Feature branch
  |
  v
Pull request
  |
  v
CI checks
  |
  v
Preview or UAT
  |
  v
QA
  |
  v
Main branch
  |
  v
Production
```

## Pre-Release Check

- [ ] Required tests pass
- [ ] Production build passes
- [ ] Environment values are present
- [ ] Database migration reviewed
- [ ] Backup requirement checked
- [ ] Security-sensitive changes reviewed
- [ ] Release notes prepared

## Database Migration

Command:

```text
[command]
```

Expected result:

[What success looks like.]

Failure action:

[What to do if the migration fails.]

## Deploy

Command or pipeline:

```text
[command or workflow name]
```

## Health Check

- Application URL: [ ]
- Health endpoint: [ ]
- Login: [ ]
- Core API: [ ]
- Database read or write: [ ]
- Background jobs: [ ]

## Rollback

Application rollback:

[Steps]

Database rollback:

[Steps or forward-fix policy]

## Post-Release

- [ ] Check application logs
- [ ] Check error tracking
- [ ] Run the core user flow
- [ ] Confirm background jobs
- [ ] Record the release in `CHANGELOG.md`
