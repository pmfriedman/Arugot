# Extract Project Attribution Workflow

## Overview

**Workflow Name:** `extract_project_attribution`

**Type:** Extract workflow

**Purpose:** Enrich `_scratch` content with project attribution metadata by analyzing content and project metadata to suggest or confirm which projects each piece of content relates to.

**Key Insight:** Attribution is a foundational capability needed before synth workflows can effectively aggregate project-specific content. By solving attribution independently, we create a reusable pattern for all future workflows.

**Ultimate Vision:** An interactive review interface that walks users through each document with suggested attributions, allowing quick accept/edit/reject actions with keyboard shortcuts and live document previews - a seamless, minimal-click experience. V1 establishes the workflow logic and data model to enable this future UI layer.

## Major Design Questions

### Q1: Content Scope
- **What content should the workflow process?**

- **DECISION:** Answered by Q7
  - Process all content in `_scratch/` (both `auto/` and `human/`)
  - Only files without `projects` attribution (no confirmed attribution)
  - Files with `suggested_projects` are re-scanned and suggestions updated
  - All markdown files (`.md`)

### Q2: Idempotence & State
- **What state needs to be tracked between runs?**

- **DECISION:** Answered by Q7
  - State lives in file frontmatter (`suggested_projects` field)
  - No separate state file needed for tracking
  - Queue document (`attribution-review-queue.md`) is regenerated each run
  - Workflow is fully idempotent - safe to run repeatedly

### Q3: Execution Model
- **Should this run automatically, on-demand, or both?**

- **DECISION:** Answered by Q7
  - Both automatic (scheduled) and on-demand
  - Safe for periodic automatic runs
  - Queue document is maintained/updated each run
  - Manual review happens async at user's convenience

### Q4: Attribution Strategy
- **How does the workflow generate attribution suggestions?**

**Project Metadata Source:**
- Location: `_meta/projects/*.md` files (see synth-project-recap.md Q2/Q3)
- Format: Markdown with YAML frontmatter
- Required fields: `id`, `name`
- Matching hint fields:
  - `repo`: Repository URL(s) for automatic matching
  - `keywords`: Words/phrases that suggest this project
  - `people`: Key people associated with project
  - `related_projects`: Other project IDs for context
- Workflow loads all project metadata at startup to build project registry

**Possible Tools for Suggestion Generation:**

1. **Simple Heuristics** (fast, deterministic)
   - Exact matches: repo URLs, project names, keyword phrases
   - Link analysis: extract GitHub/GitLab links from content
   - People mentions: match against project `people` lists
   - Pros: Fast, predictable, no cost
   - Cons: Limited to exact matches, misses semantic relationships

2. **LLM-Based Analysis** (semantic, context-aware)
   - Provide LLM with: file content + all project metadata
   - Prompt: "Which project(s) does this content relate to and why?"
   - Can understand indirect relationships (e.g., "API redesign" → specific project)
   - Pros: Semantic understanding, handles ambiguity, can explain reasoning
   - Cons: Cost, latency, token limits for long files

3. **Hybrid Approach** (pragmatic)
   - Use heuristics first for high-confidence matches
   - Fall back to LLM for ambiguous cases
   - Or: LLM validates/enriches heuristic suggestions
   - Pros: Balance of speed and accuracy
   - Cons: More complex to implement

**Open Questions:**
- Start with heuristics-only MVP or LLM from day one?
- If LLM: how to handle token limits for long files?
- Should we extract summaries first, then attribute summaries?
- Do we ask LLM to explain reasoning (for user review)?
- Cost/performance considerations for batch processing

### Q5: Matching Heuristics
- **What signals indicate a content-to-project relationship?**

- **Note:** Specific heuristics depend on Q4 decision (simple vs. LLM vs. hybrid)

**If using simple heuristics, potential signals:**
- **Repo URL matches**: Content contains URLs matching project `repo` field
- **Keyword matches**: Content contains phrases from project `keywords`
- **People mentions**: Content mentions names from project `people` list
- **Project name mentions**: Content explicitly references project `name` or `id`
- **Related content**: Content links to other files already attributed to project

**If using LLM:**
- All of the above, but LLM interprets semantic meaning
- Can infer relationships without explicit mentions
- Can weigh multiple weak signals together
- Can understand context (e.g., meeting about feature X relates to project Y)

### Q6: Already-Attributed Content
- **How should the workflow handle content that already has attributions?**

- **DECISION:** Answered by Q7
  - Files with confirmed `projects` attribution are skipped (never touched)
  - Files with `suggested_projects` (pending) are re-scanned and suggestions updated
  - Once user confirms (moves to `projects`), file won't be processed again
  - Manual attributions always take precedence

### Q7: Review & Confirmation
- **How does the user review and accept/reject suggestions?**

- **DECISION:** V1 - Frontmatter suggestions + review queue

**Workflow behavior:**
1. Scans `_scratch` content without `projects` attribution
2. Generates suggestions using matching heuristics
3. Writes `suggested_projects: [id]` directly to each file's frontmatter
4. Updates `_scratch/auto/attribution-review-queue.md` with links to all pending files

**User review workflow:**
1. Opens queue document in Obsidian
2. Clicks link to review each file
3. Sees `suggested_projects` in frontmatter alongside full content
4. **Accept:** Moves value from `suggested_projects` → `projects`, deletes `suggested_projects` field
5. **Edit:** Changes project ID(s), then moves to `projects`
6. **Reject:** Simply deletes `suggested_projects` field

**Next workflow run:**
- Rebuilds queue by scanning for files with `suggested_projects` field
- Only processes new/changed files without any attribution
- Queue shrinks as files are manually resolved
- Safe for automatic/scheduled runs

**Key benefits:**
- State lives in files (frontmatter), no separate tracking
- Queue document is a regenerated view, not source of truth
- UI-agnostic - future interactive UI can read same frontmatter
- Native Obsidian review experience
- Idempotent and safe for repeated runs

### Q8: Output Format
- **How are suggestions presented to the user?**

- **DECISION:** Answered by Q7
  - Suggestions: `suggested_projects` frontmatter field in each file
  - Queue: Single markdown document with links at `_scratch/auto/attribution-review-queue.md`
  - Queue format:
    ```markdown
    # Attribution Review Queue
    
    ## Pending Suggestions (5)
    
    - [[path/to/file1.md]] - Suggested: arugot
    - [[path/to/file2.md]] - Suggested: client-x, automation
    ...
    ```

### Q9: Ambiguous Cases
- **How should the workflow handle unclear or multi-project content?**

### Q10: Performance & Batching
- **Should it process all content at once or incrementally?**

## Goals

## Inputs

## Outputs

## Implementation Plan

### Building Blocks

## Testing Strategy

## Notes
