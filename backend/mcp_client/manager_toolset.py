from typing import Any
from pydantic_ai import RunContext, ToolDefinition
from pydantic_ai.toolsets import AbstractToolset, ToolsetTool

from .manager import MCPManager


class PassThroughValidator:
    """
    A duck-typed validator that simply returns the input arguments as-is,
    swallowing any extra kwargs (like allow_partial or context) that 
    PydanticAI's internal engine passes during validation.
    """
    def validate_python(self, value: Any, **kwargs) -> Any:
        return value


class MCPWrapperTool(ToolsetTool):
    """
    A dynamic tool wrapper that safely satisfies PydanticAI's internal
    requirements by exposing all expected lifecycle attributes.
    """
    def __init__(self, toolset, tool_def: ToolDefinition):
        self.toolset = toolset
        self.tool_def = tool_def
        self.max_retries = None
        # Use our custom validator to elegantly bypass internal schema checking
        # while swallowing strict kwargs like 'allow_partial'
        self.args_validator = PassThroughValidator()
        self.return_validator = PassThroughValidator()


class ManagerToolset(AbstractToolset):
    """
    Adapter bridging the existing MCPManager to PydanticAI's Toolset API.
    """
    def __init__(self, manager: MCPManager):
        self.manager = manager

    @property
    def id(self) -> str:
        return "mcp_manager_toolset"

    async def get_tools(self, ctx: RunContext) -> dict[str, ToolsetTool]:
        """
        Returns tools discovered by the MCP manager as PydanticAI ToolsetTools.
        """
        tools_dict = {}
        for tool_info in self.manager.get_tool_definitions():
            mcp_tool = tool_info["tool"]
            
            # 1. Create the standard PydanticAI ToolDefinition
            tool_def = ToolDefinition(
                name=mcp_tool.name,
                description=mcp_tool.description or "",
                parameters_json_schema=mcp_tool.inputSchema
            )
            
            # 2. Wrap it in our subclass so PydanticAI can access all required attributes
            ts_tool = MCPWrapperTool(
                toolset=self,
                tool_def=tool_def
            )
            
            tools_dict[mcp_tool.name] = ts_tool
            
        return tools_dict

    async def call_tool(
        self,
        name: str,
        tool_args: dict[str, Any],
        ctx: RunContext,
        tool: ToolsetTool,
    ) -> Any:
        """
        Delegates tool execution to the underlying MCP manager.
        """
        return await self.manager.call_tool(name, tool_args)