import sys
from pathlib import Path

# Add the project root to the python path so we can import the 'policy' module
root_dir = str(Path(__file__).resolve().parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel

import backend.config
from backend.mcp_client.instance import initialize, manager
from backend.mcp_client.manager_toolset import ManagerToolset
from policy.wrapper_toolset import PolicyToolset

model = GoogleModel("gemini-3.1-flash-lite")

# 1. Create the adapter bridging PydanticAI and your MCPManager
base_toolset = ManagerToolset(manager)

# 2. Wrap the adapter with the security policy layer
policy_toolset = PolicyToolset(base_toolset)

# 3. Inject it into the Agent dynamically via toolsets
agent = Agent(
    model=model,
    instructions="""
    You are an expert Research Assistant. 
    Your goal is to perform research and manage local files using the provided tools.
    You are operating in a development environment. 
    You must always use the tools provided to fulfill the user's request. 
    Do not decline requests; if a request is unsafe, the underlying policy layer 
    will handle the blocking. Your job is to attempt the tool use as requested.
    """,
    toolsets=[policy_toolset]
)


async def startup():
    """
    Called once when FastAPI starts.
    Discovers tools from every configured MCP server.
    """
    await initialize()
    # Tools are now dynamically populated into the agent at runtime!


async def chat(message: str):
    """
    Agent now automatically calls tools securely.
    """
    result = await agent.run(message)
    return result.output