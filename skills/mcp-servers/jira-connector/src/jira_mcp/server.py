"""MCP server for Jira Cloud REST API operations.

Requires environment variables:
  JIRA_BASE_URL  – e.g. https://yourcompany.atlassian.net
  JIRA_EMAIL     – Atlassian account email
  JIRA_API_TOKEN – API token (https://id.atlassian.com/manage-profile/security/api-tokens)
"""

import os

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "jira-connector",
    description="Interact with Jira: fetch tickets, post comments, manage transitions.",
)


def _get_client() -> httpx.Client:
    """Build an authenticated httpx client for Jira Cloud REST API v3."""
    base_url = os.environ.get("JIRA_BASE_URL", "")
    email = os.environ.get("JIRA_EMAIL", "")
    token = os.environ.get("JIRA_API_TOKEN", "")

    if not all([base_url, email, token]):
        msg = "Missing required env vars: JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN"
        raise RuntimeError(msg)

    return httpx.Client(
        base_url=f"{base_url.rstrip('/')}/rest/api/3",
        auth=(email, token),
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        timeout=30.0,
    )


@mcp.tool()
def get_ticket(ticket_id: str) -> dict[str, object]:
    """Fetch a Jira issue by key (e.g. TDP-2484).

    Returns summary, description, status, assignee, labels, and custom fields.
    """
    with _get_client() as client:
        resp = client.get(f"/issue/{ticket_id}")
        resp.raise_for_status()
        data = resp.json()

    fields = data.get("fields", {})
    return {
        "key": data.get("key"),
        "summary": fields.get("summary"),
        "description": _extract_text(fields.get("description")),
        "status": fields.get("status", {}).get("name"),
        "assignee": fields.get("assignee", {}).get("displayName") if fields.get("assignee") else None,
        "labels": fields.get("labels", []),
        "created": fields.get("created"),
        "updated": fields.get("updated"),
        "priority": fields.get("priority", {}).get("name") if fields.get("priority") else None,
        "issue_type": fields.get("issuetype", {}).get("name") if fields.get("issuetype") else None,
    }


@mcp.tool()
def get_ticket_description_raw(ticket_id: str) -> dict[str, object]:
    """Fetch the full raw description (ADF) of a Jira issue.

    Useful when the description contains structured data (tables, attachments)
    that get lost in plain-text extraction.
    """
    with _get_client() as client:
        resp = client.get(f"/issue/{ticket_id}", params={"fields": "description,summary,attachment"})
        resp.raise_for_status()
        data = resp.json()

    fields = data.get("fields", {})
    return {
        "key": data.get("key"),
        "summary": fields.get("summary"),
        "description_adf": fields.get("description"),
        "attachments": [
            {"filename": a.get("filename"), "url": a.get("content"), "mime": a.get("mimeType")}
            for a in fields.get("attachment", [])
        ],
    }


@mcp.tool()
def post_comment(ticket_id: str, body: str) -> dict[str, object]:
    """Post a comment on a Jira issue.

    Body is plain text; it will be wrapped in Atlassian Document Format (ADF).
    """
    adf_body = {
        "body": {
            "version": 1,
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": body}],
                }
            ],
        }
    }

    with _get_client() as client:
        resp = client.post(f"/issue/{ticket_id}/comment", json=adf_body)
        resp.raise_for_status()
        data = resp.json()

    return {
        "comment_id": data.get("id"),
        "created": data.get("created"),
        "author": data.get("author", {}).get("displayName"),
    }


@mcp.tool()
def get_comments(ticket_id: str, max_results: int = 20) -> list[dict[str, object]]:
    """Fetch comments on a Jira issue, newest first."""
    with _get_client() as client:
        resp = client.get(
            f"/issue/{ticket_id}/comment",
            params={"maxResults": max_results, "orderBy": "-created"},
        )
        resp.raise_for_status()
        data = resp.json()

    return [
        {
            "id": c.get("id"),
            "author": c.get("author", {}).get("displayName"),
            "body": _extract_text(c.get("body")),
            "created": c.get("created"),
            "updated": c.get("updated"),
        }
        for c in data.get("comments", [])
    ]


@mcp.tool()
def get_transitions(ticket_id: str) -> list[dict[str, str]]:
    """List available status transitions for a Jira issue.

    Use this to discover valid transition IDs before calling transition_ticket.
    """
    with _get_client() as client:
        resp = client.get(f"/issue/{ticket_id}/transitions")
        resp.raise_for_status()
        data = resp.json()

    return [
        {"id": t["id"], "name": t["name"], "to_status": t.get("to", {}).get("name", "")}
        for t in data.get("transitions", [])
    ]


@mcp.tool()
def transition_ticket(ticket_id: str, transition_id: str, comment: str | None = None) -> dict[str, str]:
    """Transition a Jira issue to a new status.

    Use get_transitions first to discover valid transition IDs.
    Optionally add a comment with the transition.
    """
    payload: dict[str, object] = {"transition": {"id": transition_id}}

    if comment:
        payload["update"] = {
            "comment": [
                {
                    "add": {
                        "body": {
                            "version": 1,
                            "type": "doc",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": comment}],
                                }
                            ],
                        }
                    }
                }
            ]
        }

    with _get_client() as client:
        resp = client.post(f"/issue/{ticket_id}/transitions", json=payload)
        resp.raise_for_status()

    return {"status": "ok", "ticket": ticket_id, "transition_id": transition_id}


def _extract_text(adf: dict[str, object] | None) -> str:
    """Recursively extract plain text from Atlassian Document Format."""
    if adf is None:
        return ""
    if isinstance(adf, str):
        return adf

    text_parts: list[str] = []
    if "text" in adf:
        text_parts.append(str(adf["text"]))
    for child in adf.get("content", []):  # type: ignore[union-attr]
        text_parts.append(_extract_text(child))  # type: ignore[arg-type]
    return " ".join(text_parts).strip()


def main() -> None:
    """Run the MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
