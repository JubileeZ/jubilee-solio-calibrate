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
