from pathlib import Path

import pandas as pd

from solio_calibrate.solver.adapter import (
    calculate_effective_horizon,
    format_confirmation_summary,
    generate_fplteam_link,
)


def test_calculate_effective_horizon_default():
    # next_gw = 7, default horizon = 10 -> covers GW 7..16
    horizon, expanded = calculate_effective_horizon(
        base_horizon=10,
        next_gw=7,
        use_fh=[],
        use_wc=[],
        use_bb=[],
        use_tc=[],
    )
    assert horizon == 10
    assert expanded is False


def test_calculate_effective_horizon_auto_expands_for_chip():
    # next_gw = 7, FH in GW 19 -> needs horizon 19 - 7 + 1 = 13
    horizon, expanded = calculate_effective_horizon(
        base_horizon=10,
        next_gw=7,
        use_fh=[19],
        use_wc=[],
        use_bb=[],
        use_tc=[],
    )
    assert horizon == 13
    assert expanded is True


def test_calculate_effective_horizon_chip_within_horizon():
    # next_gw = 7, FH in GW 10 -> 10 - 7 + 1 = 4 <= 10 -> no expansion
    horizon, expanded = calculate_effective_horizon(
        base_horizon=10,
        next_gw=7,
        use_fh=[10],
        use_wc=[],
        use_bb=[],
        use_tc=[],
    )
    assert horizon == 10
    assert expanded is False


def test_format_confirmation_summary():
    summary = format_confirmation_summary(
        team_id=12345,
        next_gw=7,
        horizon=10,
        expanded=False,
        chips={"fh": [19]},
        projections_path=Path("data/projections/solio_projections.csv"),
        bank=0.5,
        free_transfers=2,
    )
    assert "12345" in summary
    assert "GW 7" in summary
    assert "10 Gameweeks" in summary
    assert "solio_projections.csv" in summary
    assert "£0.5m" in summary
    assert "Free Transfers:     2" in summary


def test_generate_fplteam_link_format():
    # Create minimal picks dataframe matching solver structure
    picks = pd.DataFrame([
        {"week": 7, "id": 1, "lineup": 1.0, "bench": 0.0, "captain": 0.0, "vicecaptain": 0.0, "chip": "", "transfer_out": 0.0, "transfer_in": 0.0, "type": 1},
        {"week": 7, "id": 4, "lineup": 1.0, "bench": 0.0, "captain": 0.0, "vicecaptain": 0.0, "chip": "", "transfer_out": 0.0, "transfer_in": 0.0, "type": 2},
        {"week": 7, "id": 12, "lineup": 1.0, "bench": 0.0, "captain": 1.0, "vicecaptain": 0.0, "chip": "", "transfer_out": 0.0, "transfer_in": 0.0, "type": 3},
        {"week": 7, "id": 411, "lineup": 1.0, "bench": 0.0, "captain": 0.0, "vicecaptain": 1.0, "chip": "", "transfer_out": 0.0, "transfer_in": 0.0, "type": 4},
        {"week": 7, "id": 2, "lineup": 0.0, "bench": 1.0, "captain": 0.0, "vicecaptain": 0.0, "chip": "", "transfer_out": 0.0, "transfer_in": 0.0, "type": 1},
    ])
    solution = {"iter": 0, "picks": picks, "score": 65.4}
    link = generate_fplteam_link([solution], team_id=9999)
    assert link.startswith("https://fpl.team/plan/9999/?")
    assert "lineup7=1,4,12,411" in link
    assert "cap7=12" in link
    assert "vcap7=411" in link
