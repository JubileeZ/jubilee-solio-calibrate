import argparse
import json
import logging
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import httpx

from solio_calibrate.calibrate import (
    CalibrationConfig,
    calculate_home_advantage_factor,
    calculate_team_empirical_form,
    calibrate_team_strengths,
    compute_auto_weight,
)
from solio_calibrate.client import FPLClient
from solio_calibrate.io import (
    CANONICAL_BASE_FILENAME,
    ingest_and_archive_raw_input,
    load_solio_team_strengths,
    save_and_archive_calibrated_strengths,
)

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
        default=None,
        help="Path to original Solio team strengths CSV (default: data/raw/team_strengths_base.csv)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Override output CSV path (default: data/output/team_strengths_calibrated.csv with archive copy)",
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=Path("data/raw"),
        help="Root directory for base strength CSV and archive (default: data/raw)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/output"),
        help="Root directory for calibrated strength CSV and archive (default: data/output)",
    )
    parser.add_argument(
        "--no-ingest",
        action="store_true",
        help="Do not ingest/archive raw input into data/raw/team_strengths_base.csv",
    )
    parser.add_argument(
        "--ingest-raw",
        action="store_true",
        help="Force ingesting and archiving raw input into data/raw/ even if --output is specified",
    )
    parser.add_argument(
        "-w",
        "--weight",
        type=float,
        default=0.50,
        help="Weight [0.0-1.0] for FPL empirical form vs Solio baseline (default: 0.50)",
    )
    parser.add_argument(
        "--auto-weight",
        action="store_true",
        help="Automatically compute blend weight based on maximum finished gameweek (0.0 if unplayed)",
    )
    parser.add_argument(
        "--max-gameweek",
        type=int,
        default=None,
        help="Upper bound gameweek to include in empirical calculation",
    )
    parser.add_argument(
        "--pseudo-matches",
        type=float,
        default=3.0,
        help="Bayesian shrinkage pseudo-matches for opponent normalization (default: 3.0)",
    )
    parser.add_argument(
        "--clamp-min",
        type=float,
        default=0.65,
        help="Minimum opponent difficulty multiplier floor (default: 0.65)",
    )
    parser.add_argument(
        "--clamp-max",
        type=float,
        default=1.35,
        help="Maximum opponent difficulty multiplier cap (default: 1.35)",
    )
    parser.add_argument(
        "--recent-weight",
        type=float,
        default=0.50,
        help="Weight [0.0-1.0] for recent gameweek form (legacy mode) (default: 0.50)",
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
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output machine-readable JSON summary to stdout",
    )
    args = parser.parse_args(argv)
    args.input_explicit = args.input is not None
    if args.input is None:
        default_candidate = args.raw_dir / CANONICAL_BASE_FILENAME
        if not default_candidate.exists() and (args.raw_dir / "team_strengths.csv").exists():
            args.input = args.raw_dir / "team_strengths.csv"
        else:
            args.input = default_candidate
    return args


def main_cli(argv: Sequence[str] | None = None) -> int:
    """CLI execution entrypoint returning exit code."""
    args = parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    # Handle raw input ingestion and archiving
    should_ingest = args.ingest_raw or (
        args.input_explicit and args.output is None and not args.no_ingest
    )
    input_to_load = args.input
    if should_ingest:
        try:
            input_to_load, archived_raw = ingest_and_archive_raw_input(
                args.input, raw_dir=args.raw_dir
            )
            logger.info(f"Ingested raw input to active base strength: {input_to_load}")
            if archived_raw:
                logger.info(f"Archived previous base strength to: {archived_raw}")
        except (OSError, ValueError) as e:
            logger.error(f"Failed to ingest raw input CSV: {e}")
            return 1

    # Load input Solio CSV
    logger.info(f"Loading Solio input from {input_to_load}...")
    try:
        base_df = load_solio_team_strengths(input_to_load)
    except (OSError, ValueError, KeyError) as e:
        logger.error(f"Failed to load input CSV: {e}")
        return 1

    client = FPLClient()

    # Determine max finished gameweek
    max_gw = 0
    try:
        fixtures = (
            client.get_fixtures(force_refresh=args.force_refresh)
            if not args.offline
            else client.get_cached_fixtures()
        )
        finished_gws = [
            f.get("event")
            for f in fixtures
            if (f.get("finished") or f.get("finished_provisional"))
            and f.get("event") is not None
        ]
        if args.max_gameweek is not None:
            finished_gws = [gw for gw in finished_gws if gw <= args.max_gameweek]
        max_gw = max(finished_gws) if finished_gws else 0
    except (httpx.HTTPError, OSError, ValueError, KeyError):
        max_gw = 0

    # Fetch empirical match records and compute Home Advantage Factor
    fpl_stats: dict[str, dict[str, Any]] = {}
    provisional_matches_summary: list[str] = []
    home_factor = 0.0
    try:
        match_records = client.get_match_records(
            force_refresh=args.force_refresh,
            max_gameweek=args.max_gameweek,
            offline=args.offline,
        )
        if match_records:
            provisional_records = [r for r in match_records if r.get("is_provisional")]
            provisional_matches_summary = [
                f"{r['home_team']} {r['home_goals']}-{r['away_goals']} {r['away_team']}"
                for r in provisional_records
            ]
            home_factor = calculate_home_advantage_factor(match_records)
            fpl_stats = calculate_team_empirical_form(
                match_records,
                pseudo_matches=args.pseudo_matches,
                clamp_min=args.clamp_min,
                clamp_max=args.clamp_max,
                home_factor=home_factor,
            )
    except (httpx.HTTPError, OSError, ValueError, KeyError) as e:
        logger.warning(
            f"Could not load empirical match records ({e}); falling back to base values."
        )

    # Weight resolution: per-team weights based on matches played or manual override
    team_weights: dict[str, float] = {}
    team_codes = [str(t).strip().upper() for t in base_df["Team"]]

    if max_gw <= 0:
        effective_weight = 0.0
        team_weights = {code: 0.0 for code in team_codes}
        logger.info("No finished gameweeks detected; using 100% Solio base values (weight=0.00).")
    elif args.auto_weight:
        for code in team_codes:
            matches_played = fpl_stats.get(code, {}).get("matches_played", 0)
            team_weights[code] = compute_auto_weight(matches_played)
        effective_weight = max(team_weights.values()) if team_weights else 0.0
        logger.info(
            f"Auto-weight evaluated for max finished GW{max_gw}: max weight={effective_weight:.2f}"
        )
    else:
        effective_weight = args.weight
        team_weights = {
            code: args.weight if fpl_stats.get(code, {}).get("matches_played", 0) > 0 else 0.0
            for code in team_codes
        }

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
        weight=effective_weight,
        recent_weight=args.recent_weight,
        attack_scale=args.attack_scale,
        defense_scale=args.defense_scale,
        team_multipliers=team_multipliers,
        team_weights=team_weights,
    )

    logger.info(f"Calibrating {len(base_df)} teams (weight={effective_weight:.2f})...")
    calibrated_df = calibrate_team_strengths(base_df, fpl_stats, config=config)

    # Save output
    try:
        out_path, archived_path = save_and_archive_calibrated_strengths(
            calibrated_df,
            output_path=args.output,
            output_dir=args.output_dir,
        )
        logger.info(f"Successfully wrote calibrated Solio CSV to: {out_path}")
        if archived_path:
            logger.info(f"Archived calibrated Solio CSV to: {archived_path}")
    except (PermissionError, ValueError, OSError) as e:
        logger.error(f"Failed to save output CSV: {e}")
        return 1

    # Extract empirical home advantage factor
    home_factor = 0.0
    for s in fpl_stats.values():
        if "home_factor" in s:
            home_factor = float(s["home_factor"])
            break

    if args.json:
        summary_payload = {
            "calibrated_file": str(out_path.resolve()),
            "archived_file": str(archived_path.resolve()) if archived_path else None,
            "teams_calibrated": len(calibrated_df),
            "finished_gameweeks": max_gw,
            "home_factor_pct": round(home_factor * 100, 2),
            "blend_weight": round(effective_weight, 2),
            "team_weights": {c: round(w, 4) for c, w in team_weights.items()},
            "provisional_matches": provisional_matches_summary,
        }
        print(json.dumps(summary_payload, indent=2))
    else:
        print("\n" + "=" * 42)
        print("=== Solio Calibration Summary ===")
        print(f"Calibrated CSV: {out_path.resolve()}")
        if archived_path:
            print(f"Archived CSV: {archived_path.resolve()}")
        print(f"Teams Calibrated: {len(calibrated_df)}")
        print(f"Finished Gameweeks: {max_gw}")
        print(f"Empirical Home Advantage Factor: {home_factor * 100:.2f}%")
        distinct_weights = {round(w, 2) for w in team_weights.values()}
        if len(distinct_weights) > 1:
            min_w = min(team_weights.values()) * 100
            max_w = max(team_weights.values()) * 100
            print(f"Effective Blend Weights: {min_w:.1f}% - {max_w:.1f}%")
        else:
            print(f"Effective Blend Weight: {effective_weight * 100:.1f}%")
        if provisional_matches_summary:
            print(
                f"Provisional Matches: {len(provisional_matches_summary)} "
                f"({', '.join(provisional_matches_summary)})"
            )
        print("=" * 42 + "\n")

    return 0


def main() -> None:
    """Script entrypoint."""
    sys.exit(main_cli())


if __name__ == "__main__":
    main()
