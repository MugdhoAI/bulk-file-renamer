from pathlib import Path

import pytest

from bulk_file_renamer.renamer import (
    RenameError,
    apply_plan,
    build_name,
    build_plan,
    collect_files,
    parse_extensions,
)


def test_parse_extensions_normalizes_values() -> None:
    assert parse_extensions("jpg, .PNG, pdf") == {".jpg", ".png", ".pdf"}


def test_build_name_adds_number_prefix_and_suffix() -> None:
    path = Path("photo.jpg")

    assert build_name(path, prefix="trip_", suffix="_edited", number=7, padding=3) == (
        "trip_007_photo_edited.jpg"
    )


def test_collect_files_filters_extensions(tmp_path: Path) -> None:
    (tmp_path / "one.txt").write_text("1")
    (tmp_path / "two.JPG").write_text("2")
    (tmp_path / "three.py").write_text("3")

    assert [path.name for path in collect_files(tmp_path, extensions={".jpg"})] == ["two.JPG"]


def test_build_plan_rejects_existing_destination(tmp_path: Path) -> None:
    source = tmp_path / "photo.jpg"
    existing = tmp_path / "new_photo.jpg"
    source.write_text("source")
    existing.write_text("existing")

    with pytest.raises(RenameError, match="Destination already exists"):
        build_plan([source], prefix="new_")


def test_apply_plan_renames_files(tmp_path: Path) -> None:
    first = tmp_path / "a.txt"
    second = tmp_path / "b.txt"
    first.write_text("a")
    second.write_text("b")

    plan = build_plan([first, second], prefix="renamed_", start=1, padding=2)
    changed = apply_plan(plan)

    assert changed == 2
    assert (tmp_path / "renamed_01_a.txt").read_text() == "a"
    assert (tmp_path / "renamed_02_b.txt").read_text() == "b"


def test_apply_plan_handles_swapping_names(tmp_path: Path) -> None:
    first = tmp_path / "a.txt"
    second = tmp_path / "b.txt"
    first.write_text("A")
    second.write_text("B")

    from bulk_file_renamer.renamer import RenamePlan

    changed = apply_plan(
        [
            RenamePlan(first, second),
            RenamePlan(second, first),
        ]
    )

    assert changed == 2
    assert first.read_text() == "B"
    assert second.read_text() == "A"
