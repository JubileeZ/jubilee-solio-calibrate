import pandas as pd
import pytest

from solio_calibrate.calibrate import (
    CalibrationConfig,
    calibrate_team_strengths,
)


def test_calibrate_zero_weight_returns_base():
    df = pd.DataFrame([
        {"Team": "ARS", "Goals": 1.972, "Goals Conceded": 0.875},
        {"Team": "AVL", "Goals": 1.379, "Goals Conceded": 1.542},
    ])
    fpl_stats = {
        "ARS": {
            "matches_played": 5,
            "goals_per_match": 2.6,
            "conceded_per_match": 0.4,
            "recent_matches": 3,
            "recent_goals_per_match": 3.0,
            "recent_conceded_per_match": 0.333,
        },
        "AVL": {
            "matches_played": 5,
            "goals_per_match": 1.0,
            "conceded_per_match": 2.0,
            "recent_matches": 3,
            "recent_goals_per_match": 0.667,
            "recent_conceded_per_match": 2.333,
        },
    }

    config = CalibrationConfig(weight=0.0)
    result = calibrate_team_strengths(df, fpl_stats, config=config)

    assert result.iloc[0]["Goals"] == pytest.approx(1.972, abs=1e-3)
    assert result.iloc[0]["Goals Conceded"] == pytest.approx(0.875, abs=1e-3)


def test_calibrate_blend_fpl_performance():
    df = pd.DataFrame([{"Team": "ARS", "Goals": 2.0, "Goals Conceded": 1.0}])
    fpl_stats = {
        "ARS": {
            "matches_played": 10,
            "goals_per_match": 3.0,
            "conceded_per_match": 0.5,
            "recent_matches": 5,
            "recent_goals_per_match": 3.0,
            "recent_conceded_per_match": 0.5,
        }
    }

    # 50% blend: Goals = 0.5 * 2.0 + 0.5 * 3.0 = 2.5; Conceded = 0.5 * 1.0 + 0.5 * 0.5 = 0.75
    config = CalibrationConfig(weight=0.5, recent_weight=0.0)
    result = calibrate_team_strengths(df, fpl_stats, config=config)

    assert result.iloc[0]["Goals"] == pytest.approx(2.5, abs=1e-3)
    assert result.iloc[0]["Goals Conceded"] == pytest.approx(0.75, abs=1e-3)


def test_calibrate_per_team_weights():
    df = pd.DataFrame([
        {"Team": "ARS", "Goals": 2.0, "Goals Conceded": 1.0},
        {"Team": "AVL", "Goals": 2.0, "Goals Conceded": 1.0},
    ])
    fpl_stats = {
        "ARS": {
            "matches_played": 6,
            "empirical_attack_per_match": 3.0,
            "empirical_defense_per_match": 0.5,
        },
        "AVL": {
            "matches_played": 7,
            "empirical_attack_per_match": 3.0,
            "empirical_defense_per_match": 0.5,
        },
    }

    # ARS uses 6/19 = 0.3158; AVL uses 7/19 = 0.3684
    team_weights = {"ARS": 0.3158, "AVL": 0.3684}
    config = CalibrationConfig(weight=0.50, team_weights=team_weights)
    result = calibrate_team_strengths(df, fpl_stats, config=config)

    # ARS: (1 - 0.3158) * 2.0 + 0.3158 * 3.0 = 1.3684 + 0.9474 = 2.3158 -> 2.316
    assert result.loc[result["Team"] == "ARS", "Goals"].values[0] == pytest.approx(2.316, abs=1e-3)
    # AVL: (1 - 0.3684) * 2.0 + 0.3684 * 3.0 = 1.2632 + 1.1052 = 2.3684 -> 2.368
    assert result.loc[result["Team"] == "AVL", "Goals"].values[0] == pytest.approx(2.368, abs=1e-3)


def test_calibrate_with_team_multipliers():
    df = pd.DataFrame([{"Team": "ARS", "Goals": 2.0, "Goals Conceded": 1.0}])
    fpl_stats = {}

    config = CalibrationConfig(
        weight=0.0,
        team_multipliers={"ARS": {"goals": 1.10, "conceded": 0.90}},
    )
    result = calibrate_team_strengths(df, fpl_stats, config=config)

    assert result.iloc[0]["Goals"] == pytest.approx(2.20, abs=1e-3)
    assert result.iloc[0]["Goals Conceded"] == pytest.approx(0.90, abs=1e-3)


def test_calibrate_global_scaling():
    df = pd.DataFrame([{"Team": "ARS", "Goals": 2.0, "Goals Conceded": 1.0}])
    fpl_stats = {}

    config = CalibrationConfig(
        weight=0.0,
        attack_scale=1.05,
        defense_scale=0.95,
    )
    result = calibrate_team_strengths(df, fpl_stats, config=config)

    assert result.iloc[0]["Goals"] == pytest.approx(2.10, abs=1e-3)
    assert result.iloc[0]["Goals Conceded"] == pytest.approx(0.95, abs=1e-3)


def test_compute_auto_weight_progression():
    from solio_calibrate.calibrate import compute_auto_weight

    assert compute_auto_weight(0) == 0.0  # Preseason / unplayed
    assert compute_auto_weight(-1) == 0.0
    assert compute_auto_weight(5) == pytest.approx(5 / 19.0, abs=1e-3)
    assert compute_auto_weight(10) == pytest.approx(10 / 19.0, abs=1e-3)
    assert compute_auto_weight(19) == 1.0
    assert compute_auto_weight(20) == 1.0
    assert compute_auto_weight(38) == 1.0


def test_calibrate_zero_matches_returns_base_regardless_of_weight():
    # Pre-season or unplayed GW invariant
    df = pd.DataFrame([{"Team": "ARS", "Goals": 1.972, "Goals Conceded": 0.875}])
    fpl_stats = {"ARS": {"matches_played": 0, "goals_per_match": 0.0, "conceded_per_match": 0.0}}

    config = CalibrationConfig(weight=0.70)
    result = calibrate_team_strengths(df, fpl_stats, config=config)

    assert result.iloc[0]["Goals"] == pytest.approx(1.972, abs=1e-3)
    assert result.iloc[0]["Goals Conceded"] == pytest.approx(0.875, abs=1e-3)


def test_calibrate_with_empirical_stats():
    df = pd.DataFrame([{"Team": "MCI", "Goals": 2.000, "Goals Conceded": 1.000}])
    fpl_stats = {
        "MCI": {
            "matches_played": 5,
            "empirical_attack_per_match": 2.400,
            "empirical_defense_per_match": 1.200,
        }
    }

    # 50/50 blend: Goals = 0.5 * 2.0 + 0.5 * 2.4 = 2.2; Conceded = 0.5 * 1.0 + 0.5 * 1.2 = 1.1
    config = CalibrationConfig(weight=0.50)
    result = calibrate_team_strengths(df, fpl_stats, config=config)

    assert result.iloc[0]["Goals"] == pytest.approx(2.200, abs=1e-3)
    assert result.iloc[0]["Goals Conceded"] == pytest.approx(1.100, abs=1e-3)


def test_calculate_home_advantage_factor_empty():
    from solio_calibrate.calibrate import calculate_home_advantage_factor

    # The empirical calculation retains its neutral baseline when no matches are available.
    h = calculate_home_advantage_factor([])
    assert h == pytest.approx(0.096, abs=1e-4)


def test_calculate_home_advantage_factor_with_matches():
    from solio_calibrate.calibrate import calculate_home_advantage_factor

    # Match where home attack is 1.644 and away attack is 1.356.
    matches = [
        {
            "home_goals": 2,
            "away_goals": 1,
            "home_xg": 1.288,
            "away_xg": 1.712,
        }
    ]
    # Home G+xG = 3.288 / 2 = 1.644; Away G+xG = 2.712 / 2 = 1.356
    h = calculate_home_advantage_factor(matches, pseudo_matches=0.0)
    # (1.644 - 1.356) / (1.644 + 1.356) = 0.288 / 3.0
    assert h == pytest.approx(0.096, abs=1e-4)
