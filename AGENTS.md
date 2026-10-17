# jubilee-solio-calibrate
---

## Project Identity

Adjust and calibrate Solio team attack and defense strengths (`Goals`, `Goals Conceded`) using official FPL API stats and user preferences. Reads original Solio team strength CSV export, fetches current team performance from FPL API, computes calibrated adjustments, and outputs matched CSV for re-uploading to Solio web planner. Provides CLI tool and agent skill.

**Stack:** Python 3.12 · uv · httpx · pandas · pytest

---

## Repo Structure

```
├── data/                           # Solio raw input CSVs and calibrated outputs
├── docs/agents/                    # Continuity, roadmap, issue tracking
├── .agents/skills/calibrate-team-strength/ # Agent skill to execute calibrations
├── src/solio_calibrate/            # Calibration core package
│   ├── client.py                   # FPL API fetching & caching
│   ├── calibrate.py                # Strength adjustment logic
│   └── cli.py                      # CLI runner
├── tests/                          # Verify gate and test suite
└── pyproject.toml                  # uv packaging and dependencies
```

---

## Key Commands

| Command | What it does |
|---------|-------------|
| `bash tests/verify.sh` | Portable delivery gate (harness + project validation) |
| `uv run ruff check .` | Lint codebase |
| `uv run pytest` | Run test suite |
| `uv run solio-calibrate` | Execute calibration CLI |

**Commit readiness:** run each applicable command listed above and confirm it passes before proposing a commit. `tests/verify.sh` is the minimum portable gate.

**Windows:** run harness scripts (`azg`, `.agents/hooks/*`, `tests/verify.sh`) in an environment that can execute them (Git Bash or equivalent). App commands follow project stack docs.

---

## Safety Rules

- Never commit, print, or paste secret values (from `.env`, credentials, tokens, or chat). App code may read env vars; do not exfiltrate their values.
- Never save calibrated outputs into `data/raw/`; write outputs to `data/output/` with archive snapshots in `data/output/archive/`. Always archive prior base strength to `data/raw/archive/` before updating `data/raw/team_strengths_base.csv`.
- Calibration delivery: requesting team strength calibration (`calibrate-team-strength`) authorizes full publish cycle by default: run `tests/verify.sh`, stage and commit output/archive files, push `origin/main`.
- Deduplicate archives: verify SHA256 content before creating archive snapshots for raw base strengths and calibrated outputs. Suppress duplicate timestamped files when content is identical.

---

## Project Boundaries & Anti-Goals

- **Strict Calibration Scope**: This repository is strictly for calibrating Solio team attack and defense ratings (`Goals`, `Goals Conceded`) and empirical Home Advantage Factor using official FPL match data, outputting upload-ready CSVs for the Solio web planner.
- **No Squad Solvers or Player Projections**: Never implement, vendor, or adapt squad optimization solvers (such as `open-fpl-solver`, MILP/HiGHS), player minutes models, or transfer planners here. All squad solving, transfer planning, and player projection modeling belong strictly to sibling repository `fpl-jubilee-ascent` (`.agents/skills/transfer-planner`, `commands.solve`, `solver/`). See ADR 0002.

---

## Code Conventions

- Enforce standard Solio 3-letter team codes (`ARS`, `AVL`, `MCI`, etc.) with explicit bidirectional mapping to FPL team IDs and names.
- Keep calibration adjustment logic as pure, deterministic functions decoupled from HTTP and filesystem I/O.
- Quantize all calibrated float values (`Goals`, `Goals Conceded`) to 3 decimal places on output.

---

<!-- AZG:MANAGED:START -->
## Placeholder fill

`<!-- AGENT: ... -->` in agent/tracking docs (e.g. `AGENTS.md`, `ROADMAP.md`, `docs/agents/*`):
1. Ask fill or skip; skip → leave comment exact.
2. One section at a time; ≤3 options, recommended first.
3. Done → drop resolved comments + inapplicable sections; telegraphic prose.

---

## Session start

Once per session (not every turn). Continuity from listed files (chat ≠ continuity):

1. `current-state.md` (reality).
2. `ROADMAP.md` active phase / first unchecked only.
3. `git status` + `git log -5 --oneline` before edit.
4. Other docs JIT via pointers.

Do not read Work Packet bodies at start. **Independent Request** (no change asked): no packet I/O.

**Bind** only when the user says continue / handoff / a Packet ID, or asks to continue and `.agents/handoff-pointer` names one. Change asked with no bind: attended — ask new vs which open slug (≤3); unattended — create `.agents/work-packets/<slug>.md` from `.agents/work-packet.md.tmpl`. Never auto-bind the last leftover packet.

Session start done when: `current-state` + ROADMAP slice + git status/log. Bound packet read only after Bind.

Missing required continuity doc: restore from git if history exists; else ask user.

During work / before Checkpoint: update tracking docs when state changes
(see `docs/agents/progress.md`). Before Checkpoint: refresh bound packet SFDBN, or delete the packet if finished.

JIT (read when task needs): full `CONTEXT.md`, `progress.md`, `issue-tracker.md`, archived ROADMAP, research notes.

---

## Harness Safety

- Safety-hook deny: explain block; give exact manual command/content; leave hook unchanged (do not execute blocked action). Never emit multi-line heredocs (`cat << 'EOF'`); use single-line commands or write payload to temporary scratch files.
- Work Packets only in `.agents/`: `.agents/work-packets/` contains only `*.md` Work Packets; code files, scripts, or executables in `work-packets/` strictly forbidden. Project skills under `.agents/skills/` may contain skill assets and scripts.

---

## Domain Vocabulary

- Ambiguous domain terms: follow `docs/agents/domain.md` (read `CONTEXT.md` / `CONTEXT-MAP.md` + relevant ADRs; use glossary/ADR terms only).
- Glossary/ADR writes: `/grill-with-docs` (uses `/domain-modeling`) after a term is resolved — domain concepts only; glossary-only; lazy create/update per that skill.

---

## Work State & Checkpoints

- Tracker: `docs/agents/issue-tracker.md`. Updates/compaction/archive/cleanup: `docs/agents/progress.md`.
- Autonomous progress & push: user prompt asking to update progress and commit/push authorizes full cycle: update packet/docs, run `bash tests/verify.sh`, commit, and `git push`. Calibration skill runs authorize full publish cycle for calibration data by default.
- Code commits: stage a Work Packet under `.agents/work-packets/` with code — `commit-gate` enforces. Finished packet: delete the file in the same Checkpoint. Trivial: minimal packet OK.
- Handoff / device switch / leave-for-other-agent: write Packet ID to `.agents/handoff-pointer` and commit the packet. Other device: pull, then Bind that Packet ID.
- Cleanup when task complete: delete `implementation_plan.md` / `walkthrough.md`; **delete** the packet file (do not empty). Next task: new packet from `.agents/work-packet.md.tmpl`. Durable state stays in ROADMAP / current-state / git.
<!-- AZG:MANAGED:END -->
