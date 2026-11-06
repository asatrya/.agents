"""MCP server that exposes dbt CLI operations as tools.

Provides: build, compile, show, run status, and log retrieval.
Designed to run against a local dbt project directory.
"""

import json
import subprocess
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "dbt-runner",
    description="Run dbt commands, monitor builds, and retrieve artifacts.",
)

DEFAULT_PROJECT_DIR = "."
DEFAULT_PROFILES_DIR: str | None = None


def _run_dbt(
    args: list[str],
    project_dir: str = DEFAULT_PROJECT_DIR,
    profiles_dir: str | None = DEFAULT_PROFILES_DIR,
) -> dict[str, object]:
    """Execute a dbt CLI command and capture output."""
    cmd = ["dbt", "--log-format", "json"]
    if project_dir:
        cmd.extend(["--project-dir", project_dir])
    if profiles_dir:
        cmd.extend(["--profiles-dir", profiles_dir])
    cmd.extend(args)

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

    return {
        "command": " ".join(cmd),
        "exit_code": result.returncode,
        "stdout": result.stdout[-5000:] if len(result.stdout) > 5000 else result.stdout,
        "stderr": result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr,
    }


@mcp.tool()
def dbt_build(
    selector: str,
    project_dir: str = DEFAULT_PROJECT_DIR,
    profiles_dir: str | None = DEFAULT_PROFILES_DIR,
    full_refresh: bool = False,
    target: str | None = None,
) -> dict[str, object]:
    """Run `dbt build` for the given selector (e.g. path:models/ad_hoc/TDP-2484/*).

    Returns the command output including exit code, stdout, and stderr.
    """
    args = ["build", "--select", selector]
    if full_refresh:
        args.append("--full-refresh")
    if target:
        args.extend(["--target", target])
    return _run_dbt(args, project_dir, profiles_dir)


@mcp.tool()
def dbt_compile(
    selector: str | None = None,
    project_dir: str = DEFAULT_PROJECT_DIR,
    profiles_dir: str | None = DEFAULT_PROFILES_DIR,
) -> dict[str, object]:
    """Run `dbt compile` to parse the project and generate compiled SQL.

    Optionally filter to a specific selector. Produces/updates manifest.json.
    """
    args = ["compile"]
    if selector:
        args.extend(["--select", selector])
    return _run_dbt(args, project_dir, profiles_dir)


@mcp.tool()
def dbt_show(
    selector: str,
    limit: int = 20,
    project_dir: str = DEFAULT_PROJECT_DIR,
    profiles_dir: str | None = DEFAULT_PROFILES_DIR,
) -> dict[str, object]:
    """Run `dbt show` to preview query results without materializing.

    Returns a sample of rows from the selected model.
    """
    args = ["show", "--select", selector, "--limit", str(limit)]
    return _run_dbt(args, project_dir, profiles_dir)


@mcp.tool()
def dbt_test(
    selector: str,
    project_dir: str = DEFAULT_PROJECT_DIR,
    profiles_dir: str | None = DEFAULT_PROFILES_DIR,
) -> dict[str, object]:
    """Run `dbt test` for the given selector.

    Returns test results including pass/fail status.
    """
    args = ["test", "--select", selector]
    return _run_dbt(args, project_dir, profiles_dir)


@mcp.tool()
def dbt_get_compiled_sql(
    model_name: str,
    project_dir: str = DEFAULT_PROJECT_DIR,
) -> dict[str, str | None]:
    """Read the compiled SQL for a given model from the target directory.

    Useful for reviewing what dbt will actually execute.
    """
    target_dir = Path(project_dir) / "target" / "compiled"
    matches: list[Path] = list(target_dir.rglob(f"{model_name}.sql"))

    if not matches:
        return {"model": model_name, "compiled_sql": None, "error": "Compiled SQL not found. Run dbt compile first."}

    compiled = matches[0].read_text()
    return {"model": model_name, "path": str(matches[0]), "compiled_sql": compiled}


@mcp.tool()
def dbt_get_run_results(
    project_dir: str = DEFAULT_PROJECT_DIR,
) -> dict[str, object]:
    """Read the latest run_results.json from the target directory.

    Contains status, timing, and row counts for each node in the last run.
    """
    results_path = Path(project_dir) / "target" / "run_results.json"
    if not results_path.exists():
        return {"error": "run_results.json not found. Run dbt build first."}

    data = json.loads(results_path.read_text())

    summary = []
    for result in data.get("results", []):
        summary.append({
            "unique_id": result.get("unique_id"),
            "status": result.get("status"),
            "execution_time": result.get("execution_time"),
            "rows_affected": result.get("adapter_response", {}).get("rows_affected"),
            "message": result.get("message"),
        })

    return {
        "elapsed_time": data.get("elapsed_time"),
        "generated_at": data.get("metadata", {}).get("generated_at"),
        "results": summary,
    }


@mcp.tool()
def dbt_get_logs(
    project_dir: str = DEFAULT_PROJECT_DIR,
    tail_lines: int = 100,
) -> dict[str, str]:
    """Read the tail of dbt.log for debugging build failures."""
    log_path = Path(project_dir) / "logs" / "dbt.log"
    if not log_path.exists():
        return {"error": "dbt.log not found."}

    lines = log_path.read_text().splitlines()
    return {"log": "\n".join(lines[-tail_lines:])}


def main() -> None:
    """Run the MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
