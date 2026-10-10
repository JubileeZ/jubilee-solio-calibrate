# jubilee-solio-calibrate

Adjust and calibrate Solio team attack and defense strengths (`Goals`, `Goals Conceded`) using official Fantasy Premier League (FPL) API stats and user preferences.

## Usage

```bash
# Run tests
uv run pytest

# Run linter
uv run ruff check .

# Run calibration CLI
uv run solio-calibrate --input data/raw/team_strengths.csv --output data/output/team_strengths_calibrated.csv
```
