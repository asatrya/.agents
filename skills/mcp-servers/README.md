# MCP Servers

Standalone MCP (Model Context Protocol) tool servers that expose warehouse, storage, and project management operations to AI agents and orchestrators.

## Servers

| Server | Description | Primary tools |
|--------|-------------|--------------|
| **dbt-runner** | Execute dbt CLI commands | `dbt_build`, `dbt_compile`, `dbt_show`, `dbt_test`, `dbt_get_run_results` |
| **cloud-storage** | Export data, generate signed URLs | `export_bigquery_to_gcs`, `generate_signed_url`, `list_objects` |
| **jira-connector** | Jira ticket operations | `get_ticket`, `post_comment`, `get_comments`, `transition_ticket` |

## Quick start

Each server is a standalone Python project using the [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk).

### Install and run (any server)

```bash
cd mcp-servers/dbt-runner
uv sync
uv run dbt-runner-mcp
```

### Configure in Cursor / Claude Desktop

Add to your MCP settings (e.g. `~/.cursor/mcp.json` or Claude Desktop config):

```json
{
  "mcpServers": {
    "dbt-runner": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/mcp-servers/dbt-runner", "dbt-runner-mcp"]
    },
    "cloud-storage": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/mcp-servers/cloud-storage", "cloud-storage-mcp"]
    },
    "jira-connector": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/mcp-servers/jira-connector", "jira-connector-mcp"],
      "env": {
        "JIRA_BASE_URL": "https://yourcompany.atlassian.net",
        "JIRA_EMAIL": "you@company.com",
        "JIRA_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

## Environment variables

### jira-connector

| Variable | Required | Description |
|----------|----------|-------------|
| `JIRA_BASE_URL` | Yes | Jira Cloud URL (e.g. `https://yourcompany.atlassian.net`) |
| `JIRA_EMAIL` | Yes | Atlassian account email |
| `JIRA_API_TOKEN` | Yes | [API token](https://id.atlassian.com/manage-profile/security/api-tokens) |

### cloud-storage

Uses Google Cloud Application Default Credentials. Set `GOOGLE_APPLICATION_CREDENTIALS` if not using workload identity.

### dbt-runner

No special environment variables. Requires `dbt` to be available on PATH and a valid dbt profile configured.
