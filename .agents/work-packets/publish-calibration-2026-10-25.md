# Active Task: Publish Calibration 2026-10-25

- **Status:** In Progress
- **Objective:** Commit and push refreshed Solio team strengths and archive snapshot.
- **Acceptance:** Verify output schema and archive, pass tests/verify.sh, publish data to origin/main, and close this packet.
- **Issue/Ticket:** Calibration skill run

## Work Packet (SFDBN)

- **Status:** In Progress
- **Files:** data/raw/team_strengths_base.csv, data/raw/archive/team_strengths_base_2026-10-25_11-19-37.csv, data/output/team_strengths_calibrated.csv, data/output/archive/team_strengths_calibrated_2026-10-25_11-19-38.csv, tests/test_cli.py
- **Decisions:** Ingest supplied team_strengths.csv; GW1-GW7 completed plus 5 GW8 provisional matches; auto-weight; empirical home factor 9.12%.
- **Blocked:** None
- **Next:** Verify gate, commit and push data, then close work packet.

## Todo
- [x] Run calibration CLI
- [x] Verify gate and tests
- [ ] Commit and push calibration data
- [ ] Close and delete work packet

## Blockers / Notes
- None
