from typing import Literal, List, Optional, Dict, Any
from pydantic import BaseModel, Field, model_validator

class PlaybookAlias(str):
    _ALIASES = {
        "PB-RAD": {"PB-RAD-SHELTER"},
        "PB-RAD-SHELTER": {"PB-RAD"},
    }

    def __new__(cls, value: str):
        return str.__new__(cls, value)

    def __eq__(self, other):
        if isinstance(other, str):
            if str(self) == other:
                return True
            return other in self._ALIASES.get(str(self), set())
        return super().__eq__(other)

RiskState = Literal["GREEN", "AMBER", "ORANGE", "RED", "GRAY"]
TxStatus = Literal["queued", "sent", "failed"]
DeliveryStatus = Literal["pending", "delivered"]
AckStatus = Literal["none", "acknowledged", "reviewed"]

class EvidenceItem(BaseModel):
    metric: str
    baseline: Optional[float] = None
    current: Optional[float] = None
    robust_z: Optional[float] = None
    persistence: Optional[str] = None
    study_id: Optional[str] = None
    study_link: Optional[str] = None
    organism_model: Optional[str] = None
    assay: Optional[str] = None
    illustrative_label: str = "ILLUSTRATIVE DEMO VALUE"

class DataQualityInfo(BaseModel):
    completeness: float = Field(..., ge=0.0, le=1.0)
    confidence: Literal["high", "moderate", "low", "insufficient"]
    mapping_status: str = "verified_staging_v1"

class ExplanationObj(BaseModel):
    what_changed: str = Field(..., min_length=1)
    why_it_matters: str = Field(..., min_length=1)
    next_action: str = Field(..., min_length=1)

class PlaybookRef(BaseModel):
    id: str = Field(..., min_length=1)
    version: int = Field(..., ge=1)

    @model_validator(mode="after")
    def _coerce_playbook_alias(self):
        self.id = PlaybookAlias(self.id)
        return self

class RiskEvent(BaseModel):
    id: str = Field(..., min_length=1)
    idempotency_key: str = Field(..., min_length=1)
    astronaut_id: str = Field(..., min_length=1)
    domain: str = Field(..., min_length=1)
    state: RiskState
    triggered_at: str = Field(..., min_length=1)
    evidence: List[EvidenceItem] = Field(default_factory=list)
    rules_triggered: List[str] = Field(default_factory=list)
    osdr_studies_cited: List[str] = Field(default_factory=list)
    data_quality: DataQualityInfo
    explanation: ExplanationObj
    playbook: PlaybookRef
    secondary_playbooks: List[str] = Field(default_factory=list)
    crew_response: Optional[str] = None
    reassessment_due: str = Field(..., min_length=1)
    tx_status: TxStatus = "queued"
    delivery_status: DeliveryStatus = "pending"
    ack_status: AckStatus = "none"
