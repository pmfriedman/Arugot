"""
Core Agents Workflow

Maintains core custom GitHub Copilot agents, skills, and MCP servers.
Generates and updates .agent.md files in .github/agents/,
.SKILL.md files in .github/skills/, and .vscode/mcp.json.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any
import hashlib

from common.types import RunContext
from settings import settings

logger = logging.getLogger(__name__)

DESCRIPTION = "Maintains core custom GitHub Copilot agents, skills, and MCP servers."

# Core agents maintained by this workflow
CORE_AGENTS = []

# Core skills maintained by this workflow
CORE_SKILLS = ["inbox-processing", "gardener", "friction-capture"]

# Get the ArugotAutomation root directory dynamically
AUTOMATION_ROOT = Path(__file__).parent.parent.parent

# Core MCP servers maintained by this workflow
CORE_MCPS = {
    "arugot-vault": {
        "command": "uv",
        "args": ["run", "python", "-m", "mcp_server.server"],
        "cwd": str(AUTOMATION_ROOT),
    }
}


def calculate_checksum(content: str) -> str:
    """Calculate SHA-256 checksum of content."""
    return hashlib.sha256(content.encode()).hexdigest()


def load_agent_template(agent_id: str) -> str:
    """Load agent template from the agents/ subdirectory."""
    template_path = Path(__file__).parent / "agents" / f"{agent_id}.agent.md"

    if not template_path.exists():
        raise FileNotFoundError(f"Agent template not found: {template_path}")

    return template_path.read_text(encoding="utf-8")


def get_skill_source_dir(skill_id: str) -> Path:
    """Get the source directory for a skill."""
    skill_dir = Path(__file__).parent / "skills" / skill_id

    if not skill_dir.is_dir():
        raise FileNotFoundError(f"Skill directory not found: {skill_dir}")

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        raise FileNotFoundError(f"SKILL.md not found in: {skill_dir}")

    return skill_dir


def get_skill_files(skill_dir: Path) -> list[Path]:
    """List all files in a skill directory (recursively), relative to skill_dir."""
    return sorted(
        p.relative_to(skill_dir)
        for p in skill_dir.rglob("*")
        if p.is_file() and p.name != "__pycache__" and "__pycache__" not in p.parts
    )


async def run(context: RunContext, state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run the core agents workflow.

    Compares agent templates from the workflow directory with the vault's
    .github/agents/ directory. Updates vault files if checksums differ.

    Args:
        context: Run context with paths and arguments
        state: Workflow state (not used - kept for interface compatibility)

    Returns:
        State dictionary (unchanged)
    """
    logger.info("Starting core agents workflow")

    # Get arguments
    specific_agent = context.args.get("agent")  # Optional: generate specific agent
    specific_skill = context.args.get("skill")  # Optional: generate specific skill

    # Determine target directory in vault
    vault_root = Path(settings.obsidian_vault_dir)
    if not vault_root.is_absolute() or not vault_root.exists():
        logger.error(f"Invalid vault directory: {settings.obsidian_vault_dir}")
        logger.error("Please set OBSIDIAN_VAULT_DIR in .env")
        return state

    vault_agents_dir = vault_root / ".github" / "agents"
    vault_skills_dir = vault_root / ".github" / "skills"

    # Determine which agents to process
    agents_to_process = CORE_AGENTS if not specific_agent else [specific_agent]

    if specific_agent and specific_agent not in CORE_AGENTS:
        logger.error(f"Unknown agent: {specific_agent}")
        logger.info(f"Available agents: {', '.join(CORE_AGENTS)}")
        return state

    # Determine which skills to process
    skills_to_process = CORE_SKILLS if not specific_skill else [specific_skill]

    if specific_skill and specific_skill not in CORE_SKILLS:
        logger.error(f"Unknown skill: {specific_skill}")
        logger.info(f"Available skills: {', '.join(CORE_SKILLS)}")
        return state

    # Process each agent
    for agent_id in agents_to_process:
        logger.info(f"Processing agent: {agent_id}")

        # Load template from workflow directory
        try:
            template_content = load_agent_template(agent_id)
        except FileNotFoundError as e:
            logger.error(f"  Failed to load template: {e}")
            continue

        template_checksum = calculate_checksum(template_content)

        # Check if vault file exists and compare checksums
        vault_file = vault_agents_dir / f"{agent_id}.agent.md"
        needs_update = True

        if vault_file.exists():
            vault_content = vault_file.read_text(encoding="utf-8")
            vault_checksum = calculate_checksum(vault_content)

            if vault_checksum == template_checksum:
                logger.info(f"  ✓ Agent '{agent_id}' is up to date")
                needs_update = False
            else:
                logger.info(f"  ! Agent '{agent_id}' has changed (checksum mismatch)")
        else:
            logger.info(f"  + Agent '{agent_id}' does not exist in vault")

        # Update if needed
        if needs_update:
            if context.dry_run:
                logger.info(f"  [DRY RUN] Would write: {vault_file}")
                logger.debug(f"Content preview:\n{template_content[:200]}...")
            else:
                vault_agents_dir.mkdir(parents=True, exist_ok=True)
                vault_file.write_text(template_content, encoding="utf-8")
                logger.info(f"  ✓ Wrote: {vault_file}")

    # Process each skill (syncs entire skill directory including references, scripts, assets)
    for skill_id in skills_to_process:
        logger.info(f"Processing skill: {skill_id}")

        # Locate skill source directory
        try:
            skill_source_dir = get_skill_source_dir(skill_id)
        except FileNotFoundError as e:
            logger.error(f"  Failed to locate skill: {e}")
            continue

        # Get all files in the skill directory
        skill_files = get_skill_files(skill_source_dir)
        vault_skill_dir = vault_skills_dir / skill_id

        for rel_path in skill_files:
            source_file = skill_source_dir / rel_path
            vault_file = vault_skill_dir / rel_path

            source_content = source_file.read_text(encoding="utf-8")
            source_checksum = calculate_checksum(source_content)

            needs_update = True

            if vault_file.exists():
                vault_content = vault_file.read_text(encoding="utf-8")
                vault_checksum = calculate_checksum(vault_content)

                if vault_checksum == source_checksum:
                    logger.info(f"  ✓ {skill_id}/{rel_path} is up to date")
                    needs_update = False
                else:
                    logger.info(
                        f"  ! {skill_id}/{rel_path} has changed (checksum mismatch)"
                    )
            else:
                logger.info(f"  + {skill_id}/{rel_path} does not exist in vault")

            if needs_update:
                if context.dry_run:
                    logger.info(f"  [DRY RUN] Would write: {vault_file}")
                else:
                    vault_file.parent.mkdir(parents=True, exist_ok=True)
                    vault_file.write_text(source_content, encoding="utf-8")
                    logger.info(f"  ✓ Wrote: {vault_file}")

    # Process MCP configuration
    logger.info("Processing MCP configuration")

    mcp_config = {"servers": CORE_MCPS}
    mcp_content = json.dumps(mcp_config, indent=2)
    mcp_checksum = calculate_checksum(mcp_content)

    vault_mcp_file = vault_root / ".vscode" / "mcp.json"
    needs_update = True

    if vault_mcp_file.exists():
        vault_mcp_content = vault_mcp_file.read_text(encoding="utf-8")
        vault_mcp_checksum = calculate_checksum(vault_mcp_content)

        if vault_mcp_checksum == mcp_checksum:
            logger.info("  ✓ MCP configuration is up to date")
            needs_update = False
        else:
            logger.info("  ! MCP configuration has changed (checksum mismatch)")
    else:
        logger.info("  + MCP configuration does not exist in vault")

    if needs_update:
        if context.dry_run:
            logger.info(f"  [DRY RUN] Would write: {vault_mcp_file}")
            logger.debug(f"Content:\n{mcp_content}")
        else:
            vault_mcp_file.parent.mkdir(parents=True, exist_ok=True)
            vault_mcp_file.write_text(mcp_content, encoding="utf-8")
            logger.info(f"  ✓ Wrote: {vault_mcp_file}")

    logger.info("Core agents workflow complete")
    return state
