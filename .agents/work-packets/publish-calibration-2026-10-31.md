# Active Task: Publish GW8 team strength calibration

- **Status:** In Progress
- **Objective:** Commit and push refreshed Solio team strengths and archive snapshot.
- **Acceptance:** Verify gate passes; calibrated output and snapshots are committed and pushed to origin/main.
- **Issue/Ticket:** N/A

## Work Packet (SFDBN)

- **Status:** In Progress
- **Files:** data/output/team_strengths_calibrated.csv; data/output/archive/team_strengths_calibrated_2026-10-31_20-13-30.csv; data/raw/team_strengths_base.csv; data/raw/archive/team_strengths_base_2026-10-31_20-13-29.csv
- **Decisions:** Used --auto-weight and --force-refresh; input CSV was ingested as the active base.
- **Blocked:** None
- **Next:** Run verify gate, commit data and packet, then push origin/main.

## Todo
- [x] Refresh FPL data and generate calibrated output plus archives.
- [ ] Verify, commit, and push calibration.

## Blockers / Notes
- None
