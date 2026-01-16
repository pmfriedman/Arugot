# MCP Server for Obsidian Vault

Model Context Protocol (MCP) server that provides tools for managing the Obsidian vault.

## Running the Server

```bash
uv run python -m mcp_server.server
```

## VS Code Copilot Integration

Add to your VS Code `settings.json`:

```json
{
  "github.copilot.chat.codeGeneration.instructions": [],
  "mcp": {
    "servers": {
      "arugot-vault": {
        "command": "uv",
        "args": ["run", "python", "-m", "mcp_server.server"],
        "cwd": "C:\\dev\\Arugot\\ArugotAutomation"
      }
    }
  }
}
```

## Available Tools

### vault_archive_file

Moves a file from `_inbox/` to `_archive/` in the Obsidian vault.

**Parameters:**
- `filename` (required): The filename to archive (just the filename, not the full path)

**Example:**
```
Archive "20240115-meeting-notes.md"
```

**Behavior:**
- Validates the file exists in `_inbox/`
- Creates `_archive/` if it doesn't exist
- If a file with the same name exists in archive, adds a numeric suffix
- Returns success message or clear error

## Adding New Tools

1. Add tool logic to `mcp_server/tools/` (e.g., `vault.py` for vault operations)
2. Register the tool in `server.py`:
   - Add to `list_tools()` with schema
   - Add handler in `call_tool()`

## Architecture

```
mcp_server/
├── __init__.py
├── server.py          # MCP server setup and tool registration
└── tools/
    ├── __init__.py
    └── vault.py       # Vault management tools
```

The server uses stdio transport for VS Code integration. All vault operations use the `OBSIDIAN_VAULT_DIR` setting from `.env`.
