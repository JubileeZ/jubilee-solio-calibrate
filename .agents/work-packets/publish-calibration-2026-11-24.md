# Active Task: Publish calibration 2026-11-24

- **Status:** In Progress
- **Objective:** Commit and push refreshed Solio team strengths and archive snapshot.
- **Acceptance:** Calibrated CSV and archive verified, delivery gate passes, changes pushed to origin/main, packet removed.
- **Issue/Ticket:** Calibration skill run

## Work Packet (SFDBN)

- **Status:** In Progress
- **Files:** `data/raw/team_strengths_base.csv`, `data/raw/archive/team_strengths_base_2026-11-24_20-44-43.csv`, `data/output/team_strengths_calibrated.csv`, `data/output/archive/team_strengths_calibrated_2026-11-24_20-44-44.csv`, this packet
- **Decisions:** Use supplied Solio export with automatic seasonal weighting and fresh FPL data.
- **Blocked:** None
- **Next:** Commit and push, then close packet.

## Todo
- [x] Run calibration and verify CSV outputs
- [ ] Run `bash tests/verify.sh`
- [ ] Commit, push, and remove this packet

## Blockers / Notes
- None
