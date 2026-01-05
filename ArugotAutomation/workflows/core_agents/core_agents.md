# Core Agents Workflow

## Purpose
Maintains the core **Inbox Agent** and helps create specialized agents for processing different types of inbox items. This workflow generates agent definition files (`.agent.md`) but focuses on flexibility rather than prescribing specific structure.

## Context
The Arugot framework follows an Inbox pattern where work flows through `_inbox/` → process → `_archive/`. Custom agents provide interactive assistance while keeping the user in control.

## Core Philosophy

**Start minimal, evolve organically.** The core_agents workflow maintains a single core agent:

**`Inbox`** - The universal entry point for all inbox processing that adapts to different areas by loading area-specific instructions.

## Core Agent

### `inbox.agent.md` - The Universal Entry Point

The inbox agent is intentionally flexible:
- Analyzes any inbox item to understand its content
- References `meta/areas.md` to classify the item
- Loads area-specific instructions from `meta/areas/{area}.md`
- Applies those instructions to help process the item interactively
- Adapts its behavior based on the area's requirements

**Key characteristic**: One agent that adapts by loading different instructions, rather than many specialized agents.

## Agent Evolution Pattern

1. **Start**: Use `@Inbox` for everything
2. **Notice pattern**: "I keep processing meeting notes the same way..."
3. **Create instructions**: Add `meta/areas/meetings.md` with processing guidelines
4. **Update classification**: Add to `meta/areas.md` so inbox agent can recognize and route to those instructions
5. **Iterate**: Refine instructions based on actual usage

## Design Decisions

### Minimal Core, Organic Growth
Start with just the inbox agent. Add area-specific instruction files only when clear patterns emerge from actual usage.

### Instruction-Based, Not Agent-Based
Rather than creating many specialized agents, create instruction files that the inbox agent reads and follows dynamically.

### Handoff Configuration: `send: false`
All handoffs pre-fill prompts but wait for user review. Maintains control at each step.

### No Prescribed Taxonomy
Don't dictate "these are the types of inbox items." Let users discover their own patterns and create agents that match their workflow.

### Vault Location Flexibility
Agents suggest but don't enforce vault organization beyond `_inbox/` and `_archive/`.

## Workflow Implementation
** from `workflows/core_agents/agents/inbox.agent.md`
2. **Compares checksum** with file in vault's `.github/agents/`
3. **Updates vault file** if checksum differs (or file doesn't exist)

No state tracking needed - the workflow is stateless and compares source template with destination file
3. **Updates vault files** if checksums differ (or file doesn't exist)

No state tracking needed - the workflow is stateless and compares source templates with destination files each run.

## Usage

### Runniinbox agent
uv run python main.py run core_agents

# Dry run (show what would be updated)
uv run python main.py run core_agents --dry-run
```

### Creating Area-Specific Instructions

When you want to add processing support for a new area:
1. Add the area to `meta/areas.md` with classification keywords
2. Create `meta/areas/{area}.md` with specific processing instructions
3. The inbox agent will automatically use these when classifying and processing items

Example `meta/areas/meetings.md`:
```markdown
# Meeting Processing Instructions

## What to Extract
- Decisions, action items, attendees

## Output Format
- Add structured sections to the note

## Next Steps
- Suggest task creation, archival
```

## Future Enhancements

- **Instruction templates**: Library of starting points for common area types
- **Classification validation**: Check that area classifications are effective
- **Usage tracking**: Understand which areas are most common

## Related Workflows
- All workflows can generate inbox items that the `@_inbox` agent helps process
- As patterns emerge, create area-specific instruction files rather than new agents

## References
- [GitHub Copilot Custom Agents Docs](https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-custom-agents)
- [VS Code Custom Agents Docs](https://code.visualstudio.com/docs/copilot/customization/custom-agents)
- [Handoff Documentation](https://code.visualstudio.com/docs/copilot/customization/custom-agents#_handoffs)
