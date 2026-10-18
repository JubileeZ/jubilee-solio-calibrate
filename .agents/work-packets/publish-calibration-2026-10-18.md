# Active Task: Publish GW7 team strength calibration

- **Status:** In Progress
- **Objective:** Commit and push refreshed Solio team strengths and archive snapshot.
- **Acceptance:** Calibrated CSV and archive are verified, delivery gate passes, commits are pushed to origin/main.
- **Issue/Ticket:** None

## Work Packet (SFDBN)

- **Status:** In progress
- **Files:** data/output/team_strengths_calibrated.csv; data/output/archive/team_strengths_calibrated_2026-10-18_12-25-06.csv; data/raw/team_strengths_base.csv; data/raw/archive/team_strengths_base_2026-10-18_12-25-05.csv
- **Decisions:** Ingested new base strengths from Downloads; calibrated against GW1-GW7 (including 5 provisional matches); dynamic auto-weight 0.37.
- **Blocked:** None
- **Next:** Verify delivery gate, commit data, push to origin/main, close packet.

## Todo
- [x] Ingest and archive base strengths
- [x] Run calibration with auto-weight and force-refresh
- [ ] Run verify gate
- [ ] Commit and push calibrated outputs and archives
- [ ] Close work packet

## Blockers / Notes
- None
