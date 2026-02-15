---
name: friction-capture
description: "Capture friction inline without breaking flow. Use whenever the user writes 'retro:' followed by a friction observation. Route it to the correct RETRO.md, acknowledge briefly, and return to whatever was happening."
---

# Friction Capture

**Capture friction observations inline, without breaking the user's flow.**

---

## Purpose

Friction is the raw input to self-reflection. But logging it currently requires context-switching — figuring out which RETRO.md to write to, opening it, formatting an entry, and then finding your way back to what you were doing. That's enough friction to skip it, and skipped friction is lost signal.

This practice eliminates that barrier. The user says what they noticed, and the system handles the rest.

---

## Trigger

The user types `retro:` followed by a friction observation, at any point during any conversation.

Example: `retro: the meeting notes keep losing action items`

---

## Behavior

1. **Capture** — extract the friction observation from the user's message
2. **Route** — determine which `RETRO.md` it belongs in, using context:
   - What practice or area is the current conversation about?
   - If ambiguous, infer the best fit from the content of the observation
   - If truly unclear, ask (but prefer inferring — asking breaks flow)
3. **Append** — add an entry to the target `RETRO.md` using the current reflection format:
   ```markdown
   ## YYYY-MM-DD

   **Friction observed:** <the user's observation>

   **Signal:** To be assessed.

   **Action:** None yet — captured for review.
   ```
4. **Acknowledge** — respond with a brief confirmation (e.g., "Got it — logged to DHR retro.") and nothing more
5. **Resume** — return immediately to whatever was happening before the `retro:` trigger

---

## Routing Logic

Use the [Practice Spec](../gardener/references/PRACTICE-SPEC.md) discovery convention to find all practices and their `RETRO.md` locations. Route based on conversational context:

| Context | Route to |
|---|---|
| Currently working within a specific area | `areas/<area>/RETRO.md` |
| Currently executing a specific skill | `.github/skills/<skill>/RETRO.md` |
| Friction is about the practice system itself | `.github/skills/gardener/RETRO.md` |
| Unclear | Best inference from the observation content, or ask |

---

## Principles

- **Never break flow.** The entire point is zero-disruption capture.
- **Prefer inference over asking.** Asking which retro to log to defeats the purpose.
- **Minimal acknowledgment.** One line, then back to work.
- **Imperfect routing is fine.** A friction entry in a slightly wrong retro is infinitely better than no entry at all. Misroutes are themselves friction to capture later.
