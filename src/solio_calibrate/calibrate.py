"""Pure calibration logic for Solio team attack and defense strengths."""

from dataclasses import dataclass, field
from typing import Any

import pandas as pd


@dataclass
class CalibrationConfig:
    """Configuration parameters for calibrating Solio team strengths.

    Attributes:
        weight: Blend weight in [0.0, 1.0] between base Solio stats (1 - weight)
            and actual FPL performance (weight).
        recent_weight: Blend weight in [0.0, 1.0] for recent gameweek form vs
            full season performance within the FPL stats component.
        attack_scale: Global multiplier applied to all calibrated Goals values.
        defense_scale: Global multiplier applied to all calibrated Goals Conceded values.
        team_multipliers: Optional per-team multipliers, e.g.
            {"ARS": {"goals": 1.05, "conceded": 0.95}}.
        min_value: Minimum floor clamp for goals and goals conceded.
    """

    weight: float = 0.30
    recent_weight: float = 0.50
    attack_scale: float = 1.00
    defense_scale: float = 1.00
    team_multipliers: dict[str, dict[str, float]] = field(default_factory=dict)
    min_value: float = 0.05


def calibrate_team_strengths(
    base_df: pd.DataFrame,
    fpl_stats: dict[str, dict[str, Any]],
    config: CalibrationConfig | None = None,
) -> pd.DataFrame:
    """Calibrate base Solio team strengths with FPL match data and user preferences.

    Args:
        base_df: DataFrame with ['Team', 'Goals', 'Goals Conceded'].
        fpl_stats: Mapping of team codes to performance stats from client.
        config: Calibration configuration options.

    Returns:
        DataFrame with calibrated values rounded to 3 decimal places.
    """
    if config is None:
        config = CalibrationConfig()

    calibrated_rows = []

    for _, row in base_df.iterrows():
        code = str(row["Team"]).strip().upper()
        base_goals = float(row["Goals"])
        base_conceded = float(row["Goals Conceded"])

        team_stats = fpl_stats.get(code, {})
        matches_played = team_stats.get("matches_played", 0)

        if matches_played > 0 and config.weight > 0.0:
            season_goals_pg = team_stats.get("goals_per_match", base_goals)
            recent_goals_pg = team_stats.get("recent_goals_per_match", season_goals_pg)
            fpl_goals = (1.0 - config.recent_weight) * season_goals_pg + (
                config.recent_weight * recent_goals_pg
            )

            season_conceded_pg = team_stats.get("conceded_per_match", base_conceded)
            recent_conceded_pg = team_stats.get("recent_conceded_per_match", season_conceded_pg)
            fpl_conceded = (1.0 - config.recent_weight) * season_conceded_pg + (
                config.recent_weight * recent_conceded_pg
            )

            goals = (1.0 - config.weight) * base_goals + (config.weight * fpl_goals)
            conceded = (1.0 - config.weight) * base_conceded + (config.weight * fpl_conceded)
        else:
            goals = base_goals
            conceded = base_conceded

        # Apply global scaling
        goals *= config.attack_scale
        conceded *= config.defense_scale

        # Apply team-specific multipliers
        if code in config.team_multipliers:
            t_mult = config.team_multipliers[code]
            goals *= t_mult.get("goals", 1.0)
            conceded *= t_mult.get("conceded", 1.0)

        # Clamp to minimum safe value
        goals = max(goals, config.min_value)
        conceded = max(conceded, config.min_value)

        calibrated_rows.append({
            "Team": code,
            "Goals": round(goals, 3),
            "Goals Conceded": round(conceded, 3),
        })

    return pd.DataFrame(calibrated_rows)
