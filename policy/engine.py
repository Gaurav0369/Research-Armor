import asyncio
import re
from policy.models import PolicyDecision
from policy import store

# Common phrases used in LLM prompt injection / jailbreak attacks
INJECTION_SIGNATURES = [
    "ignore previous instructions",
    "ignore all previous instructions",
    "system prompt",
    "forget all",
    "bypass constraints",
    "jailbreak",
    "you are now",
    "developer mode"
]

def scan_for_injection(arguments: dict) -> bool:
    """Scans tool arguments for prompt injection signatures."""
    for key, value in arguments.items():
        if isinstance(value, str):
            text = value.lower()
            for sig in INJECTION_SIGNATURES:
                if sig in text:
                    return True
    return False

async def check(tool_name: str, arguments: dict) -> PolicyDecision:
    """
    Every MCP tool execution passes through here.
    1. Scans for Prompt Injection payloads.
    2. Validates arguments against security regex patterns.
    3. Checks the dynamic store for approval/block rules.
    """
    
    # --- STEP 1: PROMPT INJECTION SCANNER ---
    if scan_for_injection(arguments):
        store.add_log(
            event_type="policy",
            message=f"🛑 Critical: Prompt Injection detected in '{tool_name}'",
            details={
                "arguments": arguments, 
                "decision": "block",
                "reason": "Payload contains known jailbreak signatures."
            }
        )
        return PolicyDecision.BLOCK

    # --- STEP 2: INPUT VALIDATION (Regex) ---
    validators = store.get_validators(tool_name)
    for arg_name, regex_pattern in validators.items():
        if arg_name in arguments:
            arg_value = str(arguments[arg_name])
            if not re.match(regex_pattern, arg_value):
                store.add_log(
                    event_type="policy",
                    message=f"🛑 Security Alert: Malformed input for '{tool_name}'",
                    details={
                        "arguments": arguments, 
                        "decision": "block",
                        "reason": f"Argument '{arg_name}' failed regex validation."
                    }
                )
                return PolicyDecision.BLOCK

    # --- STEP 3: STANDARD POLICY CHECK ---
    decision = store.get_rule(tool_name)
    
    if decision == PolicyDecision.APPROVAL:
        store.add_log(
            event_type="policy",
            message=f"⏳ '{tool_name}' requires human approval. Pausing execution...",
            details={"arguments": arguments, "decision": "pending"}
        )
        
        event = asyncio.Event()
        req_id = store.create_approval_request(tool_name, arguments, event)
        
        await event.wait()
        
        req = store._pending_approvals[req_id]
        if req["status"] == "approved":
            decision = PolicyDecision.ALLOW
        else:
            decision = PolicyDecision.BLOCK

    store.add_log(
        event_type="policy",
        message=f"Agent requested tool '{tool_name}'",
        details={"arguments": arguments, "decision": decision.value}
    )
    
    return decision