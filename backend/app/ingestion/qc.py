from typing import List, Set
from app.contracts.observation import Observation

PLAUSIBLE_BOUNDS = {
    "heart_rate_resting": (25.0, 220.0),
    "sleep_duration": (0.0, 24.0),
    "fatigue_self_report": (1.0, 5.0),
    "exercise_performance_index": (0.0, 150.0),
    "exercise_completion": (0.0, 100.0),
    "glucose": (20.0, 600.0),
    "spo2": (50.0, 100.0),
    "temperature": (32.0, 43.0),
    "sustained_attention_task": (0.0, 100.0),
    "visual_change": (0.0, 5.0),
    "co2": (0.0, 30.0),
    "radiation_dose": (0.0, 100.0),
}

def process_observations(observations: List[Observation]) -> List[Observation]:
    seen_ids: Set[str] = set()
    cleaned: List[Observation] = []

    for obs in observations:
        if obs.id in seen_ids:
            continue
        seen_ids.add(obs.id)

        quality = obs.quality
        # Section 12.3 rule: source_unit_required sentinel or unknown unit -> quarantine as invalid/missing
        if obs.unit == "source_unit_required" or "assay_raw" in obs.unit:
            quality = "invalid"
        elif quality not in ("missing", "invalid"):
            bounds = PLAUSIBLE_BOUNDS.get(obs.metric)
            if bounds and not (bounds[0] <= obs.value <= bounds[1]):
                quality = "degraded"

        cleaned.append(obs.model_copy(update={"quality": quality}))

    cleaned.sort(key=lambda o: o.measured_at)
    return cleaned
