from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


@dataclass(frozen=True)
class RenamePlan:
    source: Path
    destination: Path


class RenameError(Exception):
    """Raised when a rename operation cannot be completed safely."""


def parse_extensions(value: str | None) -> set[str] | None:
    if not value:
        return None

    extensions = set()
    for item in value.split(","):
        extension = item.strip().lower()
        if not extension:
            continue
        if not extension.startswith("."):
            extension = "." + extension
        extensions.add(extension)

    return extensions or None


def build_name(
    path: Path,
    *,
    prefix: str = "",
    suffix: str = "",
    number: int | None = None,
    padding: int = 1,
) -> str:
    stem = path.stem
    extension = path.suffix

    if number is not None:
        number_text = str(number).zfill(max(1, padding))
        stem = f"{number_text}_{stem}"

    return f"{prefix}{stem}{suffix}{extension}"


def collect_files(
    directory: Path,
    *,
    extensions: set[str] | None = None,
    recursive: bool = False,
) -> list[Path]:
    if not directory.exists():
        raise RenameError(f"Directory does not exist: {directory}")
    if not directory.is_dir():
        raise RenameError(f"Not a directory: {directory}")

    iterator = directory.rglob("*") if recursive else directory.glob("*")
    files = [
        path
        for path in iterator
        if path.is_file()
        and (extensions is None or path.suffix.lower() in extensions)
    ]
    return sorted(files, key=lambda path: path.name.lower())


def build_plan(
    files: list[Path],
    *,
    prefix: str = "",
    suffix: str = "",
    start: int | None = None,
    padding: int = 1,
) -> list[RenamePlan]:
    plans = []
    for index, source in enumerate(files):
        number = None if start is None else start + index
        destination = source.with_name(
            build_name(
                source,
                prefix=prefix,
                suffix=suffix,
                number=number,
                padding=padding,
            )
        )
        plans.append(RenamePlan(source, destination))

    validate_plan(plans)
    return plans


def validate_plan(plans: list[RenamePlan]) -> None:
    sources = {plan.source.resolve() for plan in plans}
    destinations = [plan.destination.resolve() for plan in plans]

    if len(destinations) != len(set(destinations)):
        raise RenameError("Rename plan contains duplicate destination names.")

    for plan, destination in zip(plans, destinations):
        if destination.exists() and destination not in sources:
            raise RenameError(f"Destination already exists: {plan.destination}")


def apply_plan(plans: list[RenamePlan]) -> int:
    validate_plan(plans)
    changed = 0

    temporary: list[tuple[Path, Path]] = []
    try:
        for index, plan in enumerate(plans):
            if plan.source.resolve() == plan.destination.resolve():
                continue
            temporary_path = plan.source.with_name(
                f".bulk-renamer-tmp-{index}-{plan.source.name}"
            )
            while temporary_path.exists():
                index += 1
                temporary_path = plan.source.with_name(
                    f".bulk-renamer-tmp-{index}-{plan.source.name}"
                )
            plan.source.rename(temporary_path)
            temporary.append((temporary_path, plan.destination))
            changed += 1

        for temporary_path, destination in temporary:
            temporary_path.rename(destination)
    except Exception as exc:
        raise RenameError(f"Rename operation failed: {exc}") from exc

    return changed
