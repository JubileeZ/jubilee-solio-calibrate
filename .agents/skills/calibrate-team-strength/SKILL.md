---
name: calibrate-team-strength
description: Calibrate Solio team attack and defense strengths against empirical FPL match performance, calculate this season's Home Advantage Factor, and commit/push outputs by default. Use when calibrating team strengths, updating Solio CSV exports, or extracting the empirical home/away percentage for Solio web planner.
---

# Calibrate Team Strength

Calibrate Solio team attack and defense strengths (`Goals`, `Goals Conceded`) using official Fantasy Premier League fixture data, underlying chances ($xG, xGC$), and leave-one-out schedule difficulty normalization. Calculates this season's empirical league-wide Home Advantage Factor ($h$).

## When to use

- Calibrating Solio team strength CSV exports with real-time FPL match data
- Extracting the empirical Home Advantage Factor % for entry into the Solio web planner
- Applying venue-neutral strength ratings to avoid double-counting home advantage
- Running automatic seasonal progression weighting based on completed gameweeks

## Execution

Run the calibration engine CLI with `--force-refresh` by default to fetch live FPL fixture data and include all provisionally finished matches:

```bash
uv run solio-calibrate \
  --input "/path/to/team_strengths.csv" \
  --auto-weight \
  --force-refresh \
  --json
```

Or with manual fixed weight:

```bash
uv run solio-calibrate \
  --input "/path/to/team_strengths.csv" \
  --weight 0.50 \
  --force-refresh \
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
| `--force-refresh` | `false` | Force fresh download from FPL API ignoring local cache (always set `true` in agent skill runs to capture provisional matches) |
| `--offline` | `false` | Use local cache without network requests |

## Delivery & Commit-Push Workflow

By default, team strength calibration executes the complete publish cycle upon completion:

1. **Verify CSV Output**: Confirm `data/output/team_strengths_calibrated.csv` and the archive snapshot in `data/output/archive/` exist, conform to the 3-decimal schema, and have valid values.
2. **Create Publish Work Packet**: Create `.agents/work-packets/publish-calibration-YYYY-MM-DD.md` (using current date) from `.agents/work-packet.md.tmpl`:
   - Objective: `Commit and push refreshed Solio team strengths and archive snapshot.`
   - Files: `data/output/team_strengths_calibrated.csv`, `data/output/archive/...` (and `data/raw/...` if ingested).
3. **Verify Gate**: Run `bash tests/verify.sh` to ensure all tests and schema checks pass.
4. **Stage and Commit Data**:
   ```bash
   git add data/output/team_strengths_calibrated.csv data/output/archive/team_strengths_calibrated_*.csv data/raw/team_strengths_base.csv data/raw/archive/team_strengths_base_*.csv .agents/work-packets/publish-calibration-*.md
   git commit -m "data: refresh GW<X> team strength calibration"
   ```
5. **Push Remote**: Push commits to upstream branch:
   ```bash
   git push origin main
   ```
6. **Close & Delete Work Packet**: Remove the temporary work packet file, commit its removal to keep the repo clean, and push:
   ```bash
   rm .agents/work-packets/publish-calibration-*.md
   git add -u .agents/work-packets/
   git commit -m "chore: close calibration refresh packet"
   git push origin main
   ```
7. **Report**: Present the calibration report along with the commit hash and push confirmation.

## Agent Reporting Protocol

When invoking this skill, parse the output and report directly in the response:

1. **Calibrated CSV Location**: Provide clickable file links to the generated output CSV and its archive snapshot.
2. **Gameweek Coverage**: State the numerical gameweek coverage prominently:
   - When provisional matches exist: `**Gameweek Coverage**: GW1–GW<X> (plus <N> provisional matches in GW<Y>)`
   - When no provisional matches exist: `**Gameweek Coverage**: GW1–GW<X> (fully completed)`
3. **Provisional Matches Status**: Explicitly declare provisional match status in all runs:
   - If included: list each provisional fixture and scoreline (e.g. `ARS 2–1 LEE`), confirming live stats were factored into empirical ratings.
   - If none: explicitly state `None (0 provisional matches — all fixtures finalized)`.
4. **Home Advantage Factor**: Clearly state the single empirical Home Advantage Factor % (e.g. `8.32%`) and instruct the user to configure this parameter in the Solio web planner. Do not state or compare against a Solio default value because it can change.
5. **Venue Neutrality Confirmation**: Note that the generated table values are venue-neutral, allowing Solio's planner to apply the home factor on top without double-counting.
6. **Summary Table**: Display a Markdown comparison of original vs calibrated Goals and Goals Conceded for all 20 teams, indicating matches played (e.g. 6 matches vs 5 matches latest available) when a gameweek is partially played.
7. **CSV Schema Verification**: Confirm that the output CSV retains the clean Solio format (`Team,Goals,Goals Conceded`) quantized to 3 decimal places without extra metadata.
8. **Git Publication Confirmation**: Confirm that the calibrated CSV outputs and archive snapshots were verified, committed, and pushed upstream to `origin/main` (including commit hash).

### Report Template

Use this Markdown layout for the user-facing report:

````markdown
### Calibration Complete

The calibrated team strengths have been computed and exported using official FPL match data.

#### 1. Calibrated Output File
- **Calibrated CSV:** [`data/output/team_strengths_calibrated.csv`](file:///home/jubileez/jubilee-solio-calibrate/data/output/team_strengths_calibrated.csv)
- **Archived Snapshot:** [`data/output/archive/team_strengths_calibrated_<TIMESTAMP>.csv`](file:///home/jubileez/jubilee-solio-calibrate/data/output/archive/team_strengths_calibrated_<TIMESTAMP>.csv)

#### 2. Gameweek Coverage
- **Gameweek Coverage:** **GW1–GW<X> (plus <N> provisional matches in GW<Y>)**
- **Blend Weight:** **<WEIGHT>**

#### 3. Provisional Matches Status
- **Provisional Matches:**
  - `<HOME> <H_SCORE>–<A_SCORE> <AWAY>`
  *(or `None (0 provisional matches — all fixtures finalized)`)*

#### 4. Home Advantage Factor
- **Empirical Home Advantage Factor ($h$):** **`<FACTOR>%`**
- Configure this value in the Solio web planner setting.

#### 5. Venue Neutrality Confirmation
The calibrated `Goals` and `Goals Conceded` ratings are venue-neutral, allowing Solio's planner to apply the home factor on top without double-counting.

#### 6. Complete 20-Team Calibration Summary

| Team | Matches Played | Original Goals | Calibrated Goals | Original Conceded | Calibrated Conceded | Data Coverage |
|:---|:---:|:---:|:---:|:---:|:---:|:---|
| **ARS** | 6 | 1.974 | **1.871** | 0.890 | **0.815** | GW1–GW6 (Provisional) |
| ... | ... | ... | ... | ... | ... | ... |

#### 7. CSV Schema Verification
The exported CSV conforms strictly to Solio's standard schema (`Team,Goals,Goals Conceded`) quantized to 3 decimal places without extra metadata.

#### 8. Git Publication Status
- **Commit:** `<COMMIT_HASH>` (`data: refresh GW<X> team strength calibration`)
- **Remote:** Pushed to `origin/main`
````
