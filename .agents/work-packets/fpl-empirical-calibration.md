# Active Task: FPL Empirical Form Calibration Engine & Normalization

- **Status:** In Progress
- **Objective:** Implement match-level xG/xGC aggregation, leave-one-out opponent normalization, zero-GW fallback, and season progression CLI
- **Acceptance:** Tests pass with verify gate, calibrate `/home/jubileez/Downloads/team_strengths (1).csv` with 50/50 blend to upload-ready CSV
- **Issue/Ticket:** ADR-0001

## Work Packet (SFDBN)

- **Status:** Complete
- **Files:** `src/solio_calibrate/client.py`, `src/solio_calibrate/calibrate.py`, `src/solio_calibrate/cli.py`, `skills/calibrate-team-strength/SKILL.md`, `CONTEXT.md`, `docs/adr/0001-fpl-empirical-strength-normalization.md`, `tests/`
- **Decisions:** ADR-0001 (equal G/xG weighting, Bayesian shrinkage opponent difficulty, zero-GW 100% Solio fallback, venue-neutralized baseline, single empirical home advantage factor)
- **Blocked:** None
- **Next:** User review and upload to Solio web planner

## Todo
- [x] Implement FPL client live gameweek fetching & xG match aggregation in `client.py`
- [x] Implement match-level leave-one-out opponent normalization and zero-GW fallback in `calibrate.py`
- [x] Implement single league-wide Home Advantage Factor ($h$) with Bayesian shrinkage in `calibrate.py`
- [x] Implement venue neutralization in team empirical form in `client.py`
- [x] Update CLI options (`--input`, `--weight`, `--auto-weight`, `--json`, `--output`) in `cli.py`
- [x] Add unit tests for empirical normalization, zero-GW behavior, home advantage, and json CLI in `tests/`
- [x] Author agent skill `skills/calibrate-team-strength/SKILL.md` and retire legacy skill
- [x] Run calibration on `/home/jubileez/Downloads/team_strengths (1).csv`
- [x] Run `bash tests/verify.sh`
- [ ] Solio web planner upload and user verification

## Blockers / Notes
- None
