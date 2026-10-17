# ADR 0002: Scope Boundary — Team Strength Calibration vs Sibling Squad Solver

## Context
A prior feature attempt integrated Solio Analytics' `open-fpl-solver` (HiGHS MILP), player projections I/O, a `solio-solve` CLI, and squad solving skills into this repository. This introduced over 7,000 lines of vendored code, heavy mathematical solver dependencies (`highspy`), and duplicated functionality already maintained in sibling repository `fpl-jubilee-ascent`.

## Decision
1. **Single Responsibility**: `jubilee-solio-calibrate` is strictly scoped to calibrating team attack/defense ratings (`Goals`, `Goals Conceded`) against official FPL match data and exporting upload-ready CSVs for the Solio web planner.
2. **Anti-Goal (No Squad Solvers / Player Projections)**: Never introduce squad optimization, player-level minutes modeling, or transfer planning into this codebase.
3. **Sibling Ownership**: Sibling repository `fpl-jubilee-ascent` is the sole owner of FPL squad optimization, MILP solving, and transfer planning (`.agents/skills/transfer-planner`, `commands.solve`, `solver/`).

## Consequences
- Maintains a lightweight, deterministic calibration package with minimal dependencies (`httpx`, `pandas`, `pytest`, `ruff`).
- Avoids cross-repo code duplication and architectural confusion.
- Clarifies boundaries for both human developers and autonomous AI agents.
