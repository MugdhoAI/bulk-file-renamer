from __future__ import annotations

import argparse
from pathlib import Path

from .renamer import RenameError, apply_plan, build_plan, collect_files, parse_extensions


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bulk-renamer",
        description="Safely rename multiple files in a directory.",
    )
    parser.add_argument("directory", type=Path, help="Directory containing the files.")
    parser.add_argument("--prefix", default="", help="Text to add before each filename.")
    parser.add_argument("--suffix", default="", help="Text to add before the extension.")
    parser.add_argument(
        "--number",
        action="store_true",
        help="Add sequential numbers before each filename.",
    )
    parser.add_argument(
        "--start",
        type=int,
        default=1,
        help="Starting number when --number is enabled (default: 1).",
    )
    parser.add_argument(
        "--padding",
        type=int,
        default=1,
        help="Minimum number width for numbering (default: 1).",
    )
    parser.add_argument(
        "--extensions",
        help="Comma-separated extensions to include, such as jpg,png.",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Process files in subdirectories recursively.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show planned changes without renaming files.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.number and args.padding < 1:
        parser.error("--padding must be at least 1")

    try:
        extensions = parse_extensions(args.extensions)
        files = collect_files(
            args.directory,
            extensions=extensions,
            recursive=args.recursive,
        )
        if not files:
            print("No matching files found.")
            return 0

        start = args.start if args.number else None
        plan = build_plan(
            files,
            prefix=args.prefix,
            suffix=args.suffix,
            start=start,
            padding=args.padding,
        )

        for item in plan:
            if item.source != item.destination:
                print(f"{item.source.name} -> {item.destination.name}")

        if args.dry_run:
            print(f"Dry run: {len(plan)} file(s) evaluated.")
            return 0

        changed = apply_plan(plan)
        print(f"Renamed {changed} file(s).")
        return 0
    except RenameError as exc:
        parser.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
