---
name: starter-pack
description: Create a structured AI-coding project starter pack in a repository, including agent guidance, product and architecture docs, testing and security plans, operational guides, and environment templates. Use when starting a repository or adding the project-context file set; do not use for ordinary README-only edits.
---

# Starter Pack

Create the project-context files described in the [AI-Coding Project Starter Pack, Part 2](https://medium.com/activated-thinker/the-ai-coding-project-starter-pack-part-2-8060c9cd5b0f?sk=9409cdbcded3280724828aeb4861b44e). The pack is deliberately split into a short root entry point and deeper documents under `docs/` so an agent can load only the context relevant to a task.

## Files created

The generated structure is:

```text
project/
|- AGENTS.md
|- RULES.md
|- TASKS.md
|- README.md
|- CONTRIBUTING.md
|- CHANGELOG.md
|- .env.example
|- .gitignore
|- docs/
|  |- PRD.md
|  |- ARCHITECTURE.md
|  |- DESIGN.md
|  |- TEST_PLAN.md
|  |- SECURITY.md
|  |- DECISIONS.md
|  |- MEMORY.md
|  |- API.md
|  |- DATABASE.md
|  `- DEPLOYMENT.md
|- src/
`- tests/
```

`src/` and `tests/` are created as directories. The templates do not assume a language, framework, database, hosting provider, or authentication system.

## Workflow

1. Resolve the target repository. Use the repository root supplied by the user; otherwise use the current working directory. Do not guess a different project.
2. Inspect the target's existing files and identify whether any starter-pack file already exists.
3. Run the bundled generator in dry-run mode first when the target is an existing repository:

   ```bash
   python3 <this-skill>/scripts/create_starter_pack.py --target <repo> --dry-run
   ```

4. Create the pack with the generator:

   ```bash
   python3 <this-skill>/scripts/create_starter_pack.py --target <repo>
   ```

   The generator refuses to overwrite any existing pack file. If conflicts are reported, inspect them and preserve existing project truth. Use `--force` only when the user explicitly asks to replace those files.
5. Read the generated `AGENTS.md`, `README.md`, and the documents relevant to the repository. Replace placeholders with facts discovered from the codebase, package manifests, CI configuration, and deployment configuration. Do not invent commands, services, owners, URLs, tenants, or secrets.
6. Keep the documents synchronized with the code. At minimum, update `TASKS.md` and `docs/MEMORY.md` for current work; update architecture, API, database, security, test, or deployment documents when the change affects them.
7. Report the files created, any conflicts or files intentionally left unchanged, and the checks performed.

## Content rules

- `AGENTS.md` is the route map: keep it concise and link to deeper documents instead of duplicating them.
- Product scope belongs in `docs/PRD.md`; structural boundaries belong in `docs/ARCHITECTURE.md`; coding conventions belong in `RULES.md`.
- Treat `docs/SECURITY.md`, `docs/DATABASE.md`, and `docs/DEPLOYMENT.md` as project-specific checklists, not generic permission to make risky changes.
- Preserve existing project conventions and paths when they differ from the placeholders.
- `.env.example` documents variable names only. Never copy real values into it.
- Do not delete or overwrite unrelated files. The generator only writes missing pack files unless explicit replacement was requested.

## Verification

After generation, verify that every file in the structure above exists, that the files contain no accidental secrets, and that the generated Markdown links point to the generated paths. If the repository has validation commands, run the narrow relevant checks and include their results in the handoff.
