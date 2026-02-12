---
name: gardener
description: Meta-practice that audits all practices for health and improvement. Use when asked to review practices, check for staleness, find gaps in reflection, or spawn improvement work. Governed by CONSTITUTION.md at vault root.
---

# The Gardener

**A meta-practice that tends the ecosystem of all practices, ensuring each one is alive, reflective, and improving.**

This practice is governed by the [Constitution](references/CONSTITUTION.md). It is itself subject to self-reflection and improvement.

---

## Purpose

The Gardener does not do the work of improvement. It ensures the *conditions* for improvement exist across all practices. It audits, surfaces staleness, and spawns improvement work where needed.

---

## Key Definitions

### Practice

A **practice** is any repeatable process that serves how I work. It is durable and tool-agnostic — it describes the *what* and *why*, not the *how*.

A practice is **not** a skill, a script, or any specific implementation. Those are artifacts that may live *inside* a practice and will change over time.

Each practice must have:
- **A definition** — what it does and why it exists. Currently, the implementation file (e.g., `SKILL.md`) serves this purpose. If the practice outgrows its implementation, a separate definition may earn its way in.
- **A reflection mechanism** — a way to capture friction and feed it back (currently: `RETRO.md`)

### Friction

Any correction, workaround, repeated frustration, or deviation from expected behavior. Friction is data, not failure. It is the raw input to the self-reflection cycle.

---

## Structure (v1)

```
.github/
  skills/
    gardener/
      SKILL.md
      RETRO.md
      references/
        CONSTITUTION.md

    <practice-name>/
      SKILL.md
      RETRO.md
```

### Discovery (Convention-Based)

The Gardener discovers practices by scanning the `.github/skills/` directory. Any subdirectory containing a `SKILL.md` is treated as a practice. No separate registry is maintained — the filesystem is the registry.

The Gardener derives status from what it finds:
- **Has definition?** — a `SKILL.md` exists
- **Has reflection?** — a `RETRO.md` exists
- **Last reflection date** — parsed from the most recent `RETRO.md` entry
- **Status** — derived: active (recent retro), stale (no recent retro), incomplete (missing retro)

If convention-based discovery starts creating friction (e.g., practices live in multiple locations, or the Gardener needs to track things it can't derive), an explicit registry may earn its way in.

### Reflection Format (v1)

The Gardener prescribes a standard reflection format for all practices. This is a **temporary implementation choice** made for coherence during the bootstrapping phase. As the ecosystem matures, practices may earn the right to own their own reflection format.

Each `RETRO.md` should capture entries in this format:

```
## YYYY-MM-DD

**Friction observed:** What happened — corrections, workarounds, surprises.

**Signal:** What this suggests about the practice or its implementation.

**Action:** What should change, or "none — monitoring."
```

---

## What the Gardener Does

### Sense
- Scan the practices directory for all practices
- Check: does each one have a definition?
- Check: does each one have a reflection mechanism?
- Check: is that mechanism producing signal?
- Watch for friction patterns that no existing practice captures

### Assess
- Flag practices with no reflection mechanism
- Flag reflection mechanisms that have gone silent (stale)
- Flag repeated friction that is not being addressed
- Flag areas of work that have no practice at all
- Determine whether any thresholds have been crossed

### Act
- Spawn targeted improvement tasks for specific practices
- Recommend creation of new practices where gaps exist
- Recommend retirement of dead practices
- Report findings for approval before making changes

---

## The Gardener's Own Reflection

The Gardener maintains its own `RETRO.md` alongside its `SKILL.md` in `.github/skills/gardener/`. It is subject to the same standards it enforces. Specifically, the Gardener should periodically ask:

- Is the prescribed reflection format causing friction?
- Is convention-based discovery still sufficient, or does the system need an explicit registry?
- Are practices that were flagged actually improving?
- Should any practices be allowed to own their own reflection format?
- Is the Gardener itself too rigid or too loose?
- Has new tooling or technology emerged that should change how any of this works?

---

## Cadence

v1: The Gardener runs on-demand, triggered by the user. As the ecosystem matures, this may evolve to scheduled or signal-triggered execution.

---

## Principles

- Start minimal. Let complexity earn its way in through friction.
- The Gardener enforces the Constitution but does not modify it.
- The Gardener defines operational concepts (like "practice") but those definitions are subject to their own improvement.
- The Gardener prescribes implementation details only when coherence requires it, and loosens its grip as the system matures.
- The Gardener tends. It does not force growth.