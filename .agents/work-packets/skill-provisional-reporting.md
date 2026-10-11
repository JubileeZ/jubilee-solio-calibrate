# Active Task: skill-provisional-reporting

- **Status:** In Progress
- **Objective:** Update skill with default force-refresh, provisional match reporting, GW coverage, and 20-team summary template
- **Acceptance:** Tests pass via `bash tests/verify.sh`; SKILL.md and CONTEXT.md updated; calibrated outputs refreshed
- **Issue/Ticket:** /grill-with-docs skill update

## Work Packet (SFDBN)

- **Status:** In Progress
- **Files:** .agents/skills/calibrate-team-strength/SKILL.md, CONTEXT.md, docs/agents/current-state.md, data/output/, data/raw/
- **Decisions:** Use --force-refresh by default in agent skill; display GW coverage number prominently; report all 20 teams with latest available status; add report template to SKILL.md
- **Blocked:** None
- **Next:** Run tests/verify.sh and commit

## Todo
- [x] Update .agents/skills/calibrate-team-strength/SKILL.md with default force-refresh, GW coverage, and 20-team template
- [x] Update CONTEXT.md with Provisional Match and Gameweek Coverage definitions
- [x] Update docs/agents/current-state.md with skill changes
- [x] Re-run calibration skill with live provisional GW6 data
- [ ] Verify harness and project tests pass via tests/verify.sh
- [ ] Close work packet and push
