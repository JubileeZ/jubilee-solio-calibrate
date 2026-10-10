from pathlib import Path

import pandas as pd
import pytest

from solio_calibrate.io import load_solio_team_strengths, save_solio_team_strengths


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
