from pathlib import Path

import pytest

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
    assert "blend_weight" in payload
    assert "team_weights" in payload
    assert "ARS" in payload["team_weights"]
    assert "provisional_matches" in payload
    assert "planner_rules_reminder" in payload



def test_cli_ingests_and_archives_raw_and_output(tmp_path: Path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    orig_raw = raw_dir / "team_strengths_base.csv"
    orig_raw.write_text("Team,Goals,Goals Conceded\nARS,1.900,0.800\n", encoding="utf-8")

    output_dir = tmp_path / "output"

    # Explicit input from browser download
    new_input = tmp_path / "team_strengths (1).csv"
    new_input.write_text("Team,Goals,Goals Conceded\nARS,2.100,0.900\n", encoding="utf-8")

    exit_code = main_cli([
        "--input", str(new_input),
        "--raw-dir", str(raw_dir),
        "--output-dir", str(output_dir),
        "--weight", "0.0",
        "--offline",
    ])

    assert exit_code == 0

    # Raw was promoted and old archived
    assert orig_raw.read_text(encoding="utf-8") == "Team,Goals,Goals Conceded\nARS,2.100,0.900\n"
    raw_archives = list((raw_dir / "archive").glob("team_strengths_base_*.csv"))
    assert len(raw_archives) == 1
    assert raw_archives[0].read_text(encoding="utf-8") == "Team,Goals,Goals Conceded\nARS,1.900,0.800\n"

    # Output was written to canonical latest and archived
    latest_out = output_dir / "team_strengths_calibrated.csv"
    assert latest_out.is_file()
    out_archives = list((output_dir / "archive").glob("team_strengths_calibrated_*.csv"))
    assert len(out_archives) == 1
    assert out_archives[0].is_file()
    assert latest_out.read_text(encoding="utf-8") == out_archives[0].read_text(encoding="utf-8")


def test_cli_no_ingest_flag(tmp_path: Path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    orig_raw = raw_dir / "team_strengths_base.csv"
    orig_raw.write_text("Team,Goals,Goals Conceded\nARS,1.900,0.800\n", encoding="utf-8")

    output_dir = tmp_path / "output"
    new_input = tmp_path / "custom_input.csv"
    new_input.write_text("Team,Goals,Goals Conceded\nARS,2.200,0.700\n", encoding="utf-8")

    exit_code = main_cli([
        "--input", str(new_input),
        "--raw-dir", str(raw_dir),
        "--output-dir", str(output_dir),
        "--no-ingest",
        "--weight", "0.0",
        "--offline",
    ])

    assert exit_code == 0
    # Raw directory must remain untouched
    assert orig_raw.read_text(encoding="utf-8") == "Team,Goals,Goals Conceded\nARS,1.900,0.800\n"
    assert not (raw_dir / "archive").exists()


def test_cli_random_filename_ingestion(tmp_path: Path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    orig_raw = raw_dir / "team_strengths_base.csv"
    orig_raw.write_text("Team,Goals,Goals Conceded\nARS,1.900,0.800\n", encoding="utf-8")

    output_dir = tmp_path / "output"

    # Completely arbitrary filename from user download
    random_input = tmp_path / "my_custom_solio_plan_gw6_draft.csv"
    random_input.write_text("Team,Goals,Goals Conceded\nARS,2.300,0.850\n", encoding="utf-8")

    exit_code = main_cli([
        "--input", str(random_input),
        "--raw-dir", str(raw_dir),
        "--output-dir", str(output_dir),
        "--weight", "0.0",
        "--offline",
    ])

    assert exit_code == 0

    # 1. Active file in raw is canonically team_strengths_base.csv, not the random name
    assert orig_raw.is_file()
    assert not (raw_dir / "my_custom_solio_plan_gw6_draft.csv").exists()
    assert orig_raw.read_text(encoding="utf-8") == "Team,Goals,Goals Conceded\nARS,2.300,0.850\n"

    # 2. Archive filename in raw is team_strengths_base_<timestamp>.csv
    raw_archives = list((raw_dir / "archive").glob("team_strengths_base_*.csv"))
    assert len(raw_archives) == 1
    assert raw_archives[0].read_text(encoding="utf-8") == "Team,Goals,Goals Conceded\nARS,1.900,0.800\n"

    # 3. Output file is always canonical team_strengths_calibrated.csv, not the random name
    assert (output_dir / "team_strengths_calibrated.csv").is_file()
    assert not (output_dir / "my_custom_solio_plan_gw6_draft.csv").exists()

    # 4. Output archive is always team_strengths_calibrated_<timestamp>.csv
    out_archives = list((output_dir / "archive").glob("team_strengths_calibrated_*.csv"))
    assert len(out_archives) == 1


def test_cli_auto_weight_per_team(tmp_path: Path, capsys):
    import json

    in_file = tmp_path / "teams_in.csv"
    in_file.write_text(
        "Team,Goals,Goals Conceded\nARS,2.000,1.000\nAVL,2.000,1.000\nLIV,2.000,1.000\n",
        encoding="utf-8",
    )
    out_file = tmp_path / "teams_out.csv"

    # In offline mode with cached GW8 fixtures:
    # ARS and AVL have 8 matches (provisional GW8) -> weight ~ 8/19 = 0.4211
    # LIV has 7 matches (GW8 not yet played) -> weight ~ 7/19 = 0.3684
    exit_code = main_cli([
        "--input", str(in_file),
        "--output", str(out_file),
        "--auto-weight",
        "--offline",
        "--json",
    ])

    assert exit_code == 0
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    team_weights = payload["team_weights"]

    assert "ARS" in team_weights
    assert "AVL" in team_weights
    assert "LIV" in team_weights
    assert team_weights["LIV"] < team_weights["ARS"]
    assert team_weights["ARS"] == pytest.approx(round(8 / 19.0, 4), abs=1e-3)
    assert team_weights["AVL"] == pytest.approx(round(8 / 19.0, 4), abs=1e-3)
    assert team_weights["LIV"] == pytest.approx(round(7 / 19.0, 4), abs=1e-3)


def test_cli_terminal_summary_includes_planner_rules_reminder(tmp_path: Path, capsys):
    in_file = tmp_path / "teams_in.csv"
    in_file.write_text("Team,Goals,Goals Conceded\nARS,2.000,1.000\n", encoding="utf-8")
    out_file = tmp_path / "teams_out.csv"

    exit_code = main_cli([
        "--input", str(in_file),
        "--output", str(out_file),
        "--weight", "0.0",
        "--offline",
    ])

    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Solio Planner Rules: Remember to configure variance-control rules in Solio web planner before optimizing." in captured.out




