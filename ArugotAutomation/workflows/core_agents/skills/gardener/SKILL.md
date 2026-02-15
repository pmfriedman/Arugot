---
name: gardener
description: Meta-practice that audits all practices for health and improvement. Use when asked to review practices, check for staleness, find gaps in reflection, or spawn improvement work. Governed by CONSTITUTION.md at vault root.
---

# The Gardener

**A meta-practice that tends the ecosystem of all practices, ensuring each one is alive, reflective, and improving.**

This practice is governed by the [Constitution](references/CONSTITUTION.md). It is itself subject to self-reflection and improvement.

The structural definition of what a practice is — its required components, file layout, and discovery conventions — lives in the [Practice Spec](references/PRACTICE-SPEC.md). The Gardener audits against that spec but does not own it.

---

## Purpose

The Gardener does not do the work of improvement. It ensures the *conditions* for improvement exist across all practices. It audits, surfaces staleness, and spawns improvement work where needed.

---

## What the Gardener Does

### Sense

1. **Find all practices** — using the discovery convention defined in the [Practice Spec](references/PRACTICE-SPEC.md)
2. **For each practice, locate its self-reflection mechanism** — check the spec for the default, then check the practice's own docs for any self-declared alternative
3. **If no mechanism exists, flag the practice** — a practice without self-reflection cannot improve

### Assess

For practices that *do* have a self-reflection mechanism:
- Is it producing signal? (Has it been used recently?)
- Are there open actions that haven't been addressed?

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