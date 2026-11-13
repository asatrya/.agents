# Database Guide

## Database

[PostgreSQL, SQL Server, MySQL, or other]

## Schema Ownership

- [schema or module]: [owner or feature]
- [schema or module]: [owner or feature]

## Naming

- Tables: [rule]
- Columns: [rule]
- Primary keys: [rule]
- Foreign keys: [rule]
- Indexes: [rule]

## Migration Rules

- Create a migration for every schema change.
- Do not edit an applied production migration.
- Keep migrations small and related to one change.
- Review data backfills separately from schema changes.
- Test migrations against a non-production database first.
- Record manual release steps in `docs/DEPLOYMENT.md`.

## Table Template

### [table_name]

Purpose:

[What this table stores.]

Primary key: [id]

Relationships:

- [column] -> [table.column]

Important indexes:

- [index]

Sensitive fields: [field or none]

Retention: [rule or not applicable]

## Query Rules

- Use parameterized queries or the project's safe data library.
- Avoid `SELECT *` in stable API paths.
- Review queries that scan large tables.
- Add an index only after checking the query pattern and write cost.

## Backup and Restore

- Backup method: [ ]
- Restore test frequency: [ ]
- Recovery owner: [ ]
