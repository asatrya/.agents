#!/usr/bin/env python3
"""Create the DevX AI-coding project starter pack without overwriting files."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create the DevX project-context starter pack."
    )
    parser.add_argument(
        "--target",
        type=Path,
        default=Path.cwd(),
        help="Repository directory to populate (default: current directory).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List planned changes without writing files.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace existing starter-pack files. Use only with explicit approval.",
    )
    return parser.parse_args()


def template_root() -> Path:
    return Path(__file__).resolve().parents[1] / "assets" / "project-template"


def template_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.is_file())


def main() -> int:
    args = parse_args()
    target = args.target.expanduser().resolve()
    source = template_root()
    files = template_files(source)

    if not source.is_dir() or not files:
        print(f"Template assets are missing: {source}", file=sys.stderr)
        return 1

    conflicts = [target / path.relative_to(source) for path in files if (target / path.relative_to(source)).exists()]
    if conflicts and not args.force:
        print("No files were changed because these starter-pack files already exist:")
        for path in conflicts:
            print(f"  - {path}")
        print("Inspect the existing files and rerun with --force only if replacement is intended.")
        return 2

    action = "Would write" if args.dry_run else "Writing"
    for path in files:
        destination = target / path.relative_to(source)
        print(f"{action} {destination}")

    for directory in (target / "docs", target / "src", target / "tests"):
        if not args.dry_run:
            directory.mkdir(parents=True, exist_ok=True)

    if args.dry_run:
        return 0

    for path in files:
        destination = target / path.relative_to(source)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

    print(f"Created {len(files)} starter-pack files under {target}")
    print("Created directories: docs/, src/, tests/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
