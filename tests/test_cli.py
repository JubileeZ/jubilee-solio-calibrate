from pathlib import Path

from solio_calibrate.cli import main_cli
from solio_calibrate.io import load_solio_team_strengths


def test_cli_execution_with_offline_cache(tmp_path: Path):
    in_file = tmp_path / "teams_in.csv"
    in_file.write_text("Team,Goals,Goals Conceded\nARS,2.000,1.000\n", encoding="utf-8")

    out_file = tmp_path / "teams_out.csv"

    # Run CLI in offline mode
    exit_code = main_cli([
        "--input", str(in_file),
        "--output", str(out_file),
        "--weight", "0.0",
        "--attack-scale", "1.10",
        "--offline",
    ])

    assert exit_code == 0
    assert out_file.is_file()

    out_df = load_solio_team_strengths(out_file)
    assert len(out_df) == 1
    assert out_df.iloc[0]["Team"] == "ARS"
    assert out_df.iloc[0]["Goals"] == 2.200
    assert out_df.iloc[0]["Goals Conceded"] == 1.000


def test_cli_auto_weight_zero_gw_fallback(tmp_path: Path):
    in_file = tmp_path / "teams_in.csv"
    in_file.write_text("Team,Goals,Goals Conceded\nARS,1.972,0.875\n", encoding="utf-8")
    out_file = tmp_path / "teams_out.csv"

    # Pre-season / unplayed (no finished fixtures)
    exit_code = main_cli([
        "--input", str(in_file),
        "--output", str(out_file),
        "--auto-weight",
        "--offline",
        "--max-gameweek", "0",
    ])

    assert exit_code == 0
    out_df = load_solio_team_strengths(out_file)
    # Must preserve exact 100% Solio values
    assert out_df.iloc[0]["Goals"] == 1.972
    assert out_df.iloc[0]["Goals Conceded"] == 0.875


def test_cli_json_output(tmp_path: Path, capsys):
    import json

    in_file = tmp_path / "teams_in.csv"
    in_file.write_text("Team,Goals,Goals Conceded\nARS,1.972,0.875\n", encoding="utf-8")
    out_file = tmp_path / "teams_out.csv"

    exit_code = main_cli([
        "--input", str(in_file),
        "--output", str(out_file),
        "--offline",
        "--weight", "0.0",
        "--json",
    ])

    assert exit_code == 0
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["calibrated_file"] == str(out_file.resolve())
    assert payload["teams_calibrated"] == 1
    assert "home_factor_pct" in payload
