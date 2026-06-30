from pathlib import Path

from fastmcp.client.transports import StreamableHttpTransport
from fastmcp.client.transports import StdioTransport

from .manager import MCPManager

manager = MCPManager()

# ---------------------------------------------------------------------
# Project root
# ---------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent.parent

WORKSPACE_SERVER = (
    ROOT
    / "mcp_servers"
    / "workspace"
    / "server.py"
)

# ---------------------------------------------------------------------
# Register MCP Servers
# ---------------------------------------------------------------------

manager.add_client(
    "exa",
    StreamableHttpTransport(
        "https://mcp.exa.ai/mcp",
    ),
)

manager.add_client(
    "workspace",
    StdioTransport(
        command="python",
        args=[
            str(WORKSPACE_SERVER),
        ],
    ),
)


# ---------------------------------------------------------------------
# Initialize
# ---------------------------------------------------------------------

async def initialize():
    """
    Discover tools from every registered MCP server.
    """

    for server_name in manager.clients.keys():
        print(f"Discovering tools from '{server_name}'...")
        await manager.discover_tools(server_name)

    print("\nDiscovered Tools:")

    for tool_name in manager.get_tools():
        print(f" - {tool_name}")