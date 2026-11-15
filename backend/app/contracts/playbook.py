from typing import Literal
from pydantic import BaseModel, Field

class Playbook(BaseModel):
    id: str = Field(..., min_length=1)
    version: int = Field(..., ge=1)
    domain: str = Field(..., min_length=1)
    trigger: str = Field(..., min_length=1)
    required_confidence: Literal["high", "moderate", "low", "any"]
    initial_action: str = Field(..., min_length=1)
    escalation_condition: str = Field(..., min_length=1)
    reassessment_rule: str = Field(..., min_length=1)
    responsible_authority: str = Field(..., min_length=1)
    approval_status: Literal["ILLUSTRATIVE"] = "ILLUSTRATIVE"
    offline_available: bool = True
