---
name: inbox-processing
description: Process files from the _inbox folder and synthesize them into the vault
---

# Inbox Processing Skill

## Purpose

Inbox items are raw material — meeting transcripts, PR notifications, notes, and other artifacts that arrive unstructured. Left unprocessed, they accumulate and lose context. This practice turns inbox items into integrated vault knowledge by classifying them into the right Area, understanding that Area's conventions, and synthesizing the content where it will actually be used.

---

## Vault Structure

- **Inbox items**: Active items awaiting processing are in `_inbox/` folder
- **Areas**: Predefined categories defined in `/_meta/areas.md`
- **Area folders**: Each Area has its own folder at `/areas/{area_name}/`
- **Area context**: Purpose and organization documented in `/areas/{area_name}/AGENTS.md`

## Processing Workflow

When processing an inbox item, follow this workflow:

### Step 1: Read and Understand

- **Read the inbox document fully** — understand all content, metadata, and context
- **Follow Obsidian links** — read any documents linked within the inbox item (using `[[wikilinks]]`)
- **Check backlinks** — find and read documents that link to this inbox item
- **Check for related inbox items** — look for other inbox items that reference the same meeting, topic, PR, etc. If multiple inbox items relate to the same topic or meeting, process them together as a batch (see Batch Processing below)
- **Use workspace search as backup** — if needed context isn't linked, search for relevant documents
- Build a complete picture of what this inbox item is about

### Step 1.1: Special Handling for Github PRs

If the inbox item is a Pull Request Note, then do the following:
- Find all inbox notes for this PR
- Use the references in the note(s) to determine what changed that needs the user's attention
- Summarize the key changes concisely
- Skip to step 6 (archiving)

### Step 2: Classify the Area

- **Reference `/_meta/areas.md`** to see the list of predefined Areas
- **Determine which Area** this item belongs to based on the Area definitions
- **Only classify as Areas defined in the meta** - Never suggest areas that aren't in `/_meta/areas.md`
- **If no Area fits**: Inform the user that none of the predefined Areas match this item

### Step 3: Confirm Classification

- **Present the classification** to the user with a brief explanation
- **Wait for confirmation** - Do not proceed until the user confirms or corrects the classification
- If user provides a different classification, use that instead

### Step 4: Understand the Area Context

- **Read the Area instructions** from `/areas/{area_name}/AGENTS.md` where `{area_name}` is the confirmed classification
- Understand the Area's purpose, what content it maintains, and how it's organized
- If the Area AGENTS.md file doesn't exist, note that this Area hasn't been set up yet

### Step 5: Integrate the Inbox Item

- **If Area context exists**: Use the Area's purpose and organization to determine how to integrate this inbox item
  - Determine what Area content needs to be updated or created
  - Identify relevant existing Area documents that should be updated
  - Extract information from the inbox item that belongs in the Area
  - Make updates to Area content as needed
  - Work interactively with the user to refine those updates

### Step 6: Archive the Inbox Item

- **Confirm integration is complete** - Ensure all relevant content has been processed and integrated
- **Ask for user approval** - Explicitly ask the user if they're ready to archive this inbox item
- **Wait for confirmation** - Do not archive until the user explicitly approves
- **Use the vault_archive_file tool** - Once approved, call `vault_archive_file` with the inbox item's filename to move it from `_inbox/` to `_archive/`

## Important Guidelines

- **Understand the Area**: Read and understand the Area's purpose before proposing updates
- **Think integration**: Focus on how the inbox item updates or relates to existing Area content
- **Let the AGENTS.md guide detail level**: Use the Area's AGENTS.md to determine what level of detail to preserve and which information is important for that Area
- **Be adaptive**: When no Area context exists, work with the user to establish it
- **Stay interactive**: This is a collaborative process - confirm actions before taking them

## Batch Processing

When multiple inbox items relate to the same topic, meeting, or context:

- **Identify the batch** during Step 1 — flag all related inbox items before proceeding
- **Read the full batch** before classifying or integrating — the combined context often tells a richer story than any single item
- **Integrate holistically** — synthesize the batch into a single coherent update to the Area, rather than processing each item in isolation
- **Archive the full batch** — once integration is confirmed, archive all items in the batch together

## Friction Awareness

During processing, stay alert for friction signals — corrections, dissatisfaction with output quality, repeated adjustments, or the user saying something "isn't quite right." These are data:

- **Area-specific friction** (e.g., how content was written into an Area) should be routed to that Area's `RETRO.md`
- **Process-level friction** (e.g., classification was wrong, workflow steps were confusing) belongs in this practice's own `RETRO.md`
- When in doubt, the user can say `retro:` followed by their observation and it will be captured automatically

## Output Style

- **Follow explicit style guidance**: If the Area's AGENTS.md specifies formatting or style, follow it
- **Observe implicit style patterns**: If no explicit guidance exists, match the style and organization of existing Area content
