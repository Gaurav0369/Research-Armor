from typing import Any
from fastmcp import Client

class MCPManager:
    def __init__(self):
        self.clients: dict[str, Client] = {}
        self.tools: dict[str, dict[str, Any]] = {}

    def add_client(self, name: str, transport):
        self.clients[name] = Client(transport)

    def get_client(self, name: str) -> Client:
        return self.clients[name]

    async def discover_tools(self, server_name: str):
        """
        Discover all tools exposed by an MCP server and
        store them in the registry.
        """
        client = self.get_client(server_name)

        async with client:
            tools = await client.list_tools()

        for tool in tools:
            self.tools[tool.name] = {
                "server": server_name,
                "tool": tool,
            }

        return tools

    def get_tools(self):
        return self.tools

    def get_tool_definitions(self):
        """
        Returns every discovered MCP tool.
        """
        return list(self.tools.values())

    async def call_tool(
        self,
        tool_name: str,
        arguments: dict,
    ):
        """
        Delegates execution directly to the specific MCP Server.
        (Policy enforcement is now handled higher up by the PolicyToolset)
        """
        tool_info = self.tools.get(tool_name)

        if tool_info is None:
            raise ValueError(
                f"Tool '{tool_name}' not found."
            )

        server_name = tool_info["server"]
        client = self.get_client(server_name)

        async with client:
            return await client.call_tool(
                tool_name,
                arguments,
            )