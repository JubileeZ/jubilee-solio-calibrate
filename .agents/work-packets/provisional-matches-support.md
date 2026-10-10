# Active Task: Provisional Matches Support in Calibration & Skill

- **Status:** In Progress
- **Objective:** Support provisionally finished FPL matches in calibration while highlighting them in the CLI/skill report dialogue without altering clean CSV schema.
- **Acceptance:** Matches with finished_provisional=True are included in match records and max_gw; provisional matches are flagged in JSON and CLI summary; skill protocol highlights provisional matches in chat; all tests and verify gate pass.
- **Issue/Ticket:** User request

## Work Packet (SFDBN)

- **Status:** Complete
- **Files:** src/solio_calibrate/client.py, src/solio_calibrate/cli.py, tests/test_client.py, tests/test_cli.py
- **Decisions:** Treat `finished or finished_provisional` (with scores not None) as completed matches; add `is_provisional` flag to match records; report provisional list in CLI and JSON summaries; keep CSV schema strictly Team,Goals,Goals Conceded.
- **Blocked:** None
- **Next:** User reporting.

## Todo
- [x] Update client.py to accept finished_provisional fixtures
- [x] Update cli.py to account for provisional gameweeks and report provisional matches in summary / JSON
- [x] Add tests in test_client.py and test_cli.py
- [x] Run verify gate and remove untracked temporary debris if any
- [ ] Final verification and user review

## Blockers / Notes
- None
