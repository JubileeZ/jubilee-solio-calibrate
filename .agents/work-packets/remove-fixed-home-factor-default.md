# Active Task: Remove fixed Solio Home Advantage default

- **Status:** In Progress
- **Objective:** Remove fixed Solio Home Advantage default references so skill and CLI do not report a value that may change.
- **Acceptance:** Skill, CLI text/JSON, and glossary do not state a fixed default; calibration math remains unchanged; verify gate passes; changes are committed and pushed.
- **Issue/Ticket:** User request, 2026-10-11

## Work Packet (SFDBN)

- **Status:** Implemented; verification passed
- **Files:** `.agents/skills/calibrate-team-strength/SKILL.md`, `CONTEXT.md`, `src/solio_calibrate/cli.py`, `tests/test_calibrate.py`
- **Decisions:** Remove the default comparison from reports and JSON. Use zero only as the CLI's no-data reporting fallback. Preserve empirical calculation behavior.
- **Blocked:** None
- **Next:** Commit checkpoint, remove this completed packet, then push.

## Todo
- [x] Remove fixed default value references from skill, CLI, and glossary.
- [x] Run verification gate and inspect staged changes.
- [ ] Commit and push.

## Blockers / Notes
- Preserve unrelated pre-existing untracked and deleted files.
