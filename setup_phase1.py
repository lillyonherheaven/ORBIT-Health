import os
from pathlib import Path

# 1. إنشاء شجرة المجلدات بالكامل
folders = [
    "backend/app/contracts",
    "backend/app/sources",
    "backend/app/ingestion",
    "backend/app/store",
    "backend/app/baseline",
    "backend/app/risk",
    "backend/app/guidance",
    "backend/app/sync",
    "backend/app/scenarios",
    "backend/app/api",
    "backend/config",
    "backend/tests",
    "backend/eval",
    "frontend/src/components",
    "frontend/src/pages",
    "frontend/src/api",
    "frontend/src/charts",
    "frontend/src/bodymap",
    "frontend/public",
    "docs",
]

for folder in folders:
    Path(folder).mkdir(parents=True, exist_ok=True)

# 2. محتوى ملفات المرحلة الأولى (Contracts, Base Source, FastAPI, Tests)
files = {
    "backend/requirements.txt": """fastapi==0.110.0
uvicorn==0.28.0
pydantic==2.6.4
pandas==2.2.1
numpy==1.26.4
pytest==8.1.1
pyyaml==6.0.1
httpx==0.27.0
""",
    "backend/app/__init__.py": "",
    "backend/app/ingestion/__init__.py": "",
    "backend/app/store/__init__.py": "",
    "backend/app/baseline/__init__.py": "",
    "backend/app/risk/__init__.py": "",
    "backend/app/guidance/__init__.py": "",
    "backend/app/sync/__init__.py": "",
    "backend/app/api/__init__.py": "",
    "backend/tests/__init__.py": "",
    "backend/app/contracts/__init__.py": """from .observation import Observation, MetricType, QualityType, KindType
from .risk_event import RiskEvent, RiskState, EvidenceItem, DataQualityInfo, ExplanationObj, PlaybookRef
from .playbook import Playbook
from .checkin import DailyCheckin

__all__ = [
    "Observation", "MetricType", "QualityType", "KindType",
    "RiskEvent", "RiskState", "EvidenceItem", "DataQualityInfo", "ExplanationObj", "PlaybookRef",
    "Playbook", "DailyCheckin"
]
""",
    "backend/app/contracts/observation.py": """from typing import Literal, Dict, Any
from pydantic import BaseModel, Field

MetricType = Literal[
    "heart_rate_resting",
    "heart_rate_exercise",
    "hrv",
    "blood_pressure_sys",
    "blood_pressure_dia",
    "spo2",
    "respiratory_rate",
    "temperature",
    "glucose",
    "sleep_duration",
    "mood",
    "exercise_completion",
    "co2",
    "o2",
    "cabin_pressure",
    "radiation_dose",
]

QualityType = Literal["good", "degraded", "missing", "noisy"]
KindType = Literal["measured", "estimated", "self_report"]

class Observation(BaseModel):
    id: str = Field(..., min_length=1)
    astronaut_id: str = Field(..., min_length=1)
    metric: MetricType
    value: float
    unit: str = Field(..., min_length=1)
    source: str = Field(..., min_length=1)
    measured_at: str = Field(..., min_length=1)
    received_at: str = Field(..., min_length=1)
    quality: QualityType
    kind: KindType
    context: Dict[str, Any] = Field(default_factory=dict)
""",
    "backend/app/contracts/risk_event.py": """from typing import Literal, List, Optional
from pydantic import BaseModel, Field

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

class DataQualityInfo(BaseModel):
    completeness: float = Field(..., ge=0.0, le=1.0)
    confidence: Literal["high", "moderate", "low", "insufficient"]

class ExplanationObj(BaseModel):
    what_changed: str = Field(..., min_length=1)
    why_it_matters: str = Field(..., min_length=1)
    next_action: str = Field(..., min_length=1)

class PlaybookRef(BaseModel):
    id: str = Field(..., min_length=1)
    version: int = Field(..., ge=1)

class RiskEvent(BaseModel):
    id: str = Field(..., min_length=1)
    idempotency_key: str = Field(..., min_length=1)
    astronaut_id: str = Field(..., min_length=1)
    domain: str = Field(..., min_length=1)
    state: RiskState
    triggered_at: str = Field(..., min_length=1)
    evidence: List[EvidenceItem] = Field(default_factory=list)
    rules_triggered: List[str] = Field(default_factory=list)
    data_quality: DataQualityInfo
    explanation: ExplanationObj
    playbook: PlaybookRef
    crew_response: Optional[str] = None
    reassessment_due: str = Field(..., min_length=1)
    tx_status: TxStatus = "queued"
    delivery_status: DeliveryStatus = "pending"
    ack_status: AckStatus = "none"
""",
    "backend/app/contracts/playbook.py": """from typing import Literal
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
""",
    "backend/app/contracts/checkin.py": """from typing import List, Optional
from pydantic import BaseModel, Field

class DailyCheckin(BaseModel):
    astronaut_id: str = Field(..., min_length=1)
    date: str = Field(..., min_length=1)
    physical_status: str = Field(..., min_length=1)
    restedness: str = Field(..., min_length=1)
    stress: str = Field(..., min_length=1)
    mood: str = Field(..., min_length=1)
    symptoms: List[str] = Field(default_factory=list)
    free_text: Optional[str] = None
""",
    "backend/app/sources/__init__.py": """from .base import DataSource, SourceInfo
__all__ = ["DataSource", "SourceInfo"]
""",
    "backend/app/sources/base.py": """from typing import Protocol, Iterator, List, runtime_checkable
from pydantic import BaseModel
from app.contracts.observation import Observation

class SourceInfo(BaseModel):
    name: str
    metrics: List[str]
    units: dict
    cadence: str

@runtime_checkable
class DataSource(Protocol):
    def stream(self) -> Iterator[Observation]:
        ...
    def describe(self) -> SourceInfo:
        ...
""",
    "backend/app/main.py": """from fastapi import FastAPI

app = FastAPI(
    title="ORBIT Health API",
    description="Astronaut Health Monitoring & Decision Support System (ILLUSTRATIVE DEMO)",
    version="2.0.0"
)

@app.get("/health")
def health_check():
    return {"status": "ok", "mode": "offline-first", "thresholds": "ILLUSTRATIVE"}
""",
    "backend/tests/test_contracts.py": """import pytest
from pydantic import ValidationError
from app.contracts import Observation, RiskEvent, Playbook, DailyCheckin

def test_observation_appendix_d():
    data = {
        "id": "obs_000123",
        "astronaut_id": "A01",
        "metric": "heart_rate_resting",
        "value": 66,
        "unit": "bpm",
        "source": "wearable_sim_01",
        "measured_at": "2026-03-14T06:12:00Z",
        "received_at": "2026-03-14T06:12:03Z",
        "quality": "good",
        "kind": "measured",
        "context": {"state": "rest", "mission_day": 86, "phase": "steady"}
    }
    obs = Observation(**data)
    assert obs.id == "obs_000123"
    assert obs.value == 66.0

def test_observation_invalid_metric():
    with pytest.raises(ValidationError):
        Observation(
            id="obs_1", astronaut_id="A01", metric="invalid_metric",
            value=50, unit="bpm", source="sim",
            measured_at="2026-03-14T00:00:00Z", received_at="2026-03-14T00:00:00Z",
            quality="good", kind="measured"
        )

def test_risk_event_appendix_d():
    data = {
        "id": "evt_000045",
        "idempotency_key": "A01-trend-hr-sleep-86",
        "astronaut_id": "A01",
        "domain": "cardiovascular_sleep_combined",
        "state": "ORANGE",
        "triggered_at": "2026-03-14T08:00:00Z",
        "evidence": [
            {"metric": "heart_rate_resting", "baseline": 62, "current": 71, "robust_z": 2.9, "persistence": "4_of_5"},
            {"metric": "sleep_duration", "baseline": 7.1, "current": 5.4, "robust_z": -2.4, "persistence": "5_of_5"}
        ],
        "rules_triggered": ["R-CV-TREND-01 (ILLUSTRATIVE)", "R-COMBO-02 (ILLUSTRATIVE)"],
        "data_quality": {"completeness": 0.94, "confidence": "moderate"},
        "explanation": {
            "what_changed": "Resting heart rate and sleep duration have deviated from the personal baseline across repeated observations.",
            "why_it_matters": "Persistent changes across several signals can merit assessment.",
            "next_action": "Open playbook PB-CV-ASSESS v1 and confirm measurement quality."
        },
        "playbook": {"id": "PB-CV-ASSESS", "version": 1},
        "crew_response": None,
        "reassessment_due": "2026-03-14T20:00:00Z",
        "tx_status": "queued",
        "delivery_status": "pending",
        "ack_status": "none"
    }
    evt = RiskEvent(**data)
    assert evt.state == "ORANGE"
    assert len(evt.evidence) == 2

def test_playbook_appendix_d():
    data = {
        "id": "PB-CV-ASSESS",
        "version": 1,
        "domain": "cardiovascular",
        "trigger": "R-CV-TREND-01",
        "required_confidence": "moderate",
        "initial_action": "Repeat the measurement with the approved device and confirm sensor contact.",
        "escalation_condition": "Symptoms reported or deviation persists after repeat measurement.",
        "reassessment_rule": "Reassess within 12 hours.",
        "responsible_authority": "onboard_medical_officer",
        "approval_status": "ILLUSTRATIVE",
        "offline_available": True
    }
    pb = Playbook(**data)
    assert pb.approval_status == "ILLUSTRATIVE"
    assert pb.offline_available is True

def test_daily_checkin_appendix_d():
    data = {
        "astronaut_id": "A01",
        "date": "2026-03-14",
        "physical_status": "a_little_different",
        "restedness": "tired",
        "stress": "moderate",
        "mood": "neutral",
        "symptoms": ["headache_mild"],
        "free_text": None
    }
    chk = DailyCheckin(**data)
    assert chk.symptoms == ["headache_mild"]
"""
}

for filepath, content in files.items():
    p = Path(filepath)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")

print("Phase 1 structure and files generated successfully!")