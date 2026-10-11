---
name: calibrate-team-strength
description: Calibrate Solio team attack and defense strengths against empirical FPL match performance and calculate this season's Home Advantage Factor. Use when calibrating team strengths, updating Solio CSV exports, or extracting the empirical home/away percentage for Solio web planner.
---

# Calibrate Team Strength

Calibrate Solio team attack and defense strengths (`Goals`, `Goals Conceded`) using official Fantasy Premier League fixture data, underlying chances ($xG, xGC$), and leave-one-out schedule difficulty normalization. Calculates this season's empirical league-wide Home Advantage Factor ($h$).

## When to use

- Calibrating Solio team strength CSV exports with real-time FPL match data
- Extracting the empirical Home Advantage Factor % for entry into the Solio web planner
- Applying venue-neutral strength ratings to avoid double-counting home advantage
- Running automatic seasonal progression weighting based on completed gameweeks

## Execution

Run the calibration engine CLI:

```bash
uv run solio-calibrate \
  --input "/path/to/team_strengths.csv" \
  --weight 0.50 \
  --json
```

Or with automatic season progression:

```bash
uv run solio-calibrate \
  --input "/path/to/team_strengths.csv" \
  --auto-weight \
  --json
```

### CLI Parameters

| Flag | Default | Description |
|------|---------|-------------|
| `-i, --input` | `data/raw/team_strengths_base.csv` | Path to original Solio team strength CSV export (automatically archived to `data/raw/archive/` and promoted to active base strength if a new file is supplied) |
| `-o, --output` | `data/output/team_strengths_calibrated.csv` | Destination path for calibrated CSV; defaults to canonical latest output while archiving each run to `data/output/archive/team_strengths_calibrated_YYYY-MM-DD_HH-MM-SS.csv` |
| `--no-ingest` | `false` | Do not promote or archive new input into `data/raw/team_strengths_base.csv` |
| `--ingest-raw` | `false` | Force promoting and archiving input into `data/raw/` even if `--output` is specified |
| `-w, --weight` | `0.50` | Blend weight [0.0–1.0] for FPL empirical form vs Solio base |
| `--auto-weight` | `false` | Dynamically scale weight based on completed gameweeks (0.0 if unplayed) |
| `--max-gameweek` | `None` | Upper bound gameweek to include |
| `--json` | `false` | Emit machine-readable JSON summary payload to stdout |
| `--force-refresh` | `false` | Force fresh download from FPL API ignoring local cache |
| `--offline` | `false` | Use local cache without network requests |

## Agent Reporting Protocol

When invoking this skill, parse the output and report directly in the response:

1. **Calibrated CSV Location**: Provide the clickable file link to the generated output CSV.
2. **Home Advantage Factor**: Clearly state the single empirical Home Advantage Factor % (e.g. `8.32%`) and instruct the user to configure this parameter in the Solio web planner. Do not state or compare against a Solio default value because it can change.
3. **Venue Neutrality Confirmation**: Note that the generated table values are venue-neutral, allowing Solio's planner to apply the home factor on top without double-counting.
4. **Summary Table**: Display a concise Markdown comparison of original vs calibrated Goals and Goals Conceded for key teams.
5. **Provisional Matches Highlight**: If any matches were included provisionally (`provisional_matches` in JSON
  summary, e.g. games that just finished on the pitch before official FPL bonus lock), explicitly highlight them to
  the user in the response chat dialogue (e.g. fixture and scoreline). Confirm that the output CSV retains the clean
  Solio format (`Team,Goals,Goals Conceded`) without extra metadata.
