from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
import pytest

from solio_calibrate.io import (
    format_archive_filename,
    ingest_and_archive_raw_input,
    load_solio_team_strengths,
    save_and_archive_calibrated_strengths,
    save_solio_team_strengths,
)


def test_load_valid_solio_csv(tmp_path: Path):
    content = "Team,Goals,Goals Conceded\nARS,1.972,0.875\nAVL,1.379,1.542\n"
    csv_file = tmp_path / "teams.csv"
    csv_file.write_text(content, encoding="utf-8")

    df = load_solio_team_strengths(csv_file)
    assert len(df) == 2
    assert list(df.columns) == ["Team", "Goals", "Goals Conceded"]
    assert df.iloc[0]["Team"] == "ARS"
    assert df.iloc[0]["Goals"] == pytest.approx(1.972)
    assert df.iloc[0]["Goals Conceded"] == pytest.approx(0.875)


def test_load_missing_columns(tmp_path: Path):
    content = "Team,Goals\nARS,1.972\n"
    csv_file = tmp_path / "invalid.csv"
    csv_file.write_text(content, encoding="utf-8")

    with pytest.raises(ValueError, match="Missing required columns"):
        load_solio_team_strengths(csv_file)


def test_load_invalid_team_code(tmp_path: Path):
    content = "Team,Goals,Goals Conceded\nINVALID,1.972,0.875\n"
    csv_file = tmp_path / "invalid_team.csv"
    csv_file.write_text(content, encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid team code"):
        load_solio_team_strengths(csv_file)


def test_save_solio_csv_formatting(tmp_path: Path):
    df = pd.DataFrame([
        {"Team": "ARS", "Goals": 1.972499, "Goals Conceded": 0.8751},
        {"Team": "MCI", "Goals": 2.1, "Goals Conceded": 1.0},
    ])
    out_file = tmp_path / "out.csv"
    save_solio_team_strengths(df, out_file)

    saved_text = out_file.read_text(encoding="utf-8")
    lines = [line.strip() for line in saved_text.strip().splitlines()]
    assert lines[0] == "Team,Goals,Goals Conceded"
    assert lines[1] == "ARS,1.972,0.875"
    assert lines[2] == "MCI,2.100,1.000"


def test_save_refuses_to_overwrite_raw(tmp_path: Path):
    raw_file = tmp_path / "data" / "raw" / "team_strengths.csv"
    raw_file.parent.mkdir(parents=True, exist_ok=True)
    raw_file.write_text("dummy", encoding="utf-8")

    df = pd.DataFrame([{"Team": "ARS", "Goals": 2.0, "Goals Conceded": 1.0}])
    with pytest.raises(PermissionError, match="Refusing to overwrite"):
        save_solio_team_strengths(df, raw_file)


def test_format_archive_filename():
    dt = datetime(2026, 10, 11, 14, 30, 45, tzinfo=UTC)
    fname_base = format_archive_filename("team_strengths_base", dt)
    assert fname_base == "team_strengths_base_2026-10-11_14-30-45.csv"

    fname_cal = format_archive_filename("team_strengths_calibrated", dt)
    assert fname_cal == "team_strengths_calibrated_2026-10-11_14-30-45.csv"


def test_ingest_and_archive_raw_input(tmp_path: Path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    active_raw = raw_dir / "team_strengths_base.csv"
    active_raw.write_text("Team,Goals,Goals Conceded\nARS,1.900,0.800\n", encoding="utf-8")

    # 1. New file with different content (e.g. downloaded browser file)
    new_download = tmp_path / "team_strengths (1).csv"
    new_download.write_text("Team,Goals,Goals Conceded\nARS,2.100,0.900\n", encoding="utf-8")

    ts = datetime(2026, 10, 11, 12, 0, 0, tzinfo=UTC)
    active_res, archived_res = ingest_and_archive_raw_input(new_download, raw_dir=raw_dir, now=ts)

    assert active_res == active_raw
    assert active_raw.read_text(encoding="utf-8") == "Team,Goals,Goals Conceded\nARS,2.100,0.900\n"
    assert archived_res == raw_dir / "archive" / "team_strengths_base_2026-10-11_12-00-00.csv"
    assert archived_res.read_text(encoding="utf-8") == "Team,Goals,Goals Conceded\nARS,1.900,0.800\n"

    # 2. Ingesting identical file should deduplicate (no duplicate archive created)
    duplicate_download = tmp_path / "team_strengths (2).csv"
    duplicate_download.write_text("Team,Goals,Goals Conceded\nARS,2.100,0.900\n", encoding="utf-8")

    ts2 = datetime(2026, 10, 11, 12, 5, 0, tzinfo=UTC)
    active_res2, archived_res2 = ingest_and_archive_raw_input(duplicate_download, raw_dir=raw_dir, now=ts2)
    assert active_res2 == active_raw
    assert archived_res2 is None
    # Archive folder should still only contain the single initial archive
    archive_files = list((raw_dir / "archive").glob("*.csv"))
    assert len(archive_files) == 1

    # 3. Supplying the active file itself should do nothing
    active_res3, archived_res3 = ingest_and_archive_raw_input(active_raw, raw_dir=raw_dir)
    assert active_res3 == active_raw
    assert archived_res3 is None


def test_save_and_archive_calibrated_strengths(tmp_path: Path):
    output_dir = tmp_path / "output"
    df = pd.DataFrame([{"Team": "ARS", "Goals": 1.88, "Goals Conceded": 0.81}])
    ts = datetime(2026, 10, 11, 13, 0, 0, tzinfo=UTC)

    # 1. Default save writes to canonical latest + archives copy
    out_file, arch_file = save_and_archive_calibrated_strengths(
        df, output_path=None, output_dir=output_dir, now=ts
    )
    assert out_file == output_dir / "team_strengths_calibrated.csv"
    assert arch_file == output_dir / "archive" / "team_strengths_calibrated_2026-10-11_13-00-00.csv"
    assert out_file.is_file()
    assert arch_file.is_file()
    assert out_file.read_text(encoding="utf-8") == arch_file.read_text(encoding="utf-8")

    # 2. Explicit output path bypasses canonical latest and archive
    custom_target = tmp_path / "custom" / "custom_out.csv"
    out_override, arch_override = save_and_archive_calibrated_strengths(
        df, output_path=custom_target, output_dir=output_dir
    )
    assert out_override == custom_target
    assert arch_override is None
    assert custom_target.is_file()

