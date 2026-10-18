# Active Task: Per-team matches-played auto-weighting

- **Status:** In Progress
- **Objective:** Implement team-specific blend weights based on individual match sample size (n / 19), update domain docs and ADR 0001, and refresh calibration data.
- **Acceptance:** calibrate.py and cli.py support per-team weights, unit tests pass, CONTEXT.md and ADR 0001 updated, delivery gate passes, calibrated data refreshed and pushed.
- **Issue/Ticket:** None

## Work Packet (SFDBN)

- **Status:** In progress
- **Files:** src/solio_calibrate/calibrate.py; src/solio_calibrate/cli.py; tests/test_calibrate.py; tests/test_cli.py; CONTEXT.md; docs/adr/0001-fpl-empirical-strength-normalization.md
- **Decisions:** Auto-weight scales per-team by matches played (w_i = min(n_i / 19, 1.0)); manual --weight remains uniform override; JSON payload includes team_weights.
- **Blocked:** None
- **Next:** Implement changes to calibrate.py and cli.py, run tests.

## Todo
- [x] Update src/solio_calibrate/calibrate.py with team_weights support in CalibrationConfig
- [x] Update src/solio_calibrate/cli.py to compute per-team weights and emit team_weights in JSON
- [x] Update CONTEXT.md and ADR 0001
- [x] Update and expand unit tests
- [x] Run verify gate
- [x] Re-run calibration and commit data
- [ ] Close work packet

## Blockers / Notes
- None
