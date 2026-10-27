# Active Task: Publish Calibration 2026-10-27

- **Status:** In Progress
- **Objective:** Commit and push refreshed Solio team strengths and archive snapshot.
- **Acceptance:** Verify output schema and archive, pass tests/verify.sh, publish data to origin/main, and close this packet.
- **Issue/Ticket:** Calibration skill run

## Work Packet (SFDBN)

- **Status:** In Progress
- **Files:** data/raw/team_strengths_base.csv, data/raw/archive/team_strengths_base_2026-10-27_22-56-44.csv, data/output/team_strengths_calibrated.csv, data/output/archive/team_strengths_calibrated_2026-10-27_22-56-44.csv
- **Decisions:** Ingest supplied team_strengths.csv; GW1-GW8 fully completed (0 provisional matches); auto-weight 0.42; empirical home factor 8.91%.
- **Blocked:** None
- **Next:** Verify gate, commit and push data, then close work packet.

## Todo
- [x] Run calibration CLI
- [x] Verify gate and tests
- [ ] Commit and push calibration data
- [ ] Close and delete work packet

## Blockers / Notes
- None
