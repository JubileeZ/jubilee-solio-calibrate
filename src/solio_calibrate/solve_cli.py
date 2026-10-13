"""CLI runner for Solio FPL squad optimization."""

import argparse
import sys
from pathlib import Path

from solio_calibrate.projections import (
    CANONICAL_PROJECTIONS_FILENAME,
    ingest_and_archive_projections,
)
from solio_calibrate.solver.adapter import (
    prepare_solve_context,
    solve_squad,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the solio-solve argument parser."""
    parser = argparse.ArgumentParser(
        prog="solio-solve",
        description="Solve optimal FPL squad transfers, lineups, and captaincy from Solio projections.",
    )
    parser.add_argument(
        "--team-id",
        type=int,
        default=None,
        help="Official FPL manager team ID to fetch current squad, bank, and free transfers.",
    )
    parser.add_argument(
        "--projections",
        "-p",
        type=str,
        default=None,
        help="Path to Solio player projections CSV. Defaults to data/projections/solio_projections.csv.",
    )
    parser.add_argument(
        "--horizon",
        type=int,
        default=10,
        help="Planning horizon in gameweeks (default: 10). Auto-expands if chips are scheduled beyond it.",
    )
    parser.add_argument(
        "--fh",
        type=int,
        action="append",
        default=[],
        help="Schedule Free Hit chip in specified gameweek (can be passed multiple times).",
    )
    parser.add_argument(
        "--wc",
        type=int,
        action="append",
        default=[],
        help="Schedule Wildcard chip in specified gameweek.",
    )
    parser.add_argument(
        "--bb",
        type=int,
        action="append",
        default=[],
        help="Schedule Bench Boost chip in specified gameweek.",
    )
    parser.add_argument(
        "--tc",
        type=int,
        action="append",
        default=[],
        help="Schedule Triple Captain chip in specified gameweek.",
    )
    parser.add_argument(
        "--preseason",
        action="store_true",
        help="Solve unconstrained squad from scratch with £100.0m budget.",
    )
    parser.add_argument(
        "--wildcard",
        action="store_true",
        help="Solve unconstrained wildcard squad for the upcoming gameweek.",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="data/output/solver",
        help="Directory to save squad plan CSV files (default: data/output/solver).",
    )
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="Skip interactive confirmation prompt and execute solver immediately.",
    )
    return parser


def main(
    argv: list[str] | None = None,
    projections_dir: Path = Path("data/projections"),
) -> int:
    """Execute the solio-solve CLI."""
    parser = build_parser()
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    # Resolve projections file
    proj_dir = projections_dir
    if args.projections:
        src = Path(args.projections)
        active_proj, archived = ingest_and_archive_projections(src, projections_dir=proj_dir)
        if archived:
            print(f"✓ Ingested new projections: {active_proj} (archived prior to {archived})")
        else:
            print(f"✓ Using projections: {active_proj}")
        resolved_proj = active_proj
    else:
        resolved_proj = proj_dir / CANONICAL_PROJECTIONS_FILENAME
        if not resolved_proj.is_file():
            print(
                f"Error: No active projections found at {resolved_proj}.\n"
                "Please specify a Solio projections CSV with '--projections <path>'.",
                file=sys.stderr,
            )
            return 1

    chips = {
        "fh": args.fh,
        "wc": args.wc,
        "bb": args.bb,
        "tc": args.tc,
    }

    try:
        ctx = prepare_solve_context(
            projections_path=resolved_proj,
            team_id=args.team_id,
            horizon=args.horizon,
            chips=chips,
            wildcard=args.wildcard,
            preseason=args.preseason,
        )
    except (RuntimeError, ValueError, FileNotFoundError) as e:
        print(f"\nError preparing solver settings: {e}", file=sys.stderr)
        return 1

    # Pre-solve confirmation check
    if not args.yes:
        print("\n" + ctx["summary"])

        try:
            choice = input("\nConfirm settings and run HiGHS solver? [y/N]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nSolve cancelled by user.")
            return 0

        if choice not in ("y", "yes"):
            print("Solve cancelled by user.")
            return 0

    print("\nSolving multi-period FPL integer optimization model with HiGHS...")
    try:
        result = solve_squad(
            projections_path=resolved_proj,
            team_id=args.team_id,
            horizon=args.horizon,
            chips=chips,
            wildcard=args.wildcard,
            preseason=args.preseason,
            output_dir=Path(args.output),
            context=ctx,
        )
    except (RuntimeError, ValueError, FileNotFoundError) as e:
        print(f"\nError running solver: {e}", file=sys.stderr)
        return 1

    print("\n" + result["summary"])
    print("\n### Optimal Transfer & Lineup Plan\n")
    print(result["table"])
    print(f"\nTotal Projected Points: {result['score']:.2f}")
    print(f"\n✓ Squad plan saved to: {result['plan_file']}")
    print(f"\n👉 View and edit on FPL.Team:\n   {result['fplteam_url']}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
