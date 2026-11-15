import random
from typing import Iterator, Dict, Any, Optional, List
from app.contracts.observation import Observation
from app.sources.base import SourceInfo

BASELINES = {
    "A01": {
        "heart_rate_resting": (62.0, "bpm"),
        "sleep_duration": (7.2, "h"),
        "fatigue_self_report": (1.5, "ordinal_1_5"),
        "exercise_performance_index": (98.0, "percent_of_personal_baseline"),
        "exercise_completion": (96.0, "%"),
        "glucose": (92.0, "mg/dL"),
        "spo2": (98.0, "%"),
        "temperature": (36.6, "C"),
        "sustained_attention_task": (92.0, "task_score"),
        "visual_change": (0.0, "report_code"),
        "co2": (2.8, "mmHg"),
        "radiation_dose": (0.45, "mSv/day"),
    },
    "A02": {
        "heart_rate_resting": (58.0, "bpm"),
        "sleep_duration": (7.5, "h"),
        "fatigue_self_report": (1.2, "ordinal_1_5"),
        "exercise_performance_index": (99.0, "percent_of_personal_baseline"),
        "exercise_completion": (98.0, "%"),
        "glucose": (88.0, "mg/dL"),
        "spo2": (99.0, "%"),
        "sustained_attention_task": (89.5, "task_score"),
        "co2": (2.8, "mmHg"),
        "radiation_dose": (0.45, "mSv/day"),
    },
    "A03": {
        "heart_rate_resting": (67.0, "bpm"),
        "sleep_duration": (6.9, "h"),
        "fatigue_self_report": (1.8, "ordinal_1_5"),
        "exercise_performance_index": (95.0, "percent_of_personal_baseline"),
        "exercise_completion": (94.0, "%"),
        "glucose": (95.0, "mg/dL"),
        "spo2": (98.0, "%"),
        "sustained_attention_task": (94.2, "task_score"),
        "co2": (2.8, "mmHg"),
        "radiation_dose": (0.45, "mSv/day"),
    }
}

SCENARIO_SEEDS = {
    "normal": 42,
    "scenario_a": 4101,
    "scenario_b": 939,
    "scenario_c": 816,
}

class SyntheticSource:
    def __init__(
        self,
        seed: Optional[int] = None,
        scenario: str = "normal",
        days: int = 10,
        astronaut_id: str = "A01",
        faults: Optional[Dict[str, Any]] = None
    ):
        self.scenario = scenario
        self.seed = seed if seed is not None else SCENARIO_SEEDS.get(scenario, 42)
        self.days = days
        self.astronaut_id = astronaut_id
        self.faults = faults or {}

    def describe(self) -> SourceInfo:
        base = BASELINES.get(self.astronaut_id, BASELINES["A01"])
        return SourceInfo(
            name=f"synthetic_{self.scenario}_seed_{self.seed}",
            metrics=list(base.keys()),
            units={k: v[1] for k, v in base.items()},
            cadence="daily_summary"
        )

    def stream(self) -> Iterator[Observation]:
        rng = random.Random(self.seed)
        base = BASELINES.get(self.astronaut_id, BASELINES["A01"])
        records: List[Observation] = []
        obs_counter = 1

        for day in range(1, self.days + 1):
            ts = f"2026-03-{day:02d}T08:00:00Z"
            for metric, (base_val, unit) in base.items():
                if self.faults.get("missing_metric") == metric and day == self.faults.get("missing_day", day):
                    obs = Observation(
                        id=f"obs_{obs_counter:06d}",
                        astronaut_id=self.astronaut_id,
                        metric=metric,
                        value=0.0,
                        unit=unit,
                        source="wearable_sim_01",
                        measured_at=ts,
                        received_at=ts,
                        quality="missing",
                        kind="measured",
                        context={"state": "rest", "mission_day": day, "phase": "steady", "label": "ILLUSTRATIVE DEMO VALUE"}
                    )
                    records.append(obs)
                    obs_counter += 1
                    continue

                if self.faults.get("unmapped_unit_metric") == metric and day == self.faults.get("unmapped_day", day):
                    unit = "source_unit_required"

                noise = 0.0 if metric == "visual_change" else rng.gauss(0, 0.25)
                val = base_val + noise

                # Section 12.4 Scenario A (seed 4101): Muscle/metabolic/fatigue drift (OSD-684)
                if self.scenario == "scenario_a" and day > 3:
                    drift_days = day - 3
                    if metric == "exercise_performance_index":
                        val = max(60.0, base_val - 3.8 * drift_days)
                    elif metric == "exercise_completion":
                        val = max(55.0, base_val - 4.2 * drift_days)
                    elif metric == "sleep_duration":
                        val = max(4.2, base_val - 0.35 * drift_days)
                    elif metric == "fatigue_self_report":
                        val = min(5.0, base_val + 0.45 * drift_days)
                    elif metric == "heart_rate_resting":
                        val = base_val + 2.1 * drift_days
                    elif metric == "glucose":
                        val = base_val + 2.8 * drift_days

                # Section 12.4 Scenario B (seed 939): Radiation event + vigilance change (OSD-939, OSD-1010)
                elif self.scenario == "scenario_b" and day >= 4:
                    if metric == "radiation_dose":
                        val = 4.8
                    elif metric == "sustained_attention_task":
                        val = base_val - 14.5
                    elif metric == "fatigue_self_report":
                        val = 4.2

                # Section 12.4 Scenario C (seed 816): Cabin CO2 hazard + SANS visual context + offline (OSD-816)
                elif self.scenario == "scenario_c" and day >= 4:
                    if metric == "co2":
                        val = 6.2
                    elif metric == "visual_change":
                        val = 1.0

                quality = "good"
                if self.faults.get("noisy_day") == day and self.faults.get("noisy_metric") == metric:
                    val = base_val + 25.0
                    quality = "noisy"

                kind = "measured"
                if metric in ("sleep_duration", "exercise_performance_index"):
                    kind = "estimated"
                elif metric in ("fatigue_self_report", "visual_change"):
                    kind = "self_report"

                obs = Observation(
                    id=f"obs_{obs_counter:06d}",
                    astronaut_id=self.astronaut_id,
                    metric=metric,
                    value=round(val, 2),
                    unit=unit,
                    source="BRSMPT_Campaign_1_Ares" if metric == "sustained_attention_task" else "wearable_sim_01",
                    measured_at=ts,
                    received_at=ts,
                    quality=quality,
                    kind=kind,
                    context={"state": "rest", "mission_day": day, "phase": "steady", "label": "ILLUSTRATIVE DEMO VALUE"}
                )
                records.append(obs)
                obs_counter += 1

        for r in records:
            yield r
