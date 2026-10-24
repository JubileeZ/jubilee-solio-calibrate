# Active Task: Publish Calibration 2026-10-24

- **Status:** In Progress
- **Objective:** Commit and push refreshed Solio team strengths and archive snapshot.
- **Acceptance:** Verify output schema and archive, pass tests/verify.sh, publish data to origin/main, and close this packet.
- **Issue/Ticket:** Calibration skill run

## Work Packet (SFDBN)

- **Status:** In Progress
- **Files:** data/raw/team_strengths_base.csv, data/raw/archive/, data/output/team_strengths_calibrated.csv, data/output/archive/
- **Decisions:** Use supplied team_strengths.csv with automatic gameweek weighting and a forced live FPL refresh.
- **Blocked:** None
- **Next:** Run calibration, verify artifacts, run gate, and publish.

## Todo
- [ ] Run calibration and verify generated CSV/archive.
- [ ] Run bash tests/verify.sh and publish to origin/main.
- [ ] Delete packet after publication.

## Blockers / Notes
- None
