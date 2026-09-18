from pathlib import Path

from click.testing import CliRunner

from bulk_file_renamer.cli import main


def test_cli_dry_run_does_not_modify_files(tmp_path: Path, monkeypatch) -> None:
    file_path = tmp_path / "photo.jpg"
    file_path.write_text("image")

    monkeypatch.setattr("sys.argv", ["bulk-renamer", str(tmp_path), "--prefix", "trip_", "--dry-run"])

    assert main() == 0
    assert file_path.exists()
    assert not (tmp_path / "trip_photo.jpg").exists()


def test_cli_renames_matching_files(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "b.jpg").write_text("b")

    monkeypatch.setattr(
        "sys.argv",
        ["bulk-renamer", str(tmp_path), "--number", "--extensions", "txt"],
    )

    assert main() == 0
    assert (tmp_path / "1_a.txt").exists()
    assert (tmp_path / "b.jpg").exists()
