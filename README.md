# jubilee-solio-calibrate

Adjust and calibrate Solio team attack and defense strengths (`Goals`, `Goals Conceded`) using official Fantasy Premier League (FPL) API stats, and optimize multi-gameweek squad transfers, lineups, and captaincy from Solio player projections using the HiGHS MILP solver engine.

## Usage

```bash
# Run tests
uv run pytest

# Run linter
uv run ruff check .

# Run team strength calibration CLI
uv run solio-calibrate

# Run squad optimization solver CLI (interactive confirmation)
uv run solio-solve --team-id <YOUR_TEAM_ID> --horizon 10

# Run unconstrained / preseason squad solve
uv run solio-solve --preseason --horizon 10 -y

# Sync vendored open-fpl-solver from upstream
bash scripts/sync-solver.sh
```

### Team Strength Calibration
By default, the calibrated CSV is written to `data/output/team_strengths_calibrated.csv`, with an archive snapshot saved to `data/output/archive/team_strengths_calibrated_YYYY-MM-DD_HH-MM-SS.csv` (deduplicated by SHA256). Active base strength is read from `data/raw/team_strengths_base.csv`.

### Squad Optimization
Reads Solio player projections (`data/projections/solio_projections.csv`), fetches current manager squad and bank via FPL Team ID, executes a multi-gameweek integer linear programming optimization (HiGHS), outputs a terminal transfer plan, and generates an interactive [fpl.team](https://fpl.team) URL encoding the full solution for visual review.
