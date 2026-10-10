# Current Implementation State

Read if no prior context. `ROADMAP.md` shows target; this file shows what exists today. Current truth only — no historical dumps (see `docs/agents/progress.md` Compaction / Archive).

**Active phase:** Phase 1 — Repo Infrastructure & Foundations.

---

## What exists

<!-- AGENT: Document implemented areas/directories at a high level.
     (Keep this map high-level; list directories/modules, NOT individual files to save tokens).
     Table format:
     | Area | Path | Notes |
     |------|------|-------|
     | Config | `config/` | Basic loaders and env vars |
-->

| Area | Path | Notes |
|------|------|-------|
| Project Scaffold | `AGENTS.md` | Antigravity agent configuration and commands |

---

## What does NOT exist yet (do not assume)

<!-- AGENT: Document planned items not on disk yet. Prevents assuming files exist.
     | Item | Planned phase | Notes |
     |------|---------------|-------|
     | DB models | 2 | SQLAlchemy models and connection |
-->

| Item | Planned phase | Notes |
|------|---------------|-------|
| Core Logic | 2 | Business logic and implementation |

---

## Safe commands today

<!-- AGENT: Provide exact working commands runnable safely right now. -->

```bash
| Command | What it does |
|---------|-------------|
| `bash tests/verify.sh` | Portable delivery gate (harness + project validation) |
| (add your lint command here) | Lint |
| (add your test command here) | Test |
```

---

## Agent pitfalls

<!-- AGENT: Document temporary/phase pitfalls (unbuilt components, mocked APIs). Permanent traps go in AGENTS.md.
     1. Avoid importing X without Y.
     2. Ask human before migrations.
-->

- <!-- AGENT: fill in or remove -->

---

## Doc map

| Question | Read |
|----------|------|
| Glossary | `CONTEXT.md` |
| Phases & checklist | `ROADMAP.md` |
| Agent rules | `AGENTS.md` |
| How to update progress | `docs/agents/progress.md` |
