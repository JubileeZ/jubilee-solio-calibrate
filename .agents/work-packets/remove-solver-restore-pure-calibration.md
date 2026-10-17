# Active Task: remove-solver-restore-pure-calibration

- **Status:** In Progress
- **Objective:** Remove vendored solver, solver adapter, projections I/O, solve CLI, solve-squad skill, and solver documentation to restore pure team strength calibration scope.
- **Acceptance:** All solver code, vendor files, and tests removed; pyproject.toml restored; verify.sh passes with 0 failures; clean commit created.
- **Issue/Ticket:** User request

## Work Packet (SFDBN)

- **Status:** Solver files removed, documentation sanitized, tests verified passing
- **Files:**
  - vendor/open-fpl-solver/
  - src/solio_calibrate/solver/
  - src/solio_calibrate/solve_cli.py
  - src/solio_calibrate/projections.py
  - scripts/sync-solver.sh
  - data/projections/
  - data/output/solver/
  - tests/test_solve_cli.py
  - tests/test_solver_adapter.py
  - tests/test_projections.py
  - .agents/skills/solve-squad/
  - docs/adr/0002-vendor-open-fpl-solver-adapter.md
  - pyproject.toml
  - uv.lock
  - CONTEXT.md
  - ROADMAP.md
  - docs/agents/current-state.md
  - AGENTS.md
  - README.md
  - .gitignore
- **Decisions:** Squad solver and player projections belong strictly in fpl-jubilee-ascent (transfer-planner); jubilee-solio-calibrate retains only pure Solio team strength calibration.
- **Blocked:** None
- **Next:** Stage removal commit, verify gate, close packet, and push to origin/main

## Todo
- [x] Remove solver files, vendor directories, data, tests, and skills
- [x] Update pyproject.toml and regenerate lockfile
- [x] Clean documentation (ADR 0002, CONTEXT.md, ROADMAP.md, current-state.md, README.md, AGENTS.md, .gitignore)
- [x] Run verify gate and pass all tests
- [ ] Remove completed work packet file and finalize cleanup checkpoint

## Blockers / Notes
- None
