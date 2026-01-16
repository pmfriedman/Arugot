"""Vault management tools for MCP server."""

import shutil
from pathlib import Path

from settings import settings


class VaultToolError(Exception):
    """Error raised by vault tools with user-friendly messages."""
    pass


def get_vault_path() -> Path:
    """Get the configured vault path, raising clear error if not configured."""
    vault_dir = settings.obsidian_vault_dir
    if not vault_dir:
        raise VaultToolError(
            "Vault directory not configured. Set OBSIDIAN_VAULT_DIR in .env"
        )
    
    vault_path = Path(vault_dir)
    if not vault_path.exists():
        raise VaultToolError(f"Vault directory does not exist: {vault_dir}")
    
    return vault_path


def archive_file(filename: str) -> str:
    """Move a file from _inbox/ to _archive/.
    
    Args:
        filename: The filename (not full path) to archive
        
    Returns:
        Success message with the archived file path
        
    Raises:
        VaultToolError: If file doesn't exist or operation fails
    """
    vault_path = get_vault_path()
    inbox_dir = vault_path / "_inbox"
    archive_dir = vault_path / "_archive"
    
    # Validate inbox exists
    if not inbox_dir.exists():
        raise VaultToolError(f"Inbox directory does not exist: {inbox_dir}")
    
    # Build source path and validate
    source_path = inbox_dir / filename
    if not source_path.exists():
        raise VaultToolError(f"File not found in inbox: {filename}")
    
    if not source_path.is_file():
        raise VaultToolError(f"Path is not a file: {filename}")
    
    # Ensure archive directory exists
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    # Move file to archive
    dest_path = archive_dir / filename
    
    # Handle case where file already exists in archive
    if dest_path.exists():
        # Add timestamp suffix to avoid overwriting
        stem = source_path.stem
        suffix = source_path.suffix
        counter = 1
        while dest_path.exists():
            dest_path = archive_dir / f"{stem}_{counter}{suffix}"
            counter += 1
    
    try:
        shutil.move(str(source_path), str(dest_path))
    except Exception as e:
        raise VaultToolError(f"Failed to move file: {e}")
    
    return f"Archived: {filename} → _archive/{dest_path.name}"
