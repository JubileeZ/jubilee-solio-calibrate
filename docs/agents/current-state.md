# Current Implementation State

Read if no prior context. `ROADMAP.md` shows target; this file shows what exists today. Current truth only — no historical dumps (see `docs/agents/progress.md` Compaction / Archive).

**Active phase:** Complete — Maintenance & Iteration.

---

## What exists

| Area | Path | Notes |
|------|------|-------|
| Harness & Gate | `tests/verify.sh`, `tests/project-tests.sh`, `.agents/` | Alpha-Zero-G v4 harness and verify gate |
| Agent Config | `AGENTS.md` | Calibrate project identity, boundaries, commands, safety |
| Roadmap | `ROADMAP.md` | 4-phase plan; all phases complete |
| Python Package | `pyproject.toml`, `uv.lock`, `.venv/` | uv environment with httpx, pandas, pytest, ruff |
| Raw Data | `data/raw/team_strengths_base.csv`, `data/raw/archive/` | Active base strength Solio export; historical inputs archived chronologically |
| Team Mapping | `src/solio_calibrate/mapping.py` | Bidirectional 20-team Solio codes <-> FPL IDs |
| Solio CSV I/O | `src/solio_calibrate/io.py` | Schema validator and 3-decimal CSV reader/writer with deduplicated raw ingestion and output archiving |
| FPL API Client | `src/solio_calibrate/client.py` | Caching API client, fixtures (including provisional), live event element xG aggregator |
| Calibration Engine | `src/solio_calibrate/calibrate.py` | Match-level xG/xGC, leave-one-out Bayesian normalization, GW1-19 linear decay auto-weight |
| CLI Runner | `src/solio_calibrate/cli.py` | CLI executable with `--auto-weight`, provisional match reporting, raw ingestion, and output archiving |
| Calibrated Output | `data/output/team_strengths_calibrated.csv`, `data/output/archive/` | Latest calibrated Solio export (3-decimal schema); historical runs archived with ISO timestamps |
| Agent Skill | `.agents/skills/calibrate-team-strength/SKILL.md` | Skill spec with default force-refresh, GW coverage, provisional matches, 20-team template, default commit-push |
| Architecture Decision | `docs/adr/0001-fpl-empirical-strength-normalization.md` | ADR for empirical normalization, shrinkage, zero-GW fallback |
| Architecture Decision | `docs/adr/0002-scope-boundary-calibration-vs-squad-solver.md` | ADR for strict calibration scope and boundary vs sibling squad solver |

---

## What does NOT exist yet (do not assume)

| Item | Planned phase | Notes |
|------|---------------|-------|
| Squad Optimization / Solver | Out of scope | Strictly owned by sibling repo `fpl-jubilee-ascent` (`transfer-planner`) |
| Web UI / Frontend | Future | CLI and skill workflows only |

---

## Safe commands today

| Command | What it does |
|---------|-------------|
| `bash tests/verify.sh` | Portable delivery gate (harness + project validation) |
| `uv run pytest` | Run test suite |
| `uv run ruff check .` | Lint codebase |
| `uv run solio-calibrate` | Execute calibration CLI |

---

## Agent pitfalls

- Never save calibrated output into `data/raw/`. Write to `data/output/team_strengths_calibrated.csv` and `data/output/archive/`.
- Ensure output CSV maintains exact 3-decimal float precision and header format `Team,Goals,Goals Conceded`.
- Never implement squad optimization, player projections, or vendored MILP solvers in this repository; transfer planning belongs strictly to `fpl-jubilee-ascent`.

---

## Doc map

| Question | Read |
|----------|------|
| Glossary | `CONTEXT.md` |
| Phases & checklist | `ROADMAP.md` |
| Agent rules | `AGENTS.md` |
| How to update progress | `docs/agents/progress.md` |
