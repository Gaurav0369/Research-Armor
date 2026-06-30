
import os

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from agent import chat
from mcp_client.instance import initialize, manager
from policy import store
from policy.models import PolicyDecision


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing MCP Manager...")
    await initialize()
    print("MCP Manager Ready!")
    yield


app = FastAPI(lifespan=lifespan)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


class PolicyUpdateRequest(BaseModel):
    decision: PolicyDecision


class ApprovalResolution(BaseModel):
    approved: bool


@app.get("/")
def root():
    return {"status": "running"}


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    # Estimate tokens: 1 token per 4 characters (standard rough estimate)
    input_tokens = len(request.message) // 4
    store.add_tokens(input_tokens)
    store.add_log("user", f"{request.message} (Usage: ~{input_tokens} tokens)")
    
    response = await chat(request.message)
    
    output_tokens = len(response) // 4
    store.add_tokens(output_tokens)
    store.add_log("agent", f"{response} (Usage: ~{output_tokens} tokens)")
    
    return {"response": response}


@app.get("/api/tokens")
def get_tokens():
    """Returns the total token usage for the conversation."""
    return {"total": store.get_total_tokens()}

# ---------------------------------------------------------------------
# Admin API Endpoints for the Dashboard
# ---------------------------------------------------------------------

@app.get("/api/tools")
def get_tools():
    """
    Returns all dynamically discovered tools so the UI can display them.
    This fulfills the 'no hardcoded tools' UI constraint.
    """
    tools = []
    for t in manager.get_tool_definitions():
        tools.append({
            "name": t["tool"].name,
            "server": t["server"],
            "description": t["tool"].description
        })
    return tools


@app.get("/api/policy")
def get_all_policies():
    """
    Returns the current policy rules for all tools.
    """
    return store.get_all_rules()


@app.post("/api/policy/{tool_name}")
def update_policy(tool_name: str, request: PolicyUpdateRequest):
    """
    Updates the policy rule for a specific tool dynamically.
    """
    store.set_rule(tool_name, request.decision)
    return {"message": f"Policy for '{tool_name}' updated to '{request.decision.value}'"}


@app.get("/api/logs")
def get_logs():
    """Returns the recent conversation and policy logs."""
    return store.get_logs()


@app.get("/api/approvals")
def get_approvals():
    """Returns all tools currently waiting for human approval."""
    return store.get_pending_approvals()


@app.post("/api/approvals/{req_id}")
def resolve_approval(req_id: str, resolution: ApprovalResolution):
    """Resolves an approval request (Approve/Reject)."""
    store.resolve_approval_request(req_id, resolution.approved)
    return {"status": "resolved"}


# ---------------------------------------------------------------------
# Frontend Dashboard Route
# ---------------------------------------------------------------------

@app.get("/dashboard", response_class=HTMLResponse)
def read_dashboard():
    """Serves the frontend dashboard UI."""
    html_path = os.path.join(os.path.dirname(__file__), "dashboard.html")
    with open(html_path, "r") as f:
        return f.read()