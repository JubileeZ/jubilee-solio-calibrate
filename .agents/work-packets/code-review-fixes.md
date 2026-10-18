# Active Task: code-review-fixes

- **Status:** In Progress
- **Objective:** Address Standards and Spec code-review findings: add CLI summary reminder, make skill links portable and DRY, and align glossary vocabulary.
- **Acceptance:** Tests pass, ruff passes, verify.sh passes, and changes committed.
- **Issue/Ticket:** None

## Work Packet (SFDBN)

- **Status:** In Progress
- **Files:** `src/solio_calibrate/cli.py`, `tests/test_cli.py`, `.agents/skills/calibrate-team-strength/SKILL.md`, `docs/research/solio-solver-rules-variance-constraints.md`, `docs/agents/current-state.md`
- **Decisions:** Include planner rules reminder in CLI output; use portable relative links in SKILL.md; use canonical Solio Planner Rules vocabulary.
- **Blocked:** None
- **Next:** Run tests, verify gate, commit and push.

## Todo
- [x] Add planner rules reminder to CLI summary and JSON
- [x] Add test in test_cli.py for CLI reminder
- [x] Make SKILL.md links portable and eliminate rule duplication
- [x] Align vocabulary with Solio Planner Rules in research note and current-state.md
- [ ] Run verify gate
- [ ] Commit and push
- [ ] Close work packet

## Blockers / Notes
- None
