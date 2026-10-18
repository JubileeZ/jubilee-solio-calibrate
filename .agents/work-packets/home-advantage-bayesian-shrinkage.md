# Active Task: Home Advantage Empirical Bayes Shrinkage

- **Status:** In Progress
- **Objective:** Update calculate_home_advantage_factor to use 5-season post-COVID EPL prior (0.0915) and full-season Empirical Bayes shrinkage (pseudo_matches=380.0), and record research context in repo.
- **Acceptance:** Research doc created, CONTEXT.md and ADR 0001 updated, calibrate.py and tests updated, calibrated CSV refreshed, verify.sh passes.
- **Issue/Ticket:** None

## Work Packet (SFDBN)

- **Status:** In progress
- **Files:** src/solio_calibrate/calibrate.py; tests/test_calibrate.py; docs/research/home-advantage-bayesian-shrinkage.md; CONTEXT.md; docs/adr/0001-fpl-empirical-strength-normalization.md; docs/agents/current-state.md; data/output/team_strengths_calibrated.csv
- **Decisions:** Set prior_factor=0.0915 (5-yr post-COVID EPL pooled mean) and pseudo_matches=380.0 (full-season Empirical Bayes shrinkage); retain direct pooled sum in calculate_home_advantage_factor.
- **Blocked:** None
- **Next:** Implement changes, run verify.sh, commit and push, close packet.

## Todo
- [x] Add research reference doc `docs/research/home-advantage-bayesian-shrinkage.md`
- [x] Update `CONTEXT.md`, `docs/adr/0001-fpl-empirical-strength-normalization.md`, and `docs/agents/current-state.md`
- [x] Update `tests/test_calibrate.py` (TDD red test)
- [x] Update `src/solio_calibrate/calibrate.py` (TDD green test)
- [x] Refresh `data/output/team_strengths_calibrated.csv`
- [x] Run `uv run ruff check .` and `bash tests/verify.sh`
- [ ] Commit, push, and close work packet

## Blockers / Notes
- None
