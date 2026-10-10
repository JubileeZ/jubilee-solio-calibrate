import argparse
import logging
import sys
from collections.abc import Sequence
from pathlib import Path

import httpx

from solio_calibrate.calibrate import CalibrationConfig, calibrate_team_strengths
from solio_calibrate.client import FPLClient
from solio_calibrate.io import load_solio_team_strengths, save_solio_team_strengths

logger = logging.getLogger("solio_calibrate")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Calibrate Solio team attack/defense strengths using FPL API stats and preferences.",
    )
    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        default=Path("data/raw/team_strengths.csv"),
        help="Path to original Solio team strengths CSV (default: data/raw/team_strengths.csv)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("data/output/team_strengths_calibrated.csv"),
        help="Path to output calibrated CSV (default: data/output/team_strengths_calibrated.csv)",
    )
    parser.add_argument(
        "-w",
        "--weight",
        type=float,
        default=0.30,
        help="Weight [0.0-1.0] for FPL performance vs Solio baseline (default: 0.30)",
    )
    parser.add_argument(
        "--recent-weight",
        type=float,
        default=0.50,
        help="Weight [0.0-1.0] for recent gameweek form (default: 0.50)",
    )
    parser.add_argument(
        "--attack-scale",
        type=float,
        default=1.00,
        help="Global multiplier for Goals (default: 1.00)",
    )
    parser.add_argument(
        "--defense-scale",
        type=float,
        default=1.00,
        help="Global multiplier for Goals Conceded (default: 1.00)",
    )
    parser.add_argument(
        "--team-boost",
        action="append",
        default=[],
        metavar="TEAM:STAT:MULT",
        help="Custom multiplier for a team, e.g. 'ARS:goals:1.10' or 'CHE:conceded:0.90'",
    )
    parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-fetching data from FPL API ignoring local cache",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Offline mode: do not call FPL API network endpoints; use cache or skip",
    )
    return parser.parse_args(argv)


def main_cli(argv: Sequence[str] | None = None) -> int:
    """CLI execution entrypoint returning exit code."""
    args = parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    # Load input Solio CSV
    logger.info(f"Loading Solio input from {args.input}...")
    try:
        base_df = load_solio_team_strengths(args.input)
    except (OSError, ValueError, KeyError) as e:
        logger.error(f"Failed to load input CSV: {e}")
        return 1

    # Fetch FPL stats if weight > 0 and not offline
    fpl_stats = {}
    if args.weight > 0.0:
        if args.offline:
            logger.info("Offline mode requested; reading cached FPL fixtures if available...")
            client = FPLClient()
            cached_fixtures = client._load_cache("fixtures.json")
            if cached_fixtures:
                from solio_calibrate.client import calculate_team_actual_stats

                fpl_stats = calculate_team_actual_stats(cached_fixtures)
            else:
                logger.warning("No cached fixtures found in offline mode; using Solio base values.")
        else:
            try:
                logger.info("Fetching FPL fixture performance data...")
                client = FPLClient()
                fpl_stats = client.get_team_actual_stats(force_refresh=args.force_refresh)
            except (httpx.HTTPError, OSError, ValueError, KeyError) as e:
                logger.warning(f"Could not fetch live FPL API ({e}); falling back to base values.")

    # Parse team boosts
    team_multipliers: dict[str, dict[str, float]] = {}
    for boost in args.team_boost:
        parts = boost.split(":")
        if len(parts) == 3:
            t_code = parts[0].strip().upper()
            stat_name = parts[1].strip().lower()
            try:
                val = float(parts[2])
                if t_code not in team_multipliers:
                    team_multipliers[t_code] = {}
                team_multipliers[t_code][stat_name] = val
            except ValueError:
                logger.warning(f"Invalid team boost numeric value: {boost}")
        else:
            logger.warning(f"Ignoring invalid team boost format (expected TEAM:STAT:MULT): {boost}")

    # Run calibration
    config = CalibrationConfig(
        weight=args.weight,
        recent_weight=args.recent_weight,
        attack_scale=args.attack_scale,
        defense_scale=args.defense_scale,
        team_multipliers=team_multipliers,
    )

    logger.info(f"Calibrating {len(base_df)} teams (weight={args.weight})...")
    calibrated_df = calibrate_team_strengths(base_df, fpl_stats, config=config)

    # Save output
    try:
        out_path = save_solio_team_strengths(calibrated_df, args.output)
        logger.info(f"Successfully wrote calibrated Solio CSV to: {out_path}")
    except (PermissionError, ValueError, OSError) as e:
        logger.error(f"Failed to save output CSV: {e}")
        return 1

    return 0


def main() -> None:
    """Script entrypoint."""
    sys.exit(main_cli())


if __name__ == "__main__":
    main()
