from typing import Dict, List
import time
import uuid
from .models import PolicyDecision

import re

_total_tokens = 0

def add_tokens(count: int):
    global _total_tokens
    _total_tokens += count

def get_total_tokens():
    return _total_tokens


_rules: Dict[str, PolicyDecision] = {}

# Regex validation rules for specific tool arguments
_validators = {
    "save_note": {"filename": r"^[a-zA-Z0-9_-]+\.(txt|md)$"},
    "read_note": {"filename": r"^[a-zA-Z0-9_-]+\.(txt|md)$"},
    "delete_note": {"filename": r"^[a-zA-Z0-9_-]+\.(txt|md)$"}
}

def get_validators(tool_name: str) -> dict:
    """Returns the regex validators for a given tool."""
    return _validators.get(tool_name, {})

# In-memory list to hold conversation and audit logs.
_logs = []

# In-memory dictionary for pending human approvals
_pending_approvals: Dict[str, dict] = {}


def get_rule(tool_name: str) -> PolicyDecision:
    return _rules.get(tool_name, PolicyDecision.ALLOW)


def set_rule(tool_name: str, decision: PolicyDecision):
    _rules[tool_name] = decision


def get_all_rules() -> dict:
    return {k: v.value for k, v in _rules.items()}


def add_log(event_type: str, message: str, details: dict = None):
    """Saves an event to the audit log."""
    _logs.append({
        "timestamp": time.strftime("%H:%M:%S"),
        "type": event_type,
        "message": message,
        "details": details or {}
    })


def get_logs():
    return _logs[-50:]


def create_approval_request(tool_name: str, arguments: dict, event) -> str:
    """Creates a pending request and stores the asyncio Event."""
    req_id = str(uuid.uuid4())[:8]
    _pending_approvals[req_id] = {
        "id": req_id,
        "tool_name": tool_name,
        "arguments": arguments,
        "status": "pending",
        "event": event,
        "timestamp": time.strftime("%H:%M:%S")
    }
    return req_id


def resolve_approval_request(req_id: str, approved: bool):
    """Resolves a pending request and wakes up the paused agent."""
    if req_id in _pending_approvals:
        _pending_approvals[req_id]["status"] = "approved" if approved else "rejected"
        # This triggers the agent to wake up and continue!
        _pending_approvals[req_id]["event"].set()


def get_pending_approvals() -> List[dict]:
    """Returns all pending requests for the dashboard (excluding the async event objects)."""
    return [
        {k: v for k, v in req.items() if k != "event"}
        for req in _pending_approvals.values()
        if req["status"] == "pending"
    ]