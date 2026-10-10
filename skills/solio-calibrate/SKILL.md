---
name: solio-calibrate
description: Adjust and calibrate Solio team attack and defense strengths using official FPL API stats and user preferences. Use when calibrating team strengths, applying team boosts or global climate scales, and generating updated CSVs for re-uploading to the Solio web planner.
---

# Solio Calibrate Skill

Adjust and calibrate Solio team attack and defense strengths (`Goals`, `Goals Conceded`) using official FPL API stats and custom user preferences.

## When to use

- Calibrating original Solio team strength CSV export with real-time FPL match data
- Adjusting scoring climate (global attack/defense scaling)
- Applying team-specific multipliers to reflect subjective expectations or tactical changes
- Producing upload-ready CSV for the Solio web planner

## CLI Command

```bash
uv run solio-calibrate \
  --input data/raw/team_strengths.csv \
  --output data/output/team_strengths_calibrated.csv \
  --weight 0.30 \
  --recent-weight 0.50
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `-i, --input` | `data/raw/team_strengths.csv` | Path to original Solio team strength export |
| `-o, --output` | `data/output/team_strengths_calibrated.csv` | Destination path for calibrated CSV |
| `-w, --weight` | `0.30` | Weight [0.0-1.0] for FPL match stats vs Solio base |
| `--recent-weight` | `0.50` | Weight [0.0-1.0] for recent gameweek form |
| `--attack-scale` | `1.00` | Global multiplier for all team `Goals` |
| `--defense-scale` | `1.00` | Global multiplier for all team `Goals Conceded` |
| `--team-boost` | `[]` | Team multiplier in `TEAM:STAT:MULT` format (e.g. `ARS:goals:1.10`) |
| `--force-refresh` | `false` | Force fresh download from FPL API ignoring local cache |
| `--offline` | `false` | Use local cache without network requests |

## Workflow

1. **Verify input:** Confirm input file exists and has headers `Team,Goals,Goals Conceded`.
2. **Execute calibration:** Run `uv run solio-calibrate` with desired weights or team boosts.
3. **Inspect results:** Verify output CSV has all 20 teams and valid 3-decimal float numbers.
4. **Safety check:** Ensure original file in `data/raw/` was never modified.
