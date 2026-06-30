from enum import Enum

class PolicyDecision(str, Enum):
    ALLOW = "allow"
    BLOCK = "block"
    APPROVAL = "approval"