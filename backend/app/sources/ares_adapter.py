from typing import Iterator, List, Dict
from app.contracts.observation import Observation
from app.sources.base import SourceInfo

ARES_CAMPAIGN_PROFILES: Dict[str, Dict[str, float]] = {
    "Subject_1": {"srt_ms": 265.0, "running_memory_acc": 91.5, "matching_to_sample_acc": 93.0, "composite_score": 92.0},
    "Subject_2": {"srt_ms": 278.0, "running_memory_acc": 89.0, "matching_to_sample_acc": 90.5, "composite_score": 89.5},
    "Subject_3": {"srt_ms": 254.0, "running_memory_acc": 94.0, "matching_to_sample_acc": 94.5, "composite_score": 94.2},
}

class AresCampaignAdapter:
    def __init__(self, subject_id: str = "Subject_1", days: int = 10, radiation_lag: bool = False):
        self.subject_id = subject_id if subject_id in ARES_CAMPAIGN_PROFILES else "Subject_1"
        self.days = days
        self.radiation_lag = radiation_lag

    def describe(self) -> SourceInfo:
        return SourceInfo(
            name=f"BRSMPT_Campaign_1_Ares_{self.subject_id}",
            metrics=["sustained_attention_task"],
            units={"sustained_attention_task": "task_score"},
            cadence="daily_battery"
        )

    def stream(self) -> Iterator[Observation]:
        profile = ARES_CAMPAIGN_PROFILES[self.subject_id]
        base_score = profile["composite_score"]
        for d in range(1, self.days + 1):
            score = base_score - (d * 0.2)
            if self.radiation_lag and d >= 5:
                score = base_score - 14.5  # ILLUSTRATIVE DEMO VALUE
            yield Observation(
                id=f"ares_{self.subject_id}_d{d:02d}",
                astronaut_id="A01",
                metric="sustained_attention_task",
                value=round(score, 2),
                unit="task_score",
                source=f"BRSMPT_Campaign_1_Ares/{self.subject_id}",
                measured_at=f"2026-03-{d:02d}T08:00:00Z",
                received_at=f"2026-03-{d:02d}T08:00:00Z",
                quality="good",
                kind="measured",
                context={
                    "mission_day": d,
                    "ares_subject": self.subject_id,
                    "battery": ["Simple_Reaction_Time", "Running_Memory", "Matching_to_Sample", "mRTC"],
                    "illustrative": "ILLUSTRATIVE DEMO VALUE"
                }
            )
