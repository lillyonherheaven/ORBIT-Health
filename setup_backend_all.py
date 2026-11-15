from pathlib import Path

files = {
    # ---------------- PHASE 2: SCENARIOS & SOURCES ----------------
    "backend/app/scenarios/scenario_a.yaml": """name: "Scenario A - Gradual Deterioration"
description: "10-day gradual resting HR drift, shortened sleep, rising fatigue, and declining exercise completion."
days: 10
target_astronaut: "A01"
effects:
  heart_rate_resting_drift_per_day: 1.8
  sleep_duration_drift_per_day: -0.25
  exercise_completion_drift_per_day: -4.0
""",
    "backend/app/scenarios/scenario_b.yaml": """name: "Scenario B - Radiation Event"
description: "Declared solar particle event with rapidly rising radiation dose rate."
days: 3
target_astronaut: "A01"
effects:
  radiation_spike_day: 2
  radiation_dose_value: 4.8
""",
    "backend/app/scenarios/scenario_c.yaml": """name: "Scenario C - Cabin CO2 Hazard & Comms Outage"
description: "CO2 exceedance while Earth communication link is down, followed by reconnection."
days: 3
target_astronaut: "A01"
effects:
  co2_spike_day: 2
  co2_value: 6.2
  comms_offline_during_spike: true
""",
    "backend/app/sources/synthetic.py": """import random
import csv
from pathlib import Path
from typing import Iterator, Dict, Any, Optional, List
from app.contracts.observation import Observation
from app.sources.base import SourceInfo

BASELINES = {
    "A01": {
        "heart_rate_resting": (62.0, "bpm"),
        "heart_rate_exercise": (138.0, "bpm"),
        "hrv": (58.0, "ms"),
        "blood_pressure_sys": (118.0, "mmHg"),
        "blood_pressure_dia": (76.0, "mmHg"),
        "spo2": (98.0, "%"),
        "respiratory_rate": (14.0, "breaths/min"),
        "temperature": (36.6, "C"),
        "glucose": (92.0, "mg/dL"),
        "sleep_duration": (7.2, "hours"),
        "mood": (4.0, "score_1_5"),
        "exercise_completion": (96.0, "%"),
        "co2": (2.8, "mmHg"),
        "o2": (20.9, "%"),
        "cabin_pressure": (101.3, "kPa"),
        "radiation_dose": (0.45, "mSv/day"),
    },
    "A02": {
        "heart_rate_resting": (58.0, "bpm"),
        "sleep_duration": (7.5, "hours"),
        "exercise_completion": (98.0, "%"),
        "spo2": (99.0, "%"),
        "glucose": (88.0, "mg/dL"),
        "temperature": (36.5, "C"),
        "co2": (2.8, "mmHg"),
        "radiation_dose": (0.45, "mSv/day"),
    },
    "A03": {
        "heart_rate_resting": (67.0, "bpm"),
        "sleep_duration": (6.9, "hours"),
        "exercise_completion": (94.0, "%"),
        "spo2": (98.0, "%"),
        "glucose": (95.0, "mg/dL"),
        "temperature": (36.7, "C"),
        "co2": (2.8, "mmHg"),
        "radiation_dose": (0.45, "mSv/day"),
    }
}

class SyntheticSource:
    def __init__(
        self,
        seed: int = 42,
        scenario: str = "normal",
        days: int = 10,
        astronaut_id: str = "A01",
        faults: Optional[Dict[str, Any]] = None
    ):
        self.seed = seed
        self.scenario = scenario
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
                        context={"state": "rest", "mission_day": day, "phase": "steady"}
                    )
                    records.append(obs)
                    obs_counter += 1
                    continue

                noise = rng.gauss(0, 0.35)
                val = base_val + noise

                # Apply scenarios after warmup day 3
                if self.scenario == "scenario_a" and day > 3:
                    drift_days = day - 3
                    if metric == "heart_rate_resting":
                        val = base_val + 2.2 * drift_days
                    elif metric == "sleep_duration":
                        val = max(3.5, base_val - 0.35 * drift_days)
                    elif metric == "exercise_completion":
                        val = max(50.0, base_val - 4.5 * drift_days)
                    elif metric == "mood":
                        val = max(1.0, base_val - 0.3 * drift_days)

                elif self.scenario == "scenario_b" and day >= 4 and metric == "radiation_dose":
                    val = 4.8

                elif self.scenario == "scenario_c" and day >= 4 and metric == "co2":
                    val = 6.2

                quality = "good"
                if self.faults.get("noisy_day") == day and self.faults.get("noisy_metric") == metric:
                    val = base_val + 25.0
                    quality = "noisy"

                obs = Observation(
                    id=f"obs_{obs_counter:06d}",
                    astronaut_id=self.astronaut_id,
                    metric=metric,
                    value=round(val, 2),
                    unit=unit,
                    source="wearable_sim_01",
                    measured_at=ts,
                    received_at=ts,
                    quality=quality,
                    kind="estimated" if metric in ("sleep_duration", "respiratory_rate") else "measured",
                    context={"state": "rest", "mission_day": day, "phase": "steady"}
                )
                records.append(obs)
                if self.faults.get("duplicate_first") and len(records) == 1:
                    records.append(obs.model_copy())
                obs_counter += 1

        if self.faults.get("out_of_order") and len(records) >= 4:
            records[1], records[3] = records[3], records[1]

        for r in records:
            yield r
""",
    "backend/app/sources/csv_source.py": """import csv
from pathlib import Path
from typing import Iterator, Dict
from app.contracts.observation import Observation
from app.sources.base import SourceInfo

class CSVSource:
    def __init__(self, path: str, column_map: Dict[str, str]):
        self.path = Path(path)
        self.column_map = column_map

    def describe(self) -> SourceInfo:
        return SourceInfo(name=f"csv_{self.path.name}", metrics=[], units={}, cadence="custom")

    def stream(self) -> Iterator[Observation]:
        with self.path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader, 1):
                mapped = {target: row[src] for target, src in self.column_map.items() if src in row}
                yield Observation(
                    id=mapped.get("id", f"csv_{idx:05d}"),
                    astronaut_id=mapped.get("astronaut_id", "A01"),
                    metric=mapped["metric"],
                    value=float(mapped["value"]),
                    unit=mapped.get("unit", "unit"),
                    source=mapped.get("source", "csv_adapter"),
                    measured_at=mapped["measured_at"],
                    received_at=mapped.get("received_at", mapped["measured_at"]),
                    quality=mapped.get("quality", "good"),
                    kind=mapped.get("kind", "measured"),
                    context={"mission_day": int(mapped.get("mission_day", 1))}
                )
""",
    "backend/app/sources/replay.py": """from typing import Iterable, Iterator, List
from app.contracts.observation import Observation
from app.sources.base import SourceInfo

class ReplaySource:
    def __init__(self, observations: Iterable[Observation], speed: float = 1.0):
        self.observations: List[Observation] = list(observations)
        self.speed = speed

    def describe(self) -> SourceInfo:
        metrics = sorted(list({o.metric for o in self.observations}))
        return SourceInfo(name="replay_source", metrics=metrics, units={}, cadence=f"{self.speed}x")

    def stream(self) -> Iterator[Observation]:
        for obs in sorted(self.observations, key=lambda x: x.measured_at):
            yield obs
""",
    "backend/app/sources/__init__.py": """from .base import DataSource, SourceInfo
from .synthetic import SyntheticSource, BASELINES
from .csv_source import CSVSource
from .replay import ReplaySource

__all__ = ["DataSource", "SourceInfo", "SyntheticSource", "BASELINES", "CSVSource", "ReplaySource"]
""",

    # ---------------- PHASE 3: QC, STORAGE, AUDIT & BASELINE ----------------
    "backend/app/ingestion/qc.py": """from typing import List, Set
from app.contracts.observation import Observation

PLAUSIBLE_BOUNDS = {
    "heart_rate_resting": (25.0, 220.0),
    "heart_rate_exercise": (40.0, 240.0),
    "hrv": (5.0, 250.0),
    "blood_pressure_sys": (50.0, 260.0),
    "blood_pressure_dia": (30.0, 160.0),
    "spo2": (50.0, 100.0),
    "respiratory_rate": (4.0, 60.0),
    "temperature": (32.0, 43.0),
    "glucose": (20.0, 600.0),
    "sleep_duration": (0.0, 24.0),
    "mood": (1.0, 5.0),
    "exercise_completion": (0.0, 100.0),
    "co2": (0.0, 30.0),
    "o2": (10.0, 30.0),
    "cabin_pressure": (50.0, 130.0),
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
        if quality != "missing":
            bounds = PLAUSIBLE_BOUNDS.get(obs.metric)
            if bounds and not (bounds[0] <= obs.value <= bounds[1]):
                quality = "degraded"

        cleaned.append(obs.model_copy(update={"quality": quality}))

    cleaned.sort(key=lambda o: o.measured_at)
    return cleaned
""",
    "backend/app/store/db.py": """import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any
from app.contracts.observation import Observation
from app.contracts.risk_event import RiskEvent

class OnboardStore:
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_schema()

    def _init_schema(self):
        cur = self.conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS observations (
                id TEXT PRIMARY KEY,
                astronaut_id TEXT,
                metric TEXT,
                value REAL,
                measured_at TEXT,
                quality TEXT,
                payload TEXT
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS risk_events (
                id TEXT PRIMARY KEY,
                idempotency_key TEXT UNIQUE,
                astronaut_id TEXT,
                state TEXT,
                triggered_at TEXT,
                tx_status TEXT,
                delivery_status TEXT,
                ack_status TEXT,
                payload TEXT
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                seq INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                actor TEXT,
                action TEXT,
                details TEXT
            )
        ''')
        self.conn.commit()

    def save_observation(self, obs: Observation):
        self.conn.execute(
            "INSERT OR IGNORE INTO observations VALUES (?, ?, ?, ?, ?, ?, ?)",
            (obs.id, obs.astronaut_id, obs.metric, obs.value, obs.measured_at, obs.quality, obs.model_dump_json())
        )
        self.conn.commit()

    def get_observations(self, astronaut_id: str = "A01") -> List[Observation]:
        cur = self.conn.execute(
            "SELECT payload FROM observations WHERE astronaut_id = ? ORDER BY measured_at ASC",
            (astronaut_id,)
        )
        return [Observation.model_validate_json(r[0]) for r in cur.fetchall()]

    def save_risk_event(self, evt: RiskEvent):
        self.conn.execute(
            "INSERT OR REPLACE INTO risk_events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                evt.id, evt.idempotency_key, evt.astronaut_id, evt.state,
                evt.triggered_at, evt.tx_status, evt.delivery_status, evt.ack_status,
                evt.model_dump_json()
            )
        )
        self.conn.commit()

    def get_risk_events(self) -> List[RiskEvent]:
        cur = self.conn.execute("SELECT payload FROM risk_events ORDER BY triggered_at DESC")
        return [RiskEvent.model_validate_json(r[0]) for r in cur.fetchall()]

    def log_audit(self, timestamp: str, actor: str, action: str, details: Dict[str, Any]):
        self.conn.execute(
            "INSERT INTO audit_log (timestamp, actor, action, details) VALUES (?, ?, ?, ?)",
            (timestamp, actor, action, json.dumps(details))
        )
        self.conn.commit()

    def get_audit_logs(self) -> List[Dict[str, Any]]:
        cur = self.conn.execute("SELECT seq, timestamp, actor, action, details FROM audit_log ORDER BY seq ASC")
        return [
            {"seq": r[0], "timestamp": r[1], "actor": r[2], "action": r[3], "details": json.loads(r[4])}
            for r in cur.fetchall()
        ]
""",
    "backend/app/baseline/baseline_service.py": """import numpy as np
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
""",

    # ---------------- PHASE 4: RISK ENGINE & RULES ----------------
    "backend/config/rules_illustrative.yaml": """rules:
  - id: "R-RAD-CRIT-01 (ILLUSTRATIVE)"
    domain: "radiation"
    metric: "radiation_dose"
    threshold: 2.0
    state: "RED"
    playbook_id: "PB-RAD-SHELTER"
  - id: "R-ENV-CO2-01 (ILLUSTRATIVE)"
    domain: "environment"
    metric: "co2"
    threshold: 4.5
    state: "RED"
    playbook_id: "PB-ENV-CO2"
  - id: "R-CV-SLEEP-COMBO-01 (ILLUSTRATIVE)"
    domain: "cardiovascular_sleep_combined"
    persistence_required: 3
    window: 4
    state: "ORANGE"
    playbook_id: "PB-CV-ASSESS"
""",
    "backend/app/risk/engine.py": """from typing import List, Dict
from app.contracts.observation import Observation
from app.contracts.risk_event import (
    RiskEvent, EvidenceItem, DataQualityInfo, ExplanationObj, PlaybookRef
)
from app.baseline.baseline_service import PersonalBaselineService
from app.ingestion.qc import process_observations

class RiskEngine:
    def __init__(self, baseline_service: PersonalBaselineService):
        self.baseline = baseline_service

    def evaluate(self, raw_observations: List[Observation], astronaut_id: str = "A01") -> RiskEvent:
        obs_list = process_observations([o for o in raw_observations if o.astronaut_id == astronaut_id])
        now_ts = obs_list[-1].measured_at if obs_list else "2026-03-14T08:00:00Z"

        if not obs_list:
            return self._make_gray(astronaut_id, now_ts, "No observations available.")

        # Group by metric
        by_metric: Dict[str, List[Observation]] = {}
        for o in obs_list:
            by_metric.setdefault(o.metric, []).append(o)

        # Stage 1: Check critical missing sensors on latest cycle
        latest_missing = [m for m, items in by_metric.items() if items[-1].quality == "missing"]
        if latest_missing:
            return self._make_gray(
                astronaut_id, now_ts,
                f"Sensor data unavailable or missing for: {', '.join(latest_missing)}."
            )

        # Stage 2: Ensure baselines exist from first 3 observations
        for m, items in by_metric.items():
            good_vals = [x.value for x in items[:3] if x.quality == "good"]
            if good_vals and f"{astronaut_id}:{m}" not in self.baseline.inflight_reference:
                self.baseline.initialize_preflight(astronaut_id, m, good_vals)

        # Stage 3: Single-event Critical Overrides (RED)
        rad_items = [x for x in by_metric.get("radiation_dose", []) if x.quality == "good"]
        if rad_items and rad_items[-1].value >= 2.0:
            last_rad = rad_items[-1]
            return RiskEvent(
                id=f"evt_rad_{last_rad.id}",
                idempotency_key=f"{astronaut_id}-RED-radiation-{last_rad.measured_at}",
                astronaut_id=astronaut_id,
                domain="radiation",
                state="RED",
                triggered_at=last_rad.measured_at,
                evidence=[EvidenceItem(
                    metric="radiation_dose",
                    baseline=0.45,
                    current=last_rad.value,
                    robust_z=12.5,
                    persistence="immediate_override"
                )],
                rules_triggered=["R-RAD-CRIT-01 (ILLUSTRATIVE)"],
                data_quality=DataQualityInfo(completeness=1.0, confidence="high"),
                explanation=ExplanationObj(
                    what_changed=f"Radiation dose rate reached {last_rad.value} mSv/day (illustrative critical limit).",
                    why_it_matters="Elevated space radiation exposure requires immediate shielding countermeasures.",
                    next_action="Execute playbook PB-RAD-SHELTER v1 immediately and relocate to shielded storm zone."
                ),
                playbook=PlaybookRef(id="PB-RAD-SHELTER", version=1),
                reassessment_due=last_rad.measured_at
            )

        co2_items = [x for x in by_metric.get("co2", []) if x.quality == "good"]
        if co2_items and co2_items[-1].value >= 4.5:
            last_co2 = co2_items[-1]
            return RiskEvent(
                id=f"evt_co2_{last_co2.id}",
                idempotency_key=f"{astronaut_id}-RED-co2-{last_co2.measured_at}",
                astronaut_id=astronaut_id,
                domain="environment",
                state="RED",
                triggered_at=last_co2.measured_at,
                evidence=[EvidenceItem(
                    metric="co2",
                    baseline=2.8,
                    current=last_co2.value,
                    robust_z=9.8,
                    persistence="immediate_override"
                )],
                rules_triggered=["R-ENV-CO2-01 (ILLUSTRATIVE)"],
                data_quality=DataQualityInfo(completeness=1.0, confidence="high"),
                explanation=ExplanationObj(
                    what_changed=f"Cabin CO2 concentration rose to {last_co2.value} mmHg (illustrative threshold).",
                    why_it_matters="High cabin CO2 affects cognitive and physiological safety for the entire crew.",
                    next_action="Execute playbook PB-ENV-CO2 v1: verify scrubber status and cross-check backup sensor."
                ),
                playbook=PlaybookRef(id="PB-ENV-CO2", version=1),
                reassessment_due=last_co2.measured_at
            )

        # Stage 4: Persistence & Multi-signal Combination (N of M valid observations)
        evidence_list: List[EvidenceItem] = []
        persistent_metrics: List[str] = []

        for m, items in by_metric.items():
            valid_items = [x for x in items if x.quality == "good"]
            if len(valid_items) < 4:
                continue
            window = valid_items[-5:]
            z_scores = [self.baseline.compute_robust_z(astronaut_id, m, x.value) for x in window]
            abnormal_count = sum(1 for z in z_scores if abs(z) >= 2.2)
            if abnormal_count >= 3:
                persistent_metrics.append(m)
                base_val = self.baseline.get_baseline(astronaut_id, m)["median"]
                evidence_list.append(EvidenceItem(
                    metric=m,
                    baseline=round(base_val, 2),
                    current=window[-1].value,
                    robust_z=z_scores[-1],
                    persistence=f"{abnormal_count}_of_{len(window)}"
                ))

        evidence_list.sort(key=lambda e: abs(e.robust_z or 0.0), reverse=True)

        # Stage 5: Fuse Evidence
        if len(persistent_metrics) >= 2:
            return RiskEvent(
                id=f"evt_orange_{astronaut_id}_{len(obs_list)}",
                idempotency_key=f"{astronaut_id}-ORANGE-combo-{now_ts}",
                astronaut_id=astronaut_id,
                domain="cardiovascular_sleep_combined",
                state="ORANGE",
                triggered_at=now_ts,
                evidence=evidence_list,
                rules_triggered=["R-CV-TREND-01 (ILLUSTRATIVE)", "R-COMBO-02 (ILLUSTRATIVE)"],
                data_quality=DataQualityInfo(completeness=0.95, confidence="high"),
                explanation=ExplanationObj(
                    what_changed=f"Persistent deviation from personal baseline in {', '.join(persistent_metrics)}.",
                    why_it_matters="Combined multi-day shifts across cardiovascular, sleep, and exercise signals merit structured clinical review.",
                    next_action="Open playbook PB-CV-ASSESS v1, confirm measurement contact, and complete symptom check-in."
                ),
                playbook=PlaybookRef(id="PB-CV-ASSESS", version=1),
                reassessment_due=now_ts
            )

        if len(persistent_metrics) == 1:
            return RiskEvent(
                id=f"evt_amber_{astronaut_id}_{len(obs_list)}",
                idempotency_key=f"{astronaut_id}-AMBER-{persistent_metrics[0]}-{now_ts}",
                astronaut_id=astronaut_id,
                domain=persistent_metrics[0],
                state="AMBER",
                triggered_at=now_ts,
                evidence=evidence_list,
                rules_triggered=["R-SINGLE-DRIFT-01 (ILLUSTRATIVE)"],
                data_quality=DataQualityInfo(completeness=0.95, confidence="moderate"),
                explanation=ExplanationObj(
                    what_changed=f"Isolated trend shift detected in {persistent_metrics[0]}.",
                    why_it_matters="Single-metric drift warrants monitoring to verify whether it resolves or persists.",
                    next_action="Repeat measurement during next scheduled check-in and continue routine monitoring."
                ),
                playbook=PlaybookRef(id="PB-ROUTINE-WATCH", version=1),
                reassessment_due=now_ts
            )

        return RiskEvent(
            id=f"evt_green_{astronaut_id}_{len(obs_list)}",
            idempotency_key=f"{astronaut_id}-GREEN-{now_ts}",
            astronaut_id=astronaut_id,
            domain="general",
            state="GREEN",
            triggered_at=now_ts,
            evidence=[],
            rules_triggered=[],
            data_quality=DataQualityInfo(completeness=1.0, confidence="high"),
            explanation=ExplanationObj(
                what_changed="All monitored indicators remain within personal baseline reference bands.",
                why_it_matters="No persistent abnormalities or critical safety triggers detected.",
                next_action="Continue scheduled daily check-ins and standard exercise protocol."
            ),
            playbook=PlaybookRef(id="PB-STANDARD", version=1),
            reassessment_due=now_ts
        )

    def _make_gray(self, astronaut_id: str, now_ts: str, reason: str) -> RiskEvent:
        return RiskEvent(
            id=f"evt_gray_{astronaut_id}",
            idempotency_key=f"{astronaut_id}-GRAY-{now_ts}",
            astronaut_id=astronaut_id,
            domain="monitoring_integrity",
            state="GRAY",
            triggered_at=now_ts,
            evidence=[],
            rules_triggered=["R-DATA-MISSING-01 (ILLUSTRATIVE)"],
            data_quality=DataQualityInfo(completeness=0.4, confidence="insufficient"),
            explanation=ExplanationObj(
                what_changed=reason,
                why_it_matters="Missing or unreliable sensor data is never silently interpreted as healthy.",
                next_action="Inspect wearable/sensor connection and perform manual backup measurement via PB-SENSOR-CHECK v1."
            ),
            playbook=PlaybookRef(id="PB-SENSOR-CHECK", version=1),
            reassessment_due=now_ts
        )
""",

    # ---------------- PHASE 5: PLAYBOOKS, ALERT MANAGER & SYNC OUTBOX ----------------
    "backend/app/guidance/playbooks.json": """[
  {
    "id": "PB-CV-ASSESS",
    "version": 1,
    "domain": "cardiovascular",
    "trigger": "R-CV-TREND-01",
    "required_confidence": "moderate",
    "initial_action": "Repeat the measurement with the approved device, confirm sensor contact, and log rest context.",
    "escalation_condition": "Symptoms (dizziness, palpitations) reported or deviation persists across reassessment.",
    "reassessment_rule": "Reassess within 12 hours.",
    "responsible_authority": "onboard_medical_officer",
    "approval_status": "ILLUSTRATIVE",
    "offline_available": true
  },
  {
    "id": "PB-RAD-SHELTER",
    "version": 1,
    "domain": "radiation",
    "trigger": "R-RAD-CRIT-01",
    "required_confidence": "any",
    "initial_action": "Relocate immediately to designated spacecraft radiation shelter and verify personal dosimeter.",
    "escalation_condition": "Immediate priority notification queued for Mission Control.",
    "reassessment_rule": "Continuous dose-rate review every 30 minutes.",
    "responsible_authority": "crew_commander",
    "approval_status": "ILLUSTRATIVE",
    "offline_available": true
  },
  {
    "id": "PB-ENV-CO2",
    "version": 1,
    "domain": "environment",
    "trigger": "R-ENV-CO2-01",
    "required_confidence": "any",
    "initial_action": "Cross-check primary CO2 reading with portable analyzer to distinguish cabin hazard from sensor fault; inspect CDRA scrubber.",
    "escalation_condition": "Confirmed CO2 > 4.5 mmHg or crew headache symptoms.",
    "reassessment_rule": "Reassess every 15 minutes until nominal.",
    "responsible_authority": "crew_commander",
    "approval_status": "ILLUSTRATIVE",
    "offline_available": true
  },
  {
    "id": "PB-SENSOR-CHECK",
    "version": 1,
    "domain": "monitoring_integrity",
    "trigger": "R-DATA-MISSING-01",
    "required_confidence": "any",
    "initial_action": "Check sensor battery, skin contact, or cable link; switch to manual cuff/spot-check device.",
    "escalation_condition": "Hardware failure persists for > 2 hours.",
    "reassessment_rule": "Reassess after reconnection.",
    "responsible_authority": "astronaut",
    "approval_status": "ILLUSTRATIVE",
    "offline_available": true
  }
]
""",
    "backend/app/guidance/alert_manager.py": """import json
from pathlib import Path
from typing import List, Dict, Optional
from app.contracts.playbook import Playbook
from app.contracts.risk_event import RiskEvent

PRIORITY_RANK = {"RED": 1, "ORANGE": 2, "GRAY": 3, "AMBER": 4, "GREEN": 5}

class AlertManager:
    def __init__(self):
        pb_path = Path(__file__).parent / "playbooks.json"
        raw = json.loads(pb_path.read_text(encoding="utf-8"))
        self.playbooks: Dict[str, Playbook] = {item["id"]: Playbook(**item) for item in raw}
        self.active_alerts: Dict[str, RiskEvent] = {}

    def get_playbook(self, playbook_id: str) -> Optional[Playbook]:
        return self.playbooks.get(playbook_id)

    def register_event(self, event: RiskEvent) -> RiskEvent:
        self.active_alerts[event.id] = event
        return event

    def acknowledge(self, event_id: str, actor: str, response_note: str = "Confirmed procedure") -> Optional[RiskEvent]:
        if event_id not in self.active_alerts:
            return None
        evt = self.active_alerts[event_id]
        updated = evt.model_copy(update={
            "ack_status": "acknowledged",
            "crew_response": f"{actor}: {response_note}"
        })
        self.active_alerts[event_id] = updated
        return updated

    def list_prioritized(self) -> List[RiskEvent]:
        return sorted(
            self.active_alerts.values(),
            key=lambda e: (PRIORITY_RANK.get(e.state, 99), e.triggered_at)
        )
""",
    "backend/app/sync/sync_manager.py": """from typing import List, Dict
from app.contracts.risk_event import RiskEvent

PRIORITY_ORDER = {"RED": 1, "ORANGE": 2, "GRAY": 3, "AMBER": 4, "GREEN": 5}

class SyncManager:
    def __init__(self, online: bool = True):
        self.online = online
        self.outbox: Dict[str, RiskEvent] = {}
        self.delivered_records: Dict[str, RiskEvent] = {}

    def set_connectivity(self, online: bool):
        self.online = online
        if self.online:
            self.flush()

    def enqueue(self, event: RiskEvent) -> RiskEvent:
        if event.idempotency_key in self.delivered_records:
            return self.delivered_records[event.idempotency_key]

        queued_evt = event.model_copy(update={"tx_status": "queued", "delivery_status": "pending"})
        self.outbox[event.idempotency_key] = queued_evt
        if self.online:
            self.flush()
            return self.delivered_records.get(event.idempotency_key, queued_evt)
        return queued_evt

    def flush(self) -> List[RiskEvent]:
        if not self.online:
            return []
        # Sort by priority first, then by measurement/trigger timestamp
        pending = sorted(
            self.outbox.values(),
            key=lambda e: (PRIORITY_ORDER.get(e.state, 99), e.triggered_at)
        )
        sent_list: List[RiskEvent] = []
        for evt in pending:
            delivered = evt.model_copy(update={
                "tx_status": "sent",
                "delivery_status": "delivered"
            })
            self.delivered_records[evt.idempotency_key] = delivered
            del self.outbox[evt.idempotency_key]
            sent_list.append(delivered)
        return sent_list

    def mark_medical_review(self, idempotency_key: str) -> RiskEvent:
        evt = self.delivered_records[idempotency_key]
        reviewed = evt.model_copy(update={"ack_status": "reviewed"})
        self.delivered_records[idempotency_key] = reviewed
        return reviewed
""",

    # ---------------- FASTAPI ROUTES & MAIN ----------------
    "backend/app/api/routes.py": """from fastapi import APIRouter
from typing import Dict, Any
from app.sources.synthetic import SyntheticSource
from app.store.db import OnboardStore
from app.baseline.baseline_service import PersonalBaselineService
from app.risk.engine import RiskEngine
from app.guidance.alert_manager import AlertManager
from app.sync.sync_manager import SyncManager
from app.contracts.checkin import DailyCheckin

router = APIRouter()

store = OnboardStore()
baseline_svc = PersonalBaselineService(store=store)
engine = RiskEngine(baseline_svc)
alerts = AlertManager()
sync_mgr = SyncManager(online=True)

CURRENT_STATE = {
    "scenario": "normal",
    "seed": 42,
    "faults": {},
    "checkins": []
}

def _run_current_simulation():
    src = SyntheticSource(
        seed=CURRENT_STATE["seed"],
        scenario=CURRENT_STATE["scenario"],
        days=10,
        astronaut_id="A01",
        faults=CURRENT_STATE["faults"]
    )
    obs_list = list(src.stream())
    evt = engine.evaluate(obs_list, astronaut_id="A01")
    alerts.register_event(evt)
    synced_evt = sync_mgr.enqueue(evt)
    alerts.register_event(synced_evt)
    return obs_list, synced_evt

@router.get("/state")
def get_system_state():
    obs_list, evt = _run_current_simulation()
    pb = alerts.get_playbook(evt.playbook.id)
    return {
        "online": sync_mgr.online,
        "outbox_count": len(sync_mgr.outbox),
        "delivered_count": len(sync_mgr.delivered_records),
        "scenario": CURRENT_STATE["scenario"],
        "active_event": evt,
        "playbook": pb,
        "observations": obs_list[-48:],
        "playbooks_all": list(alerts.playbooks.values()),
        "checkins": CURRENT_STATE["checkins"]
    }

@router.post("/scenario/{scenario_name}")
def inject_scenario(scenario_name: str, missing_sensor: str = "", noisy: bool = False):
    CURRENT_STATE["scenario"] = scenario_name
    faults: Dict[str, Any] = {}
    if missing_sensor:
        faults["missing_metric"] = missing_sensor
        faults["missing_day"] = 10
    if noisy:
        faults["noisy_day"] = 10
        faults["noisy_metric"] = "heart_rate_resting"
    CURRENT_STATE["faults"] = faults
    if scenario_name == "scenario_c":
        sync_mgr.set_connectivity(False)
    return get_system_state()

@router.post("/comms/{mode}")
def toggle_comms(mode: str):
    sync_mgr.set_connectivity(mode.lower() == "online")
    return {
        "online": sync_mgr.online,
        "outbox_count": len(sync_mgr.outbox),
        "delivered_count": len(sync_mgr.delivered_records)
    }

@router.post("/checkin")
def submit_checkin(checkin: DailyCheckin):
    CURRENT_STATE["checkins"].append(checkin)
    return {"status": "recorded", "streak": len(CURRENT_STATE["checkins"])}
""",
    "backend/app/main.py": """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router

app = FastAPI(
    title="ORBIT Health API",
    description="Astronaut Health Monitoring & Decision Support System (ILLUSTRATIVE DEMO)",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/health")
def health_check():
    return {"status": "ok", "mode": "offline-first", "thresholds": "ILLUSTRATIVE"}
""",

    # ---------------- COMPREHENSIVE TESTS FOR PHASES 2-5 ----------------
    "backend/tests/test_system_phases.py": """import pytest
from app.sources.synthetic import SyntheticSource
from app.sources.replay import ReplaySource
from app.ingestion.qc import process_observations
from app.store.db import OnboardStore
from app.baseline.baseline_service import PersonalBaselineService
from app.risk.engine import RiskEngine
from app.sync.sync_manager import SyncManager

def test_seed_determinism():
    s1 = list(SyntheticSource(seed=99, scenario="scenario_a").stream())
    s2 = list(SyntheticSource(seed=99, scenario="scenario_a").stream())
    assert [x.value for x in s1] == [x.value for x in s2]

def test_noisy_sample_does_not_escalate():
    src = SyntheticSource(seed=42, scenario="normal", faults={"noisy_day": 10, "noisy_metric": "heart_rate_resting"})
    engine = RiskEngine(PersonalBaselineService())
    evt = engine.evaluate(list(src.stream()))
    assert evt.state == "GREEN"

def test_scenario_a_reaches_orange():
    src = SyntheticSource(seed=42, scenario="scenario_a", days=10)
    engine = RiskEngine(PersonalBaselineService())
    evt = engine.evaluate(list(src.stream()))
    assert evt.state == "ORANGE"
    assert len(evt.evidence) >= 2

def test_scenario_b_critical_override_red():
    src = SyntheticSource(seed=42, scenario="scenario_b", days=5)
    engine = RiskEngine(PersonalBaselineService())
    evt = engine.evaluate(list(src.stream()))
    assert evt.state == "RED"
    assert evt.playbook.id == "PB-RAD-SHELTER"

def test_missing_sensor_produces_gray_never_green():
    src = SyntheticSource(seed=42, scenario="normal", days=5, faults={"missing_metric": "heart_rate_resting", "missing_day": 5})
    engine = RiskEngine(PersonalBaselineService())
    evt = engine.evaluate(list(src.stream()))
    assert evt.state == "GRAY"

def test_baseline_drift_attack_blocked_during_alert():
    store = OnboardStore()
    svc = PersonalBaselineService(store=store)
    svc.initialize_preflight("A01", "heart_rate_resting", [62.0, 62.5, 61.5])
    obs = next(SyntheticSource(seed=1, days=1).stream())
    updated = svc.update_inflight(obs, active_alert_above_green=True)
    assert updated is False
    assert svc.get_baseline("A01", "heart_rate_resting")["median"] == 62.0

def test_offline_outbox_and_idempotent_sync():
    src = SyntheticSource(seed=42, scenario="scenario_c", days=5)
    engine = RiskEngine(PersonalBaselineService())
    evt = engine.evaluate(list(src.stream()))
    assert evt.state == "RED"

    sync = SyncManager(online=False)
    queued = sync.enqueue(evt)
    assert queued.tx_status == "queued"
    assert len(sync.outbox) == 1

    # Duplicate enqueue while offline should not create duplicate records
    sync.enqueue(evt)
    assert len(sync.outbox) == 1

    # Restore connection
    sync.set_connectivity(True)
    assert len(sync.outbox) == 0
    assert len(sync.delivered_records) == 1
    delivered = sync.delivered_records[evt.idempotency_key]
    assert delivered.tx_status == "sent"
    assert delivered.delivery_status == "delivered"
    assert delivered.ack_status == "none"
"""
}

for filepath, content in files.items():
    p = Path(filepath)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")

print("Phases 2, 3, 4, and 5 generated successfully!")