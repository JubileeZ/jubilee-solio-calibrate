# Active Task: standardize-data-archive

- **Status:** In Progress
- **Objective:** Standardize data/output and data/raw storage with symmetric team_strengths_base.csv and team_strengths_calibrated.csv at roots and matching self-describing ISO timestamped files under archive/
- **Acceptance:** Tests pass; data/output/ and data/raw/ have clean layout; CLI supports raw ingestion with deduplicated archive and output archiving
- **Issue/Ticket:** User request / grill-with-docs

## Work Packet (SFDBN)

- **Status:** In Progress
- **Files:** src/solio_calibrate/io.py, src/solio_calibrate/cli.py, tests/test_io.py, tests/test_cli.py, CONTEXT.md, README.md, AGENTS.md, docs/agents/current-state.md, .agents/skills/calibrate-team-strength/SKILL.md
- **Decisions:** Symmetric base and calibrated naming: data/raw/team_strengths_base.csv and data/output/team_strengths_calibrated.csv; self-describing archives (team_strengths_base_... and team_strengths_calibrated_...); deduplicate raw ingestion by content diff; explicit -o bypasses archive
- **Blocked:** None
- **Next:** Commit changes and push to remote


## Todo
- [x] Update CONTEXT.md with domain terms
- [x] Implement archive and raw ingestion helpers in io.py
- [x] Wire CLI to use raw ingestion and output archiving
- [x] Migrate and clean up loose data/output files
- [x] Adopt symmetric team_strengths_base and team_strengths_calibrated naming
- [x] Add unit tests for archiving and ingestion
- [x] Update documentation (README, SKILL.md, current-state.md, AGENTS.md)
- [x] Run verify.sh gate
- [ ] Push changes to remote

## Blockers / Notes
- None
