---
name: solve-squad
description: Optimize FPL squad transfers, lineups, captaincy, and chips using Solio player projections and the open-fpl-solver HiGHS MILP model. Use when solving an optimal squad, planning multi-gameweek transfers, or generating an interactive FPL.Team planner link.
---

# Solve FPL Squad

Solve deterministic multi-period Fantasy Premier League squad optimization problems using player projections exported from the Solio web planner and the HiGHS Mixed Integer Linear Programming (MILP) solver engine.

## When to use

- Optimizing multi-gameweek FPL transfer plans, lineups, bench order, and captaincy from Solio player projections.
- Generating an interactive [fpl.team](https://fpl.team) URL encoding the full gameweek-by-gameweek plan for visual tweaking.
- Solving Wildcard, Free Hit, Bench Boost, or Triple Captain chip strategies.
- Running unconstrained preseason or wildcard team generation with £100.0m budget.

## Execution

### CLI Runner

```bash
# Standard solve using FPL Team ID
uv run solio-solve --team-id <TEAM_ID> --horizon 10

# Solve with scheduled chips (auto-expands horizon if chip is beyond default)
uv run solio-solve --team-id <TEAM_ID> --fh 19

# Solve unconstrained / preseason squad from scratch (£100.0m budget)
uv run solio-solve --preseason --horizon 10 -y

# Pass newly downloaded Solio player projections CSV
uv run solio-solve --team-id <TEAM_ID> --projections "/path/to/solio.csv"
```

### CLI Parameters

| Flag | Default | Description |
|------|---------|-------------|
| `--team-id` | `None` | Official FPL manager team ID to fetch current squad, bank, and free transfers |
| `-p, --projections` | `data/projections/solio_projections.csv` | Path to Solio player projections CSV (automatically ingested and deduplicated via SHA256) |
| `--horizon` | `10` | Planning horizon in gameweeks (auto-expands if any scheduled chip exceeds it) |
| `--fh` | `[]` | Schedule Free Hit chip in specified gameweek (can be passed multiple times) |
| `--wc` | `[]` | Schedule Wildcard chip in specified gameweek |
| `--bb` | `[]` | Schedule Bench Boost chip in specified gameweek |
| `--tc` | `[]` | Schedule Triple Captain chip in specified gameweek |
| `--preseason` | `false` | Solve unconstrained squad from scratch with £100.0m budget |
| `--wildcard` | `false` | Solve unconstrained wildcard squad for upcoming gameweek |
| `-o, --output` | `data/output/solver` | Directory to save squad plan CSV and timestamped archives |
| `-y, --yes` | `false` | Skip interactive confirmation prompt and execute solver immediately |

## Mandatory Pre-Execution Confirmation

Before executing the solver, **always confirm settings with the user first**:
1. Present the configuration summary:
   - **FPL Team ID**: (or Preseason / Unconstrained)
   - **Starting Gameweek**: next upcoming GW
   - **Planning Horizon**: e.g., 10 Gameweeks (or expanded count if chip scheduled)
   - **Scheduled Chips**: e.g., `FH in GW 19`
   - **Active Projections File**: `data/projections/solio_projections.csv`
2. If a planned chip falls beyond the base horizon (e.g. Free Hit in GW 19 when horizon is 10), state that the horizon is auto-expanded to cover GW 19 and confirm with the user before running.

## Agent Reporting Protocol

When reporting solver results to the user:
1. **Settings Confirmation**: Confirm the Team ID, gameweek horizon, and active projections dataset used.
2. **Transfer & Lineup Plan Table**: Present the gameweek-by-gameweek table including:
   - Starting XI with Captain (`(C)`) and Vice-Captain (`(V)`)
   - Bench order (Goalkeeper, Bench 1, 2, 3)
   - Transfers In and Out (or `Roll FT`)
   - Active Chips (if any)
3. **Total Projected Points**: Report total expected points over the planning horizon.
4. **Interactive FPL.Team URL**: Provide the clickable [fpl.team](https://fpl.team) URL so the user can inspect, tweak, and visualize the solution directly in their browser.
5. **Saved Artifacts**: Link to the generated plan CSV in `data/output/solver/squad_plan_latest.csv`.
