from typing import Any
from pydantic_ai import RunContext
from pydantic_ai.toolsets import WrapperToolset, ToolsetTool

from policy import engine
from policy.models import PolicyDecision


class PolicyToolset(WrapperToolset):
    """
    Security wrapper that intercepts every tool execution.
    """
    async def call_tool(
        self,
        name: str,
        tool_args: dict[str, Any],
        ctx: RunContext,
        tool: ToolsetTool,
    ) -> Any:
        
        # 1. Run the policy guardrail BEFORE execution
        decision = await engine.check(
            tool_name=name,
            arguments=tool_args,
        )

        if decision == PolicyDecision.BLOCK:
            raise PermissionError(f"Tool '{name}' blocked by policy.")

        if decision == PolicyDecision.APPROVAL:
            raise PermissionError(f"Tool '{name}' requires approval.")

        # 2. If ALLOW, delegate execution to the underlying ManagerToolset
        return await super().call_tool(name, tool_args, ctx, tool)