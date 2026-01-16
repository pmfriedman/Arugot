"""MCP Server for Obsidian vault management.

Run with: uv run python -m mcp_server.server
"""

import logging
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from mcp_server.tools.vault import archive_file, VaultToolError

# Configure logging to stderr (stdout is reserved for MCP protocol)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Create the MCP server
server = Server("arugot-vault")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """Return list of available tools."""
    return [
        Tool(
            name="vault_archive_file",
            description="Move a file from _inbox/ to _archive/ in the Obsidian vault",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "The filename to archive (just the filename, not the full path)",
                    }
                },
                "required": ["filename"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    logger.info(f"Tool called: {name} with args: {arguments}")
    
    try:
        if name == "vault_archive_file":
            filename = arguments.get("filename")
            if not filename:
                return [TextContent(type="text", text="Error: filename is required")]
            
            result = archive_file(filename)
            return [TextContent(type="text", text=result)]
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    except VaultToolError as e:
        # User-friendly errors from our tools
        return [TextContent(type="text", text=f"Error: {e}")]
    
    except Exception as e:
        # Unexpected errors
        logger.exception(f"Unexpected error in tool {name}")
        return [TextContent(type="text", text=f"Unexpected error: {e}")]


async def main():
    """Run the MCP server."""
    logger.info("Starting Arugot Vault MCP server...")
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
