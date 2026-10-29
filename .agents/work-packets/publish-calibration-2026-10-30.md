# Active Task: Publish GW8 Solio team strengths

- **Status:** In Progress
- **Objective:** Commit and push refreshed Solio team strengths and archive snapshot.
- **Acceptance:** Verify the calibrated CSV and archives, pass `bash tests/verify.sh`, commit the data and packet, push to `origin/main`, then remove and push the packet closure.
- **Issue/Ticket:** Calibration run 2026-10-30

## Work Packet (SFDBN)

- **Status:** Calibration completed; publication in progress
- **Files:** `data/output/team_strengths_calibrated.csv`, `data/output/archive/team_strengths_calibrated_2026-10-30_00-11-22.csv`, `data/raw/team_strengths_base.csv`, `data/raw/archive/team_strengths_base_2026-10-30_00-11-21.csv`
- **Decisions:** Used official FPL API data with `--auto-weight --force-refresh`; input CSV promoted to raw base. GW1–GW8 coverage, 42.11% FPL weight, 8.91% home factor, zero provisional matches.
- **Blocked:** None
- **Next:** Validate output and archives, run the project verify gate, commit and push, then delete this packet and push its closure.

## Todo
- [x] Run live GW8 calibration from supplied CSV.
- [ ] Verify CSV schema, values, archive snapshots, and project gate.
- [ ] Commit and push calibration data to `origin/main`.
- [ ] Delete this packet, commit closure, and push.

## Blockers / Notes
- None
