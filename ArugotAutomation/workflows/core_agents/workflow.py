"""
Core Agents Workflow

Maintains core custom GitHub Copilot agents and skills.
Generates and updates .agent.md files in .github/agents/
and .SKILL.md files in .github/skills/.
"""

import logging
from pathlib import Path
from typing import Dict, Any
import hashlib

from common.types import RunContext
from settings import settings

logger = logging.getLogger(__name__)

DESCRIPTION = "Maintains core custom GitHub Copilot agents and skills."

# Core agents maintained by this workflow
CORE_AGENTS = ["inbox"]

# Core skills maintained by this workflow
CORE_SKILLS = ["inbox"]


def calculate_checksum(content: str) -> str:
    """Calculate SHA-256 checksum of content."""
    return hashlib.sha256(content.encode()).hexdigest()


def load_agent_template(agent_id: str) -> str:
    """Load agent template from the agents/ subdirectory."""
    template_path = Path(__file__).parent / "agents" / f"{agent_id}.agent.md"
    
    if not template_path.exists():
        raise FileNotFoundError(f"Agent template not found: {template_path}")
    
    return template_path.read_text(encoding="utf-8")


def load_skill_template(skill_id: str) -> str:
    """Load skill template from the skills/ subdirectory."""
    template_path = Path(__file__).parent / "skills" / f"{skill_id}.SKILL.md"
    
    if not template_path.exists():
        raise FileNotFoundError(f"Skill template not found: {template_path}")
    
    return template_path.read_text(encoding="utf-8")


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
    
    # Process each skill
    for skill_id in skills_to_process:
        logger.info(f"Processing skill: {skill_id}")
        
        # Load template from workflow directory
        try:
            template_content = load_skill_template(skill_id)
        except FileNotFoundError as e:
            logger.error(f"  Failed to load template: {e}")
            continue
        
        template_checksum = calculate_checksum(template_content)
        
        # Check if vault file exists and compare checksums
        vault_file = vault_skills_dir / skill_id / "SKILL.md"
        needs_update = True
        
        if vault_file.exists():
            vault_content = vault_file.read_text(encoding="utf-8")
            vault_checksum = calculate_checksum(vault_content)
            
            if vault_checksum == template_checksum:
                logger.info(f"  ✓ Skill '{skill_id}' is up to date")
                needs_update = False
            else:
                logger.info(f"  ! Skill '{skill_id}' has changed (checksum mismatch)")
        else:
            logger.info(f"  + Skill '{skill_id}' does not exist in vault")
        
        # Update if needed
        if needs_update:
            if context.dry_run:
                logger.info(f"  [DRY RUN] Would write: {vault_file}")
                logger.debug(f"Content preview:\n{template_content[:200]}...")
            else:
                vault_file.parent.mkdir(parents=True, exist_ok=True)
                vault_file.write_text(template_content, encoding="utf-8")
                logger.info(f"  ✓ Wrote: {vault_file}")
    
    logger.info("Core agents workflow complete")
    return state
