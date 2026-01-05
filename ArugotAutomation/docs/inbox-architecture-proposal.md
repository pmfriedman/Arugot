# The Inbox Pattern

## Core Concept

Work flows through an Inbox: when something needs your attention, you get a notification. Process it however you want. Mark it complete when done.

From the core perspective, and additional workflows or automation are implementation details.

## The Three Steps

1. **Create notification** in `_inbox/` when something needs attention.
2. **Process however you want**: Manual, Copilot-assisted, or automated
3. **Mark complete**: Move to `_archive/` when done

## Key Principles

**Notifications ≠ Artifacts**
- The Inbox contains lightweight messages about work needing attention
- The message points to source artifacts stored elsewhere, they do not contain the content themselves
- The Inbox just tracks what needs processing



**Processing method is your choice**
- Manual: Read the notification, do the work by hand, mark complete
- Copilot-assisted: Open in VS Code, use AI to help
- Automated: Build a workflow to process automatically

**Explicit completion**
- When done, move notification to `_archive/`
- Source artifacts stay where they are
- The Inbox only tracks what still needs attention

## Vault Structure

**Required:**
- `_inbox/` - Active notifications
- `_archive/` - Completed notifications

**Everything else is up to you:**
- Where meeting notes live
- How you organize projects
- Folder structure for artifacts
- What format notifications take
- How notifications are created

The Inbox is just the coordination layer.

## Why This Works

**Decoupling**: "What needs attention" is separate from "how to handle it"

**Flexibility**: Processing method can change without changing the Inbox

**Progressive automation**: Start manual, automate only when you understand the workflow

**No premature optimization**: Don't build automation before you know what you need
