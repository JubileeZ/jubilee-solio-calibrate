# Active Task: publish-calibration-2026-10-15

- **Status:** In Progress
- **Objective:** Commit and push refreshed Solio team strengths and archive snapshot.
- **Acceptance:** Calibrated team strengths and archived raw/output data verified and committed.
- **Issue/Ticket:** /calibrate-team-strength

## Work Packet (SFDBN)

- **Status:** In Progress
- **Files:** data/output/team_strengths_calibrated.csv, data/output/archive/team_strengths_calibrated_2026-10-15_20-17-33.csv, data/raw/team_strengths_base.csv, data/raw/archive/team_strengths_base_2026-10-15_20-17-30.csv
- **Decisions:** Ingest user input CSV, calibrate with GW6 data (weight 0.32), archive snapshots.
- **Blocked:** None
- **Next:** Run tests/verify.sh gate and commit data files.

## Todo
- [x] Ingest raw input CSV and archive prior base
- [x] Run calibration with live provisional FPL stats
- [x] Verify data output files
- [ ] Run test verification gate
- [ ] Commit and push upstream

## Blockers / Notes
- None
