from pathlib import Path
from unittest.mock import patch

import pytest

from solio_calibrate.solve_cli import main


def test_solve_cli_help(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "solio-solve" in captured.out
    assert "--team-id" in captured.out
    assert "--horizon" in captured.out


@patch("solio_calibrate.solve_cli.prepare_solve_context")
@patch("solio_calibrate.solve_cli.solve_squad")
def test_solve_cli_invocation_with_defaults(mock_solve_squad, mock_prep_ctx, capsys, tmp_path: Path):
    proj_file = tmp_path / "solio.csv"
    proj_file.write_text("Pos,ID,Name,BV,SV,Team,7_xMins,7_Pts\nG,1,Raya,6.1,6.1,Arsenal,90,4.5\n", encoding="utf-8")

    mock_prep_ctx.return_value = {
        "summary": "MOCK SETTINGS REVIEW",
        "options": {},
        "my_data": {},
        "next_gw": 7,
        "effective_horizon": 8,
        "expanded": False,
        "bank": 1.5,
        "free_transfers": 2,
    }

    mock_solve_squad.return_value = {
        "summary": "MOCK SETTINGS REVIEW",
        "table": "| GW | Transfers |\n| GW 7 | None |",
        "fplteam_url": "https://fpl.team/plan/12345/?lineup7=1",
        "plan_file": tmp_path / "plan.csv",
        "score": 75.2,
    }

    exit_code = main(
        [
            "--team-id", "12345",
            "--projections", str(proj_file),
            "--horizon", "8",
            "-y",
        ],
        projections_dir=tmp_path / "projections",
    )
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "MOCK SETTINGS REVIEW" in captured.out
    assert "https://fpl.team/plan/12345/?lineup7=1" in captured.out
    assert "GW 7" in captured.out
    mock_solve_squad.assert_called_once()
    kwargs = mock_solve_squad.call_args.kwargs
    assert kwargs["team_id"] == 12345
    assert kwargs["horizon"] == 8


@patch("solio_calibrate.solve_cli.input", return_value="n")
@patch("solio_calibrate.solve_cli.prepare_solve_context")
@patch("solio_calibrate.solve_cli.solve_squad")
def test_solve_cli_confirmation_aborted(mock_solve_squad, mock_prep_ctx, mock_input, capsys, tmp_path: Path):
    proj_file = tmp_path / "solio.csv"
    proj_file.write_text("Pos,ID,Name,BV,SV,Team,7_xMins,7_Pts\nG,1,Raya,6.1,6.1,Arsenal,90,4.5\n", encoding="utf-8")

    mock_prep_ctx.return_value = {
        "summary": "MOCK SETTINGS REVIEW - BANK £1.5m",
        "options": {},
        "my_data": {},
        "next_gw": 7,
        "effective_horizon": 10,
        "expanded": False,
        "bank": 1.5,
        "free_transfers": 2,
    }

    # If user cancels confirmation, solver is not called and code exits cleanly with 0
    exit_code = main(
        [
            "--team-id", "12345",
            "--projections", str(proj_file),
        ],
        projections_dir=tmp_path / "projections",
    )
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "MOCK SETTINGS REVIEW - BANK £1.5m" in captured.out
    assert "Solve cancelled by user." in captured.out
    mock_solve_squad.assert_not_called()
