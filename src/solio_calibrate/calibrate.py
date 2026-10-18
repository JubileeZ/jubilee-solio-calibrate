"""Pure calibration logic for Solio team attack and defense strengths."""

from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from solio_calibrate.mapping import SOLIO_TEAMS


@dataclass
class CalibrationConfig:
    """Configuration parameters for calibrating Solio team strengths.

    Attributes:
        weight: Blend weight in [0.0, 1.0] between base Solio stats (1 - weight)
            and actual FPL performance (weight). Default is 0.50 (50/50 mix).
        recent_weight: Blend weight in [0.0, 1.0] for recent gameweek form vs
            full season performance when using legacy actual stats.
        attack_scale: Global multiplier applied to all calibrated Goals values.
        defense_scale: Global multiplier applied to all calibrated Goals Conceded values.
        team_multipliers: Optional per-team multipliers, e.g.
            {"ARS": {"goals": 1.05, "conceded": 0.95}}.
        min_value: Minimum floor clamp for goals and goals conceded.
    """

    weight: float = 0.50
    recent_weight: float = 0.50
    attack_scale: float = 1.00
    defense_scale: float = 1.00
    team_multipliers: dict[str, dict[str, float]] = field(default_factory=dict)
    min_value: float = 0.05
    team_weights: dict[str, float] = field(default_factory=dict)


def compute_auto_weight(matches_or_gw: int) -> float:
    """Compute recommended empirical blend weight based on matches played or season progress.

    Decays linearly from 100% Solio baseline (weight=0.0) at 0 matches/GW
    to 100% empirical season stats (weight=1.0) once half the season (19 matches/GW)
    has been reached. From 19 onward, weight remains 1.0 (pure season stats).
    """
    if matches_or_gw <= 0:
        return 0.0
    if matches_or_gw >= 19:
        return 1.0
    return round(matches_or_gw / 19.0, 4)


def calculate_home_advantage_factor(
    match_records: list[dict[str, Any]],
    pseudo_matches: float = 10.0,
    prior_factor: float = 0.096,
    clamp_min: float = 0.0,
    clamp_max: float = 0.25,
) -> float:
    """Compute empirical league-wide home advantage factor h from match records.

    Solio defines:
        Home Goals = Goals * (1 + h)
        Away Goals = Goals * (1 - h)
    where h = (Avg_home - Avg_away) / (Avg_home + Avg_away).

    If match_records is empty (pre-season or unplayed), returns prior_factor (0.096).
    In early gameweeks, applies Bayesian shrinkage with pseudo_matches of prior_factor.
    """
    if not match_records:
        return prior_factor

    tot_home = sum(
        0.5 * m.get("home_goals", 0) + 0.5 * m.get("home_xg", 0.0) for m in match_records
    )
    tot_away = sum(
        0.5 * m.get("away_goals", 0) + 0.5 * m.get("away_xg", 0.0) for m in match_records
    )
    n = len(match_records)

    if n == 0 or (tot_home + tot_away) == 0:
        return prior_factor

    mean_per_match = (tot_home + tot_away) / (2 * n)
    prior_home_rate = mean_per_match * (1.0 + prior_factor)
    prior_away_rate = mean_per_match * (1.0 - prior_factor)

    effective_home = tot_home + pseudo_matches * prior_home_rate
    effective_away = tot_away + pseudo_matches * prior_away_rate

    denom = effective_home + effective_away
    if denom == 0:
        return prior_factor

    h = (effective_home - effective_away) / denom
    return max(clamp_min, min(clamp_max, round(h, 4)))


def calculate_team_empirical_form(
    match_records: list[dict[str, Any]],
    pseudo_matches: float = 3.0,
    clamp_min: float = 0.65,
    clamp_max: float = 1.35,
    home_factor: float | None = None,
) -> dict[str, dict[str, Any]]:
    """Compute venue-neutral, leave-one-out opponent-normalized empirical form.

    Args:
        match_records: List of match dicts with home_team, away_team, goals, and xG.
        pseudo_matches: Bayesian shrinkage weight toward league average (default 3.0).
        clamp_min: Minimum difficulty multiplier floor (default 0.65).
        clamp_max: Maximum difficulty multiplier cap (default 1.35).
        home_factor: Optional league-wide home advantage factor. If None, computed from matches.

    Returns:
        Mapping of Solio 3-letter team codes to their computed empirical metrics.
    """
    if home_factor is None:
        effective_home_factor = calculate_home_advantage_factor(match_records)
    else:
        effective_home_factor = float(home_factor)

    summary: dict[str, dict[str, Any]] = {}
    for code in SOLIO_TEAMS:
        summary[code] = {
            "matches_played": 0,
            "goals_scored": 0,
            "goals_conceded": 0,
            "xg_scored": 0.0,
            "xg_conceded": 0.0,
            "home_factor": effective_home_factor,
            "raw_attack_per_match": 0.0,
            "raw_defense_per_match": 0.0,
            "empirical_attack_per_match": 0.0,
            "empirical_defense_per_match": 0.0,
            "goals_per_match": 0.0,
            "conceded_per_match": 0.0,
            "recent_goals_per_match": 0.0,
            "recent_conceded_per_match": 0.0,
        }

    if not match_records:
        return summary

    home_multiplier = 1.0 + effective_home_factor if (1.0 + effective_home_factor) > 0.01 else 1.0
    away_multiplier = 1.0 - effective_home_factor if (1.0 - effective_home_factor) > 0.01 else 1.0

    team_scores: list[float] = []
    team_matches: dict[str, list[dict[str, Any]]] = {code: [] for code in SOLIO_TEAMS}

    for match in match_records:
        home_code = match["home_team"]
        away_code = match["away_team"]
        home_goals = match["home_goals"]
        away_goals = match["away_goals"]
        home_xg = match["home_xg"]
        away_xg = match["away_xg"]

        home_attack_neutral = (0.5 * home_goals + 0.5 * home_xg) / home_multiplier
        home_defense_neutral = (0.5 * away_goals + 0.5 * away_xg) / away_multiplier

        away_attack_neutral = (0.5 * away_goals + 0.5 * away_xg) / away_multiplier
        away_defense_neutral = (0.5 * home_goals + 0.5 * home_xg) / home_multiplier

        team_scores.extend([home_attack_neutral, away_attack_neutral])

        if home_code in team_matches:
            team_matches[home_code].append({
                "opponent": away_code,
                "is_home": True,
                "goals": home_goals,
                "conceded": away_goals,
                "xg": home_xg,
                "xgc": away_xg,
                "attack_neutral": home_attack_neutral,
                "defense_neutral": home_defense_neutral,
            })
        if away_code in team_matches:
            team_matches[away_code].append({
                "opponent": home_code,
                "is_home": False,
                "goals": away_goals,
                "conceded": home_goals,
                "xg": away_xg,
                "xgc": home_xg,
                "attack_neutral": away_attack_neutral,
                "defense_neutral": away_defense_neutral,
            })

    league_avg_team_rate = sum(team_scores) / len(team_scores) if team_scores else 1.45

    for code, matches in team_matches.items():
        if not matches:
            continue

        total_goals = sum(m["goals"] for m in matches)
        total_conceded = sum(m["conceded"] for m in matches)
        total_xg = sum(m["xg"] for m in matches)
        total_xgc = sum(m["xgc"] for m in matches)
        n = len(matches)

        adjusted_attacks: list[float] = []
        adjusted_defenses: list[float] = []

        for m in matches:
            opponent_code = m["opponent"]
            opponent_other_matches = [
                om for om in team_matches.get(opponent_code, []) if om["opponent"] != code
            ]

            opponent_defense_sum = sum(om["defense_neutral"] for om in opponent_other_matches)
            opponent_defense_rating = (
                opponent_defense_sum + pseudo_matches * league_avg_team_rate
            ) / (len(opponent_other_matches) + pseudo_matches)

            opponent_attack_sum = sum(om["attack_neutral"] for om in opponent_other_matches)
            opponent_attack_rating = (
                opponent_attack_sum + pseudo_matches * league_avg_team_rate
            ) / (len(opponent_other_matches) + pseudo_matches)

            multiplier_attack = max(
                clamp_min, min(clamp_max, league_avg_team_rate / opponent_defense_rating)
            )
            multiplier_defense = max(
                clamp_min, min(clamp_max, league_avg_team_rate / opponent_attack_rating)
            )

            adjusted_attacks.append(m["attack_neutral"] * multiplier_attack)
            adjusted_defenses.append(m["defense_neutral"] * multiplier_defense)

        empirical_attack = sum(adjusted_attacks) / n
        empirical_defense = sum(adjusted_defenses) / n

        summary[code] = {
            "matches_played": n,
            "goals_scored": total_goals,
            "goals_conceded": total_conceded,
            "xg_scored": total_xg,
            "xg_conceded": total_xgc,
            "home_factor": effective_home_factor,
            "raw_attack_per_match": sum(m["attack_neutral"] for m in matches) / n,
            "raw_defense_per_match": sum(m["defense_neutral"] for m in matches) / n,
            "empirical_attack_per_match": empirical_attack,
            "empirical_defense_per_match": empirical_defense,
            "goals_per_match": empirical_attack,
            "conceded_per_match": empirical_defense,
            "recent_goals_per_match": empirical_attack,
            "recent_conceded_per_match": empirical_defense,
        }

    return summary


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

        effective_weight = (
            config.team_weights.get(code, config.weight)
            if config.team_weights
            else config.weight
        )

        if matches_played > 0 and effective_weight > 0.0:
            if "empirical_attack_per_match" in team_stats:
                fpl_goals = team_stats["empirical_attack_per_match"]
            else:
                season_goals_pg = team_stats.get("goals_per_match", base_goals)
                recent_goals_pg = team_stats.get("recent_goals_per_match", season_goals_pg)
                fpl_goals = (1.0 - config.recent_weight) * season_goals_pg + (
                    config.recent_weight * recent_goals_pg
                )

            if "empirical_defense_per_match" in team_stats:
                fpl_conceded = team_stats["empirical_defense_per_match"]
            else:
                season_conceded_pg = team_stats.get("conceded_per_match", base_conceded)
                recent_conceded_pg = team_stats.get(
                    "recent_conceded_per_match", season_conceded_pg
                )
                fpl_conceded = (1.0 - config.recent_weight) * season_conceded_pg + (
                    config.recent_weight * recent_conceded_pg
                )

            goals = (1.0 - effective_weight) * base_goals + (effective_weight * fpl_goals)
            conceded = (1.0 - effective_weight) * base_conceded + (effective_weight * fpl_conceded)
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
