"""Adapter interfacing between jubilee-solio-calibrate and vendored open-fpl-solver."""

import sys
from pathlib import Path
from typing import Any

from tabulate import tabulate

BINARY_THRESHOLD = 0.5


def calculate_effective_horizon(
    base_horizon: int,
    next_gw: int,
    use_fh: list[int] | None = None,
    use_wc: list[int] | None = None,
    use_bb: list[int] | None = None,
    use_tc: list[int] | None = None,
) -> tuple[int, bool]:
    """Calculate the effective planning horizon, auto-expanding if chips are scheduled beyond it.

    Args:
        base_horizon: Configured base horizon (default 10).
        next_gw: Starting gameweek of the solve.
        use_fh: List of GWs where Free Hit is scheduled.
        use_wc: List of GWs where Wildcard is scheduled.
        use_bb: List of GWs where Bench Boost is scheduled.
        use_tc: List of GWs where Triple Captain is scheduled.

    Returns:
        Tuple of (effective_horizon, was_expanded).
    """
    all_chips = (use_fh or []) + (use_wc or []) + (use_bb or []) + (use_tc or [])
    if not all_chips:
        return base_horizon, False

    max_chip_gw = max(all_chips)
    needed_horizon = max_chip_gw - next_gw + 1

    if needed_horizon > base_horizon:
        return needed_horizon, True
    return base_horizon, False


def format_confirmation_summary(
    team_id: int | None,
    next_gw: int,
    horizon: int,
    expanded: bool,
    chips: dict[str, list[int]],
    projections_path: Path,
    bank: float,
    free_transfers: int,
) -> str:
    """Format structured confirmation summary of solve settings before execution."""
    chip_items = []
    for chip_name, gws in chips.items():
        if gws:
            chip_items.append(f"{chip_name.upper()}: GW {', '.join(str(g) for g in gws)}")
    chips_str = ", ".join(chip_items) if chip_items else "None scheduled"

    expansion_note = " (Auto-expanded to cover scheduled chip)" if expanded else ""

    lines = [
        "===========================================================",
        "           SOLIO SQUAD OPTIMIZER - SETTINGS REVIEW        ",
        "===========================================================",
        f"  • FPL Team ID:        {team_id if team_id else 'Unconstrained / Preseason'}",
        f"  • Starting Gameweek:  GW {next_gw}",
        f"  • Planning Horizon:   {horizon} Gameweeks (GW {next_gw} to {next_gw + horizon - 1}){expansion_note}",
        f"  • Active Projections: {projections_path.name}",
        f"  • Current Bank:       £{bank:.1f}m",
        f"  • Free Transfers:     {free_transfers}",
        f"  • Planned Chips:      {chips_str}",
        "===========================================================",
    ]
    return "\n".join(lines)


def generate_fplteam_link(response: list[dict[str, Any]], team_id: int | None = None) -> str:
    """Generate an interactive fpl.team URL encoding the optimal plan.

    Args:
        response: Output solution list from solve_multi_period_fpl.
        team_id: Optional manager team ID.

    Returns:
        Full fpl.team planner URL.
    """
    if not response:
        return ""

    result = response[0]
    picks = result["picks"]
    gws = picks["week"].unique()
    effective_team_id = team_id if team_id is not None else 1
    url_base = f"https://fpl.team/plan/{effective_team_id}/?"

    result_url = url_base
    for gw in gws:
        gw_picks = picks[picks["week"] == gw]
        lineup_players = ",".join(
            gw_picks[gw_picks["lineup"] > BINARY_THRESHOLD]["id"].astype(str).tolist()
        )
        bench_players = ",".join(
            gw_picks[gw_picks["bench"] > -BINARY_THRESHOLD]["id"].astype(str).tolist()
        )

        cap_df = gw_picks[gw_picks["captain"] > BINARY_THRESHOLD]
        cap = cap_df.iloc[0]["id"] if not cap_df.empty else ""

        vcap_df = gw_picks[gw_picks["vicecaptain"] > BINARY_THRESHOLD]
        vcap = vcap_df.iloc[0]["id"] if not vcap_df.empty else ""

        chip = gw_picks.iloc[0].get("chip", "") or ""

        sold_players = (
            gw_picks[gw_picks["transfer_out"] > BINARY_THRESHOLD]
            .sort_values(by="type")["id"]
            .astype(str)
            .tolist()
        )
        bought_players = (
            gw_picks[gw_picks["transfer_in"] > BINARY_THRESHOLD]
            .sort_values(by="type")["id"]
            .astype(str)
            .tolist()
        )

        if gw == 1:
            sold_players = []
            bought_players = []

        tr_string = ";".join(
            [f"{i},{j}" for (i, j) in zip(sold_players, bought_players, strict=False)]
        )
        if not tr_string:
            tr_string = ";"

        sub_text = ";"
        if gw > gws[0]:
            prev_picks = picks[picks["week"] == gw - 1]
            prev_lineup = prev_picks[prev_picks["lineup"] > BINARY_THRESHOLD]["id"].tolist()
            now_bench = gw_picks[gw_picks["bench"] > -BINARY_THRESHOLD]["id"].tolist()
            lineup_to_bench = [i for i in prev_lineup if i in now_bench]

            prev_bench = prev_picks[prev_picks["bench"] > -BINARY_THRESHOLD]["id"].tolist()
            now_lineup = gw_picks[gw_picks["lineup"] > BINARY_THRESHOLD]["id"].tolist()
            bench_to_lineup = [i for i in prev_bench if i in now_lineup]

            sub_pairs = [f"{i},{j}" for (i, j) in zip(lineup_to_bench, bench_to_lineup, strict=False)]
            if sub_pairs:
                sub_text = ";".join(sub_pairs)

        gw_params = (
            f"lineup{gw}={lineup_players}&bench{gw}={bench_players}&cap{gw}={cap}&vcap{gw}={vcap}"
            f"&chip{gw}={chip}&transfers{gw}={tr_string}&subs{gw}={sub_text}&opt=true"
        )
        result_url += ("" if gw == gws[0] else "&") + gw_params

    return result_url


def format_solution_table(response: list[dict[str, Any]]) -> str:
    """Format solution picks and transfers into a clean ASCII table."""
    if not response:
        return "No solutions found."

    result = response[0]
    picks = result["picks"]
    gws = sorted(picks["week"].unique())

    table_data = []
    for gw in gws:
        gw_picks = picks[picks["week"] == gw]
        chip = gw_picks.iloc[0].get("chip", "") or "-"

        name_col = "name" if "name" in gw_picks.columns else ("web_name" if "web_name" in gw_picks.columns else "id")

        cap_df = gw_picks[gw_picks["captain"] > BINARY_THRESHOLD]
        cap_name = str(cap_df.iloc[0][name_col]) if not cap_df.empty else "-"

        vcap_df = gw_picks[gw_picks["vicecaptain"] > BINARY_THRESHOLD]
        vcap_name = str(vcap_df.iloc[0][name_col]) if not vcap_df.empty else "-"

        in_df = gw_picks[gw_picks["transfer_in"] > BINARY_THRESHOLD]
        in_names = in_df[name_col].tolist() if not in_df.empty else []

        out_df = gw_picks[gw_picks["transfer_out"] > BINARY_THRESHOLD]
        out_names = out_df[name_col].tolist() if not out_df.empty else []

        if in_names:
            transfers_str = ", ".join(f"{o} -> {i}" for o, i in zip(out_names, in_names, strict=False))
        elif gw == gws[0]:
            transfers_str = "-"
        else:
            transfers_str = "Roll FT"

        bench_df = gw_picks[gw_picks["bench"] > -BINARY_THRESHOLD].sort_values(by="bench")
        bench_names = bench_df[name_col].tolist() if not bench_df.empty else []
        bench_str = ", ".join(bench_names) if bench_names else "-"

        table_data.append([
            f"GW {gw}",
            chip.upper() if chip != "-" else "-",
            transfers_str,
            f"{cap_name} (vc: {vcap_name})",
            bench_str,
        ])

    headers = ["Gameweek", "Chip", "Transfers", "Captaincy", "Bench Order"]
    return tabulate(table_data, headers=headers, tablefmt="github")


def prepare_solve_context(
    projections_path: str | Path,
    team_id: int | None = None,
    horizon: int = 10,
    chips: dict[str, list[int]] | None = None,
    wildcard: bool = False,
    preseason: bool = False,
    vendor_dir: Path | None = None,
) -> dict[str, Any]:
    """Prepare and validate solver options, manager team state, and confirmation summary.

    Args:
        projections_path: Path to Solio player projections CSV.
        team_id: Optional FPL manager team ID.
        horizon: Base planning horizon (default 10).
        chips: Dictionary of scheduled chips.
        wildcard: Schedule wildcard on upcoming gameweek.
        preseason: Solve unconstrained squad from scratch with £100.0m budget.
        vendor_dir: Path to vendored open-fpl-solver directory.

    Returns:
        Dictionary containing options, my_data, summary, next_gw, bank, and free_transfers.
    """
    vendor_root = (vendor_dir or (Path(__file__).parents[3] / "vendor" / "open-fpl-solver")).resolve()
    if not vendor_root.is_dir():
        raise FileNotFoundError(
            f"Vendored open-fpl-solver not found at {vendor_root}. "
            "Run 'bash scripts/sync-solver.sh' to vendor it."
        )

    if str(vendor_root) not in sys.path:
        sys.path.insert(0, str(vendor_root))

    from dev.solver import generate_team_json  # type: ignore[import-not-found]
    from utils import cached_request, load_settings  # type: ignore[import-not-found]

    options = load_settings()

    chips = chips or {}
    use_fh = list(chips.get("fh", []))
    use_wc = list(chips.get("wc", []))
    use_bb = list(chips.get("bb", []))
    use_tc = list(chips.get("tc", []))

    static_url = "https://fantasy.premierleague.com/api/bootstrap-static/"
    static_data = cached_request(static_url)
    next_gw = next(x for x in static_data["events"] if x["is_next"])["id"]

    if wildcard and next_gw not in use_wc:
        use_wc.append(next_gw)

    effective_horizon, expanded = calculate_effective_horizon(
        base_horizon=horizon,
        next_gw=next_gw,
        use_fh=use_fh,
        use_wc=use_wc,
        use_bb=use_bb,
        use_tc=use_tc,
    )

    proj_file = Path(projections_path).resolve()

    # open-fpl-solver checks DATA_DIR / f"{source}.csv"
    vendor_data_dir = vendor_root / "data"
    vendor_data_dir.mkdir(parents=True, exist_ok=True)
    solio_link = vendor_data_dir / "solio.csv"
    if solio_link.is_symlink() or solio_link.is_file():
        solio_link.unlink()
    solio_link.symlink_to(proj_file)

    options.update({
        "datasource": "solio",
        "data_path": proj_file,
        "horizon": effective_horizon,
        "use_fh": use_fh,
        "use_wc": use_wc,
        "use_bb": use_bb,
        "use_tc": use_tc,
        "single_solve": True,
        "verbose": False,
    })

    if preseason or team_id is None:
        my_data = {"picks": [], "chips": [], "transfers": {"limit": None, "cost": 4, "bank": 1000, "value": 0}}
        bank = 100.0
        free_transfers = 0
    else:
        options["team_id"] = team_id
        options["team_data"] = "id"
        my_data = generate_team_json(team_id, options)
        bank = my_data["transfers"]["bank"] / 10.0
        free_transfers = my_data["transfers"]["limit"]

    summary = format_confirmation_summary(
        team_id=team_id,
        next_gw=next_gw,
        horizon=effective_horizon,
        expanded=expanded,
        chips={"fh": use_fh, "wc": use_wc, "bb": use_bb, "tc": use_tc},
        projections_path=proj_file,
        bank=bank,
        free_transfers=free_transfers,
    )

    return {
        "options": options,
        "my_data": my_data,
        "summary": summary,
        "next_gw": next_gw,
        "effective_horizon": effective_horizon,
        "expanded": expanded,
        "bank": bank,
        "free_transfers": free_transfers,
        "proj_file": proj_file,
    }


def solve_squad(
    projections_path: str | Path,
    team_id: int | None = None,
    horizon: int = 10,
    chips: dict[str, list[int]] | None = None,
    wildcard: bool = False,
    preseason: bool = False,
    vendor_dir: Path | None = None,
    output_dir: Path = Path("data/output/solver"),
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Execute multi-period squad optimization using vendored open-fpl-solver.

    Args:
        projections_path: Path to Solio player projections CSV.
        team_id: Optional FPL manager team ID.
        horizon: Base planning horizon (default 10).
        chips: Dictionary of scheduled chips (e.g. {'fh': [19], 'wc': [8]}).
        wildcard: Force unconstrained wildcard solve on next GW.
        preseason: Solve unconstrained squad from scratch with £100.0m budget.
        vendor_dir: Path to vendored open-fpl-solver directory.
        output_dir: Output directory for saving plans.
        context: Optional pre-computed context from prepare_solve_context.

    Returns:
        Dictionary containing solution, table, fplteam_url, plan_file, and summary.
    """
    from solio_calibrate.io import format_archive_filename

    ctx = context or prepare_solve_context(
        projections_path=projections_path,
        team_id=team_id,
        horizon=horizon,
        chips=chips,
        wildcard=wildcard,
        preseason=preseason,
        vendor_dir=vendor_dir,
    )

    options = ctx["options"]
    my_data = ctx["my_data"]

    from dev.solver import prep_data, solve_multi_period_fpl  # type: ignore[import-not-found]

    processed_data = prep_data(my_data, options)
    solutions = solve_multi_period_fpl(processed_data, options)

    if not solutions:
        raise RuntimeError("HiGHS solver returned no feasible solutions.")

    table = format_solution_table(solutions)
    fplteam_url = generate_fplteam_link(solutions, team_id=team_id)

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    plan_path = out_dir / "squad_plan_latest.csv"

    picks_df = solutions[0]["picks"]
    picks_df.to_csv(plan_path, index=False)

    archive_dir = out_dir / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    archive_filename = format_archive_filename("squad_plan")
    archive_path = archive_dir / archive_filename
    picks_df.to_csv(archive_path, index=False)

    return {
        "solutions": solutions,
        "summary": ctx["summary"],
        "table": table,
        "fplteam_url": fplteam_url,
        "plan_file": plan_path,
        "archive_file": archive_path,
        "effective_horizon": ctx["effective_horizon"],
        "expanded": ctx["expanded"],
        "score": solutions[0].get("score", 0.0),
    }
