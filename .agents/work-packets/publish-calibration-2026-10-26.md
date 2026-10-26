# Active Task: Publish GW8 Solio Team Strength Calibration Refresh

- **Status:** In Progress
- **Objective:** Commit and push refreshed Solio team strengths and archive snapshot.
- **Acceptance:** Calibrate against forced-refresh official FPL data, resolve cache-dependent test expectation, verify the output and delivery gate, commit calibration files, and push `origin/main`.
- **Issue/Ticket:** None

## Work Packet (SFDBN)

- **Status:** Test expectation resolved with deterministic mock; gate passing
- **Files:** `data/output/team_strengths_calibrated.csv`, `data/output/archive/team_strengths_calibrated_2026-10-26_02-03-15.csv`, `tests/test_cli.py`, `.agents/work-packets/publish-calibration-2026-10-26.md`
- **Decisions:** Made `test_cli_auto_weight_per_team` deterministic with monkeypatched match records and fixtures to eliminate cache dependence; preserved 10-match GW8 calibrated output.
- **Blocked:** None
- **Next:** Verify gate, commit calibration and test fix, close work packet, and push upstream.

## Todo
- [x] Run forced-refresh calibration and review coverage and CSV artifacts.
- [x] Resolve cache-dependent test failure and rerun delivery gate.
- [ ] Close work packet and push upstream.

## Blockers / Notes
- Ruff and tests/verify.sh passing.
