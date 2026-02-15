# Practice Specification

**The structural definition of a practice — what it is, what it's made of, and where it lives.**

This document is a shared reference. It is consumed by any skill that needs to create, audit, or modify practices. It is expected to change as tooling and standards evolve.

This document is governed by the [Constitution](CONSTITUTION.md). Changes to this spec must not violate constitutional principles.

---

## What Is a Practice?

A **practice** is any repeatable process that serves how I work. It is durable and tool-agnostic — it describes the *what* and *why*, not the *how*.

A practice is **not** a skill, a script, or any specific implementation. Those are artifacts that may live *inside* a practice and will change over time.

---

## What Is Friction?

Any correction, workaround, repeated frustration, or deviation from expected behavior. Friction is data, not failure. It is the raw input to the self-reflection cycle.

---

# Current Implementation

> Everything below describes how practices are currently structured. These are implementation choices, not principles — they are subject to adjustment as the system matures and friction is observed.

## Required Components

Each practice must have:

### 1. Definition

A document that describes what the practice does and why it exists. The form depends on context:

| Form | When to use | Location |
|---|---|---|
| `SKILL.md` | The practice should be auto-discoverable by Copilot as a skill | `.github/skills/<name>/` |
| `AGENTS.md` | The practice is area-specific, scoped to a domain of work | `areas/<area>/` |

A `SKILL.md` serves double duty: it is both the practice definition and the Copilot skill entry point. An `AGENTS.md` is lighter — it defines how work is done within an area without registering as a Copilot skill.

Other definition forms may emerge. The requirement is that a definition exists, not that it takes a specific form.

**`SKILL.md` frontmatter (required when used):**
```yaml
---
name: <practice-id>
description: <one-line description>
---
```

### 2. Reflection Mechanism (`RETRO.md`)

A file that captures friction and feeds it back into the practice. Every practice must have one. A practice without reflection cannot improve and will eventually die or drift.

The `RETRO.md` lives alongside the definition document — in the same directory.

**Entry format (v1):**
```markdown
## YYYY-MM-DD

**Friction observed:** What happened — corrections, workarounds, surprises.

**Signal:** What this suggests about the practice or its implementation.

**Action:** What should change, or "none — monitoring."
```

This format is a v1 implementation choice made for coherence during the bootstrapping phase. As the ecosystem matures, practices may earn the right to own their own reflection format.

---

## File Layout

```
.github/
  skills/
    <practice-name>/
      SKILL.md          ← definition (skill-based practices)
      RETRO.md          ← reflection mechanism (required)
      references/       ← supporting documents (optional)

areas/
  <area-name>/
    AGENTS.md           ← definition (area-based practices)
    RETRO.md            ← reflection mechanism (required)
```

### Shared References

Documents that serve multiple practices live in the `gardener/references/` directory. This includes the Constitution and this spec. If this location causes friction as more shared references accumulate, a dedicated shared location (e.g., `.github/skills/_references/`) may earn its way in.

---

## Discovery Convention

Practices are discovered by scanning known locations for known definition document types:

| Location | Definition file | Type |
|---|---|---|
| `.github/skills/*/` | `SKILL.md` | Skill-based practice |
| `areas/*/` | `AGENTS.md` | Area-based practice |

No separate registry is maintained — the filesystem is the registry.

Status is derived from what exists:

| Check | How |
|---|---|
| Has definition? | A recognized definition file exists |
| Has reflection? | `RETRO.md` exists alongside the definition |
| Last reflection date | Parsed from most recent `RETRO.md` entry |
| Status | Derived: **active** (recent retro), **stale** (no recent retro), **incomplete** (missing retro) |

If convention-based discovery starts creating friction (e.g., practices live in additional locations, or auditing needs to track things it can't derive from the filesystem), an explicit registry may earn its way in.

---

## Versioning

This spec does not use formal version numbers. Changes are tracked through the Gardener's retro and through the document's own edit history. If versioning becomes necessary, it will earn its way in.
