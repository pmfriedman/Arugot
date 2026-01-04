# Synth Project Recap Workflow

## Overview

**Workflow Name:** `synth_project_recap`

**Type:** Synth workflow

**Purpose:** Maintain an overview document within each project directory that synthesizes project status, progress, and context.

## Major Design Questions

### Q1: Scope & Iteration Strategy
- **Should we start with a single hardcoded project or build multi-project from day one?**
  - Single project = faster learning, lower risk, easier to change
  - Multi-project = more complete but harder to unwind if we get fundamentals wrong
  - **DECISION:** Build for multi-project architecture from the start, but validate with a single project initially
  - **Implications:**
    - Must design project discovery/selection mechanism upfront (even if it returns one project at first)
    - Must think through project identification in content attribution (Q4)
    - Initial implementation will test with one real project to prove the pattern works
    - Architecture should not have hardcoded project names or paths

### Q2: Project Organization
- **How should projects be organized to allow flexibility later?**

- **DECISION:** Hybrid approach - centralized metadata registry + flexible content structure
  - **Metadata**: `_meta/projects/[project-name].md` (Markdown with YAML frontmatter)
  - **Content**: `/projects/[project-name]/` (flexible organization, can reorganize later)
  - Frontmatter contains: `id`, `name`, `contexts`, `status`, `repo`, etc.
  - Markdown body for human documentation, links, notes
  - Discovery scans `_meta/projects/*.md` files
  
- **Key Benefits:**
  - Centralized registry makes project discovery trivial
  - Native Obsidian experience (links, search, graph)
  - Stable project IDs decouple identity from filesystem location
  - Can reorganize `/projects/` structure without breaking workflows
  - Flexible context/tags without filesystem constraints
  - Self-documenting projects

### Q3: Project Discovery & Definition
- **How does the workflow know what constitutes a "project"?**

- **DECISION:** Answered by Q2 - metadata file defines a project
  - A project exists if `_meta/projects/[project-name].md` exists with valid frontmatter
  - Discovery: scan `_meta/projects/*.md` files
  - Required frontmatter fields: `id`, `name`
  - Optional fields: `contexts`, `status`, `repo`, etc.
  - No project is valid without a metadata file
  - Workflows read all metadata files at startup to build project registry

### Q4: Content Attribution
- **How do we map source content to projects?**

- **Key Insight:** Attribution is complex enough to warrant its own workflow

- **Recording Attribution - Simple Frontmatter Approach:**
  ```yaml
  projects: [arugot]              # Confirmed attributions (manual or accepted)
  suggested_projects: [client-x]  # Machine-generated suggestions pending review
  ```
  - Clear state separation
  - Simple to edit manually
  - Easy to query programmatically
  - Review process promotes suggestions to confirmed

- **Multi-Level Strategy:**
  1. **Manual Attribution** (immediate trust)
     - User adds `projects: [id]` in frontmatter
     - Workflow trusts immediately
  
  2. **Automatic Attribution** (needs review)
     - Workflow generates `suggested_projects: [id]`
     - Based on project metadata hints (repo URLs, keywords, people)
     - Based on content analysis (mentions, links, context)
  
  3. **Review & Confirmation**
     - During review, show all attributions
     - User confirms, corrects, or adds
     - Move from `suggested_projects` → `projects`

- **Project Metadata for Matching:**
  - `repo`: Repository URL(s) for automatic matching
  - `keywords`: Words/phrases that suggest this project
  - `people`: Key people associated with project
  - `related_projects`: Other project IDs for context

- **RECOMMENDATION:** Build `extract_project_attribution` workflow first
  - Solves attribution independently before building synth workflows
  - Reusable across all future workflows
  - Lower risk, smaller scope
  - Can start with manual-only, add auto-suggest later
  - See `extract-project-attribution.md` design doc

### Q5: Multi-Project Orchestration
- **If supporting multiple projects, how does the workflow run?**
  - Single workflow run maintains ALL projects?
  - Workflow takes a `--project` argument to target one?
  - Separate workflow instance per project?
  - **Impact:** Affects state management, scheduling, and error handling

### Q6: Overview Content & Structure
- **What makes a good project overview?**
  - What sections? (Status, Recent Activity, Key Decisions, Next Actions, etc.)
  - How much history? (Last week? Last month? Since inception?)
  - What level of detail? (Bullet points? Paragraphs? Links to source material?)
  - **Unknown:** We don't have a template/pattern yet

### Q7: Update Strategy
- **How should the overview be maintained?**
  - Full regeneration each run? (Simpler but loses manual edits)
  - Append-only with dated sections? (Preserves history but grows indefinitely)
  - Hybrid: regenerate some sections, preserve others?
  - Reconciliation: detect and preserve manual edits?
  - **Risk:** Wrong choice here is very hard to unwind

### Q8: LLM Integration
- **How does the LLM fit in?**
  - What's the prompt structure?
  - What context do we provide? (All source content? Summaries? Previous overview?)
  - How do we handle token limits for large projects?
  - Do we need multiple LLM calls? (One per section? One for full overview?)

### Q9: Run Frequency & Scheduling
- **How often should this run?**
  - Daily? (Catches all activity but may be noisy)
  - Weekly? (Good for summaries but may miss urgency)
  - On-demand only? (User control but requires discipline)
  - Triggered by events? (New PR, new meeting, etc.)

### Q10: Review & Approval Process
- **How do we ensure human approval before modifying root-level content?**
  - **Constraint:** Workflows should NEVER modify root data without permission
  - **Options:**
    - Stage changes in `_scratch/auto/synth_proposals/` for human review?
    - Generate diffs/previews that require explicit approval command?
    - Interactive mode that prompts before writing?
    - Two-step workflow: generate → review → apply?
  - **What's the approval mechanism?**
    - CLI command: `run synth_project_recap --approve <proposal-id>`?
    - Manual file editing: User edits/approves in scratch then moves to root?
    - Frontmatter flag: `approved: true` in staged content?
  - **How do we track what's pending approval?**
    - State file tracking proposal IDs and timestamps?
    - Convention-based file naming in scratch directory?
    - Separate manifest/index file?
  - **What if user makes manual edits to a proposal before approving?**
    - Accept the edited version as-is?
    - Detect changes and prompt for confirmation?
    - Diff tool to show what changed from original proposal?
  - **Critical:** This affects the entire synth workflow pattern, not just this one workflow

## Goals



