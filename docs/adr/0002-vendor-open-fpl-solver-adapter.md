# ADR 0002: Vendoring open-fpl-solver with In-Tree Adapter

## Context
We need to provide deterministic FPL squad optimization based on Solio player projections. The official open-source solver from Solio Analytics (`solioanalytics/open-fpl-solver`) implements a multi-period HiGHS MILP tailored to Solio's CSV schema. However, upstream declares `requires-python = ">=3.14"` in its packaging metadata, preventing direct git installation via `uv` on stable Python releases. Additionally, git submodules introduce friction across environments and CI runners.

## Decision
1. **In-Tree Vendoring**: Vendor `open-fpl-solver` under `vendor/open-fpl-solver/` and provide `scripts/sync-solver.sh` for one-command upstream updates.
2. **Adapter Architecture**: Build `src/solio_calibrate/solver/` as a clean adapter interfacing with the vendored solver without modifying upstream source files.
3. **Strict SHA256 Deduplication**: Apply content-hash verification across both team strengths and player projections, suppressing redundant archive generation when files are identical.
4. **Planning Horizon & Chip Coverage**: Default planning horizon to 10 gameweeks, auto-expanding to encompass any scheduled chip gameweek.
5. **Mandatory Confirmation**: Require an explicit user confirmation of all settings (Team ID, horizon, chips, bank/FTs) before executing the HiGHS optimization model.
