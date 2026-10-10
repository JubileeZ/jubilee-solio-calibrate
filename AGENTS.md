# jubilee-solio-calibrate
---

## Project Identity

<!-- AGENT: 2–3 sentences. What does this repo do and why does it exist?
     Include the primary user, the core problem it solves, and the output it produces.
     Example: "Order management API for an e-commerce platform. Handles cart, checkout,
     and fulfillment state. Consumed by web and mobile frontends via REST." -->

**Stack:** <!-- AGENT: list primary language, runtime version, key frameworks, and package manager.
              Example: Python 3.12 · uv · FastAPI · PostgreSQL · SQLAlchemy · pytest -->

---

## Repo Structure

<!-- AGENT: One line per path that matters for navigation or boundaries.
     No recursive dumps. If a package needs its own rules, use nested AGENTS.md
     there instead of bloating this map. Remove section if none. -->

```
<repo structure here>
```

---

## Key Commands

| Command | What it does |
|---------|-------------|
| `bash tests/verify.sh` | Portable delivery gate (harness + project validation) |
| (add your lint command here) | Lint |
| (add your test command here) | Test |

**Commit readiness:** run each applicable command listed above and confirm it passes before proposing a commit. `tests/verify.sh` is the minimum portable gate.

**Windows:** run harness scripts (`azg`, `.agents/hooks/*`, `tests/verify.sh`) in an environment that can execute them (Git Bash or equivalent). App commands follow project stack docs.

---

## Safety Rules

- Never commit, print, or paste secret values (from `.env`, credentials, tokens, or chat). App code may read env vars; do not exfiltrate their values.
<!-- AGENT: Add repository-specific safety constraints below (migrations, prod config, data stores, etc.).
     Remove this comment when done. -->

---

## Code Conventions

<!-- AGENT: Add only non-obvious conventions not already enforced by tools or canonical code.
     Remove this section if none. -->

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
- Work Packets only in `.agents/`: `.agents/work-packets/` contains only `*.md` Work Packets. Code files, scripts, or executables in `.agents/` strictly forbidden.

---

## Domain Vocabulary

- Ambiguous domain terms: follow `docs/agents/domain.md` (read `CONTEXT.md` / `CONTEXT-MAP.md` + relevant ADRs; use glossary/ADR terms only).
- Glossary/ADR writes: `/grill-with-docs` (uses `/domain-modeling`) after a term is resolved — domain concepts only; glossary-only; lazy create/update per that skill.

---

## Work State & Checkpoints

- Tracker: `docs/agents/issue-tracker.md`. Updates/compaction/archive/cleanup: `docs/agents/progress.md`.
- Autonomous progress & push: user prompt asking to update progress and commit/push authorizes full cycle: update packet/docs, run `bash tests/verify.sh`, commit, and `git push`.
- Code commits: stage a Work Packet under `.agents/work-packets/` with code — `commit-gate` enforces. Finished packet: delete the file in the same Checkpoint. Trivial: minimal packet OK.
- Handoff / device switch / leave-for-other-agent: write Packet ID to `.agents/handoff-pointer` and commit the packet. Other device: pull, then Bind that Packet ID.
- Cleanup when task complete: delete `implementation_plan.md` / `walkthrough.md`; **delete** the packet file (do not empty). Next task: new packet from `.agents/work-packet.md.tmpl`. Durable state stays in ROADMAP / current-state / git.

<!-- AZG:MANAGED:END -->
