from typing import Literal, Dict, Any, Union
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
    "fatigue_self_report",
    "exercise_completion",
    "exercise_performance_index",
    "co2",
    "o2",
    "cabin_pressure",
    "radiation_dose",
    "radiation_dose_rate",
    "visual_change",
    "sustained_attention_task",
]

QualityType = Literal["good", "suspect", "invalid", "missing", "degraded", "noisy"]
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
