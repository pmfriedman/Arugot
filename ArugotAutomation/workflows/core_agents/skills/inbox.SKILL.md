---
name: Inbox-Processing
description: Process files from the _inbox folder and synthesize them into the vault
---

# Inbox Processing Skill

This skill provides instructions for processing inbox items within an Obsidian vault that follows the Inbox pattern.

## Vault Structure

- **Inbox items**: Active items awaiting processing are in `_inbox/` folder
- **Areas**: Predefined categories defined in `/_meta/areas.md`
- **Area folders**: Each Area has its own folder at `/areas/{area_name}/`
- **Area context**: Purpose and organization documented in `/areas/{area_name}/overview.md`

## Processing Workflow

When processing an inbox item, follow this workflow:

### Step 1: Read and Understand

- **Read the inbox document fully** - understand all content, metadata, and context
- **Follow Obsidian links** - Read any documents linked within the inbox item (using `[[wikilinks]]`)
- **Check backlinks** - Find and read documents that link to this inbox item
- **Use workspace search as backup** - If needed context isn't linked, search for relevant documents
- Build a complete picture of what this inbox item is about

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

- **Read the Area overview** from `/areas/{area_name}/overview.md` where `{area_name}` is the confirmed classification
- Understand the Area's purpose, what content it maintains, and how it's organized
- If the Area overview file doesn't exist, note that this Area hasn't been set up yet

### Step 5: Integrate the Inbox Item

- **If Area context exists**: Use the Area's purpose and organization to determine how to integrate this inbox item
  - Determine what Area content needs to be updated or created
  - Identify relevant existing Area documents that should be updated
  - Extract information from the inbox item that belongs in the Area
  - Make updates to Area content as needed
  - Work interactively with the user to refine those updates

## Important Guidelines

- **Understand the Area**: Read and understand the Area's purpose before proposing updates
- **Think integration**: Focus on how the inbox item updates or relates to existing Area content
- **Let the overview guide detail level**: Use the Area's overview to determine what level of detail to preserve and which information is important for that Area
- **Be adaptive**: When no Area context exists, work with the user to establish it
- **Stay interactive**: This is a collaborative process - confirm actions before taking them

## Output Style

- **Follow explicit style guidance**: If the Area's overview specifies formatting or style, follow it
- **Observe implicit style patterns**: If no explicit guidance exists, match the style and organization of existing Area content

## Goal

Help efficiently process inbox items by classifying them into Areas, understanding Area context, and proposing appropriate updates to integrate the inbox content into the vault structure.