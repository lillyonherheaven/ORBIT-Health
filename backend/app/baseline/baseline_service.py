import numpy as np
from typing import Dict, List, Optional
from app.contracts.observation import Observation
from app.store.db import OnboardStore

class PersonalBaselineService:
    def __init__(self, store: Optional[OnboardStore] = None):
        self.store = store
        self.preflight_reference: Dict[str, Dict[str, float]] = {}
        self.inflight_reference: Dict[str, Dict[str, float]] = {}

    def _key(self, astronaut_id: str, metric: str) -> str:
        return f"{astronaut_id}:{metric}"

    def initialize_preflight(self, astronaut_id: str, metric: str, values: List[float]):
        arr = np.array(values, dtype=float)
        median = float(np.median(arr))
        mad = float(np.median(np.abs(arr - median)))
        mad = max(mad, 0.25)
        k = self._key(astronaut_id, metric)
        ref = {"median": median, "mad": mad, "ewma": median}
        self.preflight_reference[k] = dict(ref)
        self.inflight_reference[k] = dict(ref)

    def get_baseline(self, astronaut_id: str, metric: str) -> Dict[str, float]:
        k = self._key(astronaut_id, metric)
        return self.inflight_reference.get(k, {"median": 0.0, "mad": 1.0, "ewma": 0.0})

    def compute_robust_z(self, astronaut_id: str, metric: str, value: float) -> float:
        base = self.get_baseline(astronaut_id, metric)
        denom = 1.4826 * max(base["mad"], 0.2)
        return round((value - base["median"]) / denom, 2)

    def update_inflight(self, obs: Observation, active_alert_above_green: bool = False) -> bool:
        if obs.quality != "good":
            return False
        if active_alert_above_green:
            if self.store:
                self.store.log_audit(
                    obs.measured_at, "baseline_service", "adaptation_blocked",
                    {"astronaut_id": obs.astronaut_id, "metric": obs.metric, "reason": "active_alert_above_green"}
                )
            return False

        k = self._key(obs.astronaut_id, obs.metric)
        if k not in self.inflight_reference:
            self.initialize_preflight(obs.astronaut_id, obs.metric, [obs.value])
            return True

        curr = self.inflight_reference[k]
        old_med = curr["median"]
        # Rate-limited adaptation (max 5% shift per observation)
        new_med = 0.95 * old_med + 0.05 * obs.value
        curr["median"] = round(new_med, 3)
        curr["ewma"] = round(0.8 * curr["ewma"] + 0.2 * obs.value, 3)

        if self.store:
            self.store.log_audit(
                obs.measured_at, "baseline_service", "baseline_adapted",
                {"astronaut_id": obs.astronaut_id, "metric": obs.metric, "old": old_med, "new": curr["median"]}
            )
        return True
