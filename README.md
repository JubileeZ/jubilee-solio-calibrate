# jubilee-solio-calibrate

Adjust and calibrate Solio team attack and defense strengths (`Goals`, `Goals Conceded`) using official Fantasy Premier League (FPL) API stats and user preferences.

## Usage

```bash
# Run tests
uv run pytest

# Run linter
uv run ruff check .

# Run calibration CLI
uv run solio-calibrate
```

By default, the calibrated CSV is written to `data/output/team_strengths_calibrated.csv`, with an archive snapshot saved to `data/output/archive/team_strengths_calibrated_YYYY-MM-DD_HH-MM-SS.csv` (deduplicated by SHA256). The active base strength is read from `data/raw/team_strengths_base.csv`. When a new base strength CSV is supplied via `--input`, it is promoted to `data/raw/team_strengths_base.csv` after archiving the prior base file to `data/raw/archive/team_strengths_base_YYYY-MM-DD_HH-MM-SS.csv` (if contents changed). Pass `--output` to override the output path.

## Architecture & Boundaries

- **Single Purpose**: This project solely calibrates team-level attack/defense ratings and computes the empirical league-wide Home Advantage Factor for upload to the Solio web planner.
- **Squad Optimization**: FPL squad selection, transfer planning, player minutes modeling, and MILP solvers belong strictly to sibling repository `fpl-jubilee-ascent` (via `.agents/skills/transfer-planner`). See [ADR 0002](docs/adr/0002-scope-boundary-calibration-vs-squad-solver.md).
