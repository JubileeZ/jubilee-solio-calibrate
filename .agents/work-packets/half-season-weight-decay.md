# Active Task: half-season-weight-decay

- **Status:** In Progress
- **Objective:** Implement linear half-season auto-weight decay (GW 1-19) so GW 20 onward runs on 100% empirical season stats
- **Acceptance:** Tests verify GW 0 is 0.0, GW 19 is 1.0, GW 20+ is 1.0; output generated with new weighting for GW 5

## Work Packet (SFDBN)

- **Status:** In Progress
- **Files:** src/solio_calibrate/calibrate.py, tests/test_calibrate.py, data/output/team_strengths_calibrated.csv
- **Decisions:** Linear progression min(1.0, max_finished_gw / 19.0)
- **Blocked:** None
- **Next:** Commit changes and complete work packet

## Todo
- [ ] Implement and verify linear half-season auto-weight decay

## Blockers / Notes
- None
