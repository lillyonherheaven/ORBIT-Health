from pathlib import Path

files = {
    # ---------------- 1. CONFIG: OSDR STUDIES & STAGING MAP (SECTION 12) ----------------
    "backend/config/osdr_studies.json": """{
  "OSD-1010": {
    "study_id": "OSD-1010",
    "id_note": "ID correction from supplied OSD-1018",
    "title": "Lacticaseibacillus rhamnosus GG modulates epithelial responses to space-relevant heavy-ion irradiation in a human gut-on-chip",
    "url": "https://osdr.nasa.gov/bio/repo/data/studies/OSD-1010",
    "organism_model": "human_gut_on_chip",
    "assay": "RNA-seq transcriptomics",
    "risk_domains": ["radiation", "gi_immune", "metabolic"],
    "body_map_regions": ["abdomen", "cabin"],
    "playbooks": ["PB-RAD", "PB-GI-IMMUNE", "PB-MET"],
    "evidence_limitation": "In-vitro gut-on-chip model; supports mechanism context only. Does not validate personal risk prediction, clinical thresholds, or probiotic intervention."
  },
  "OSD-684": {
    "study_id": "OSD-684",
    "title": "Human skeletal muscle tissue chip autonomous payload reveals changes in fiber type and metabolic gene expression due to spaceflight",
    "url": "https://osdr.nasa.gov/bio/repo/data/studies/OSD-684",
    "organism_model": "human_myobundle_tissue_chip",
    "assay": "RNA-seq transcriptomics",
    "risk_domains": ["bone_muscle", "metabolic"],
    "body_map_regions": ["limbs", "abdomen"],
    "playbooks": ["PB-MSK", "PB-MET", "PB-RECOVERY"],
    "evidence_limitation": "Human myobundle tissue-chip; not a wearable feed, muscle strength measurement, bone-density measurement, or clinical predictor."
  },
  "OSD-816": {
    "study_id": "OSD-816",
    "title": "The ex vivo human translaminar autonomous system to study spaceflight associated neuro-ocular syndrome pathogenesis",
    "url": "https://osdr.nasa.gov/bio/repo/data/studies/OSD-816",
    "organism_model": "ex_vivo_human_translaminar_ocular_model",
    "assay": "ICP:IOP translaminar pressure & electrophysiology",
    "risk_domains": ["sans_visual"],
    "body_map_regions": ["head"],
    "playbooks": ["PB-SANS"],
    "evidence_limitation": "Ex vivo human ocular model; no consumer wearable ICP:IOP inference, diagnosis, or invented pressure threshold."
  },
  "OSD-939": {
    "study_id": "OSD-939",
    "associated_records": ["OSD-896", "OSD-897"],
    "title": "Deficits in Sustained Attention and Changes in Dopaminergic Protein Levels following Exposure to Proton Radiation",
    "url": "https://osdr.nasa.gov/bio/repo/data/studies/OSD-939",
    "organism_model": "rodent_rPVT_behavioral_and_brain_protein",
    "assay": "Rodent psychomotor vigilance task (rPVT) & dopaminergic protein assay",
    "risk_domains": ["radiation", "behavioral_sleep"],
    "body_map_regions": ["head", "cabin"],
    "playbooks": ["PB-RAD", "PB-BEH-SLEEP"],
    "evidence_limitation": "Animal, strain-specific evidence; motivates cautious vigilance monitoring hypothesis only. Never establishes human dose-response or fitness-for-duty."
  },
  "BRSMPT-ARES-C1": {
    "study_id": "BRSMPT_Campaign_1_Ares",
    "title": "BRSMPT Campaign 1 Ares Analog Behavioral & Cognitive Task Battery (Subjects 1, 2, 3)",
    "url": "local://BRSMPT_Campaign_1_Ares",
    "organism_model": "human_analog_crew_subjects_1_to_3",
    "assay": "Simple Reaction Time, Running Memory, Matching to Sample, mRTC, Obsv_All",
    "risk_domains": ["behavioral_sleep"],
    "body_map_regions": ["head"],
    "playbooks": ["PB-BEH-SLEEP"],
    "evidence_limitation": "Analog campaign cognitive task battery; vigilance change alone never triggers RED and never diagnoses psychiatric conditions."
  }
}
""",
    "backend/config/staging_column_map.yaml": """source_id: orbit_normalized_staging_v1
path: data/normalized_observations.csv
format: csv
encoding: utf-8
delimiter: ","
timezone: UTC
columns:
  observation_id: observation_id
  astronaut_id: astronaut_id
  metric: metric
  value: value
  unit: unit
  source: source
  measured_at: measured_at
  received_at: received_at
  quality: quality
  kind: kind
  context_json: context_json
metric_map:
  heart_rate_resting: {unit: bpm, kind: measured}
  sleep_duration: {unit: h, kind: estimated}
  fatigue_self_report: {unit: ordinal_1_5, kind: self_report}
  exercise_performance_index: {unit: percent_of_personal_baseline, kind: estimated}
  exercise_completion: {unit: "%", kind: measured}
  glucose: {unit: mg/dL, kind: measured}
  radiation_dose_rate: {unit: source_unit_required, kind: measured}
  visual_change: {unit: report_code, kind: self_report}
  sustained_attention_task: {unit: task_score, kind: measured}
  co2: {unit: mmHg, kind: measured}
quality_values: [good, suspect, invalid, missing]
required_fields: [observation_id, astronaut_id, metric, value, unit, source, measured_at, received_at, quality, kind]
unknown_column_policy: reject_with_audit_record
unknown_unit_policy: quarantine_and_set_domain_gray
semantic_mismatch_policy: reject; never_coerce_assay_to_observation
""",

    # ---------------- 2. CONTRACTS (V3 NASA GROUNDED) ----------------
    "backend/app/contracts/osdr_provenance.py": """from typing import Optional
from pydantic import BaseModel, Field

class OSDRProvenance(BaseModel):
    study_id: str = Field(..., min_length=1)
    study_link: str = Field(..., min_length=1)
    version: str = "v1"
    organism_model: str = Field(..., min_length=1)
    tissue: str = Field(..., min_length=1)
    assay: str = Field(..., min_length=1)
    source_file: str = Field(..., min_length=1)
    source_column: str = Field(..., min_length=1)
    original_unit: str = Field(..., min_length=1)
    normalized_unit: str = Field(..., min_length=1)
    transformation: str = "identity_or_baseline_normalized"
    evidence_limitation: str = Field(..., min_length=1)
    license_status: str = "NASA_Open_Science_OSDR"
""",
    "backend/app/contracts/observation.py": """from typing import Literal, Dict, Any, Union
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
""",
    "backend/app/contracts/risk_event.py": """from typing import Literal, List, Optional, Dict, Any
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
""",
    "backend/app/contracts/__init__.py": """from .observation import Observation, MetricType, QualityType, KindType
from .risk_event import RiskEvent, RiskState, EvidenceItem, DataQualityInfo, ExplanationObj, PlaybookRef
from .playbook import Playbook
from .checkin import DailyCheckin
from .osdr_provenance import OSDRProvenance

__all__ = [
    "Observation", "MetricType", "QualityType", "KindType",
    "RiskEvent", "RiskState", "EvidenceItem", "DataQualityInfo", "ExplanationObj", "PlaybookRef",
    "Playbook", "DailyCheckin", "OSDRProvenance"
]
""",

    # ---------------- 3. ARES ADAPTER & SEEDED V3 SIMULATOR ----------------
    "backend/app/sources/ares_adapter.py": """from typing import Iterator, List, Dict
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
""",
    "backend/app/sources/synthetic.py": """import random
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
""",

    # ---------------- 4. INGESTION QC WITH SECTION 12.3 SENTINEL REJECTION ----------------
    "backend/app/ingestion/qc.py": """from typing import List, Set
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
""",

    # ---------------- 5. V3 NASA-GROUNDED PLAYBOOKS (SECTION 5.2 & 12.1) ----------------
    "backend/app/guidance/playbooks.json": """[
  {
    "id": "PB-MSK",
    "version": 1,
    "domain": "bone_muscle",
    "trigger": "R-MSK-MET-DRIFT-01 (ILLUSTRATIVE DEMO VALUE)",
    "required_confidence": "moderate",
    "initial_action": "Review resistance/aerobic exercise adherence and workload logs; inspect ARED/treadmill hardware and ask crew about localized pain or fatigue (OSD-684 context).",
    "escalation_condition": "Persistent multi-day decline in exercise performance index alongside fatigue or metabolic drift.",
    "reassessment_rule": "Reassess after next scheduled training session (within 24 hours).",
    "responsible_authority": "onboard_medical_officer",
    "approval_status": "ILLUSTRATIVE",
    "offline_available": true
  },
  {
    "id": "PB-MET",
    "version": 1,
    "domain": "metabolic",
    "trigger": "R-MSK-MET-DRIFT-01 (ILLUSTRATIVE DEMO VALUE)",
    "required_confidence": "moderate",
    "initial_action": "Verify fasting/post-meal context for approved glucose monitor reading and review hydration/nutrition intake log (OSD-684 / OSD-1010 context).",
    "escalation_condition": "Repeated out-of-range glucose trend or associated GI/fatigue symptoms.",
    "reassessment_rule": "Reassess within 12 hours.",
    "responsible_authority": "onboard_medical_officer",
    "approval_status": "ILLUSTRATIVE",
    "offline_available": true
  },
  {
    "id": "PB-BEH-SLEEP",
    "version": 1,
    "domain": "behavioral_sleep",
    "trigger": "R-BEH-VIG-01 (ILLUSTRATIVE DEMO VALUE)",
    "required_confidence": "moderate",
    "initial_action": "Review sleep duration vs. schedule, voluntary fatigue check-in, and BRSMPT Ares sustained-attention task trend (OSD-939 context); offer private rest/workload countermeasures.",
    "escalation_condition": "Persistent sleep deficit or vigilance decline impacting safety-critical tasks.",
    "reassessment_rule": "Reassess after next rest period (12 hours).",
    "responsible_authority": "onboard_medical_officer",
    "approval_status": "ILLUSTRATIVE",
    "offline_available": true
  },
  {
    "id": "PB-RAD",
    "version": 1,
    "domain": "radiation",
    "trigger": "R-RAD-CRIT-01 (ILLUSTRATIVE DEMO VALUE)",
    "required_confidence": "any",
    "initial_action": "Execute spacecraft radiation shelter procedure immediately; verify personal dosimeter rate and log subsequent vigilance (OSD-939) and GI symptoms (OSD-1010).",
    "escalation_condition": "Immediate priority store-and-forward alert queued for Mission Control.",
    "reassessment_rule": "Continuous dosimeter reassessment every 30 minutes.",
    "responsible_authority": "crew_commander",
    "approval_status": "ILLUSTRATIVE",
    "offline_available": true
  },
  {
    "id": "PB-GI-IMMUNE",
    "version": 1,
    "domain": "gi_immune",
    "trigger": "R-RAD-GI-01 (ILLUSTRATIVE DEMO VALUE)",
    "required_confidence": "moderate",
    "initial_action": "Open structured GI/immune symptom check-in and hydration support pathway in radiation exposure context (OSD-1010 human gut-on-chip context).",
    "escalation_condition": "Persistent GI symptoms or fever following elevated radiation dose.",
    "reassessment_rule": "Reassess every 6 hours.",
    "responsible_authority": "onboard_medical_officer",
    "approval_status": "ILLUSTRATIVE",
    "offline_available": true
  },
  {
    "id": "PB-ENV",
    "version": 1,
    "domain": "environment",
    "trigger": "R-ENV-CO2-01 (ILLUSTRATIVE DEMO VALUE)",
    "required_confidence": "any",
    "initial_action": "Cross-check primary cabin CO2 sensor with portable analyzer to distinguish true environmental hazard from sensor failure; inspect scrubber equipment.",
    "escalation_condition": "Confirmed cabin CO2 exceedance or crew headache/visual symptoms.",
    "reassessment_rule": "Reassess every 15 minutes until nominal.",
    "responsible_authority": "crew_commander",
    "approval_status": "ILLUSTRATIVE",
    "offline_available": true
  },
  {
    "id": "PB-SANS",
    "version": 1,
    "domain": "sans_visual",
    "trigger": "R-SANS-VIS-01 (ILLUSTRATIVE DEMO VALUE)",
    "required_confidence": "moderate",
    "initial_action": "Record visual change report and open scheduled onboard ocular assessment protocol (OSD-816 ex vivo translaminar mechanism context; never infer ICP:IOP from wearables).",
    "escalation_condition": "Confirmed visual acuity/fundoscopy change or persistent headache.",
    "reassessment_rule": "Reassess within 24 hours with flight surgeon sync.",
    "responsible_authority": "onboard_medical_officer",
    "approval_status": "ILLUSTRATIVE",
    "offline_available": true
  },
  {
    "id": "PB-SENSOR-CHECK",
    "version": 1,
    "domain": "monitoring_integrity",
    "trigger": "R-DATA-GRAY-01 (ILLUSTRATIVE DEMO VALUE)",
    "required_confidence": "any",
    "initial_action": "Quarantine missing/unmappable feed; inspect sensor connection or staging unit map and perform manual backup verification.",
    "escalation_condition": "Critical monitoring feed unavailable for > 2 hours.",
    "reassessment_rule": "Reassess immediately upon sensor restoration.",
    "responsible_authority": "astronaut",
    "approval_status": "ILLUSTRATIVE",
    "offline_available": true
  }
]
""",

    # ---------------- 6. V3 RISK ENGINE WITH SECTION 12.2 TEMPLATES ----------------
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

        by_metric: Dict[str, List[Observation]] = {}
        for o in obs_list:
            by_metric.setdefault(o.metric, []).append(o)

        # Stage 1: Data Quality & Semantic Quarantine Gate -> GRAY (Never GREEN)
        bad_metrics = [
            m for m, items in by_metric.items()
            if items[-1].quality in ("missing", "invalid")
        ]
        if bad_metrics:
            return self._make_gray(
                astronaut_id,
                now_ts,
                f"Missing, corrupt, or unmappable unit ('source_unit_required') detected on latest cycle for: {', '.join(bad_metrics)}."
            )

        # Stage 2: Initialize Preflight Baselines
        for m, items in by_metric.items():
            good_vals = [x.value for x in items[:3] if x.quality == "good"]
            if good_vals and f"{astronaut_id}:{m}" not in self.baseline.inflight_reference:
                self.baseline.initialize_preflight(astronaut_id, m, good_vals)

        # Stage 3: Critical Overrides (RED) — Note: Vigilance alone NEVER triggers RED (Section 12.4)
        rad_items = [x for x in by_metric.get("radiation_dose", []) if x.quality == "good"]
        if rad_items and rad_items[-1].value >= 2.0:
            last_rad = rad_items[-1]
            att_items = by_metric.get("sustained_attention_task", [])
            att_val = att_items[-1].value if att_items else 90.0
            return RiskEvent(
                id=f"evt_rad_{last_rad.id}",
                idempotency_key=f"{astronaut_id}-RED-radiation-{last_rad.measured_at}",
                astronaut_id=astronaut_id,
                domain="radiation_vigilance_gi_context",
                state="RED",
                triggered_at=last_rad.measured_at,
                evidence=[
                    EvidenceItem(
                        metric="radiation_dose",
                        baseline=0.45,
                        current=last_rad.value,
                        robust_z=12.5,
                        persistence="immediate_override",
                        study_id="OSD-1010",
                        study_link="https://osdr.nasa.gov/bio/repo/data/studies/OSD-1010",
                        organism_model="human_gut_on_chip",
                        assay="Heavy-ion irradiation epithelial RNA-seq"
                    ),
                    EvidenceItem(
                        metric="sustained_attention_task",
                        baseline=92.0,
                        current=att_val,
                        robust_z=-3.8,
                        persistence="contextual_followup",
                        study_id="OSD-939",
                        study_link="https://osdr.nasa.gov/bio/repo/data/studies/OSD-939",
                        organism_model="rodent_rPVT_and_BRSMPT_Ares",
                        assay="Psychomotor vigilance & dopaminergic protein context"
                    )
                ],
                rules_triggered=["R-RAD-CRIT-01 (ILLUSTRATIVE DEMO VALUE)", "R-BEH-VIG-01 (ILLUSTRATIVE DEMO VALUE)"],
                osdr_studies_cited=["OSD-939", "OSD-1010"],
                data_quality=DataQualityInfo(completeness=1.0, confidence="high"),
                explanation=ExplanationObj(
                    what_changed=(
                        f"radiation_dose ({last_rad.value} mSv/day) and sustained_attention_task ({att_val} score) "
                        f"changed from the astronaut's approved baseline over 4d window; source={last_rad.source}; "
                        f"context=flight; quality=good. Rule R-RAD-CRIT-01 applied using ILLUSTRATIVE DEMO VALUE >= 2.0 mSv/day."
                    ),
                    why_it_matters=(
                        "NASA OSDR OSD-939 observed proton-radiation sustained-attention changes in rodent rPVT models, and "
                        "OSD-1010 (corrected from OSD-1018) observed heavy-ion responses in human gut-on-chip RNA-seq. "
                        "This supports monitoring radiation alongside vigilance and GI domains; it does not establish this astronaut's condition or validate this alert."
                    ),
                    next_action=(
                        "Open PB-RAD v1 (ILLUSTRATIVE), plus secondary PB-BEH-SLEEP and PB-GI-IMMUNE; confirm source/data quality "
                        "and follow the approved shelter procedure. Escalate to crew_commander immediately."
                    )
                ),
                playbook=PlaybookRef(id="PB-RAD", version=1),
                secondary_playbooks=["PB-BEH-SLEEP", "PB-GI-IMMUNE"],
                reassessment_due=last_rad.measured_at
            )

        co2_items = [x for x in by_metric.get("co2", []) if x.quality == "good"]
        if co2_items and co2_items[-1].value >= 4.5:
            last_co2 = co2_items[-1]
            return RiskEvent(
                id=f"evt_co2_{last_co2.id}",
                idempotency_key=f"{astronaut_id}-RED-co2-{last_co2.measured_at}",
                astronaut_id=astronaut_id,
                domain="cabin_hazard_and_sans_context",
                state="RED",
                triggered_at=last_co2.measured_at,
                evidence=[
                    EvidenceItem(
                        metric="co2",
                        baseline=2.8,
                        current=last_co2.value,
                        robust_z=9.8,
                        persistence="immediate_override",
                        study_id="OSD-816",
                        study_link="https://osdr.nasa.gov/bio/repo/data/studies/OSD-816",
                        organism_model="ex_vivo_human_translaminar_ocular_model",
                        assay="ICP:IOP translaminar pressure & optic nerve context"
                    )
                ],
                rules_triggered=["R-ENV-CO2-01 (ILLUSTRATIVE DEMO VALUE)", "R-SANS-VIS-01 (ILLUSTRATIVE DEMO VALUE)"],
                osdr_studies_cited=["OSD-816"],
                data_quality=DataQualityInfo(completeness=1.0, confidence="high"),
                explanation=ExplanationObj(
                    what_changed=(
                        f"co2 ({last_co2.value} mmHg) and visual_change self-report changed from baseline over current window; "
                        f"source={last_co2.source}; context=cabin; quality=good. Rule R-ENV-CO2-01 applied using ILLUSTRATIVE DEMO VALUE >= 4.5 mmHg."
                    ),
                    why_it_matters=(
                        "NASA OSDR OSD-816 investigated translaminar pressure (ICP:IOP) in an ex vivo human ocular model for SANS pathogenesis. "
                        "This supports monitoring visual symptoms alongside cabin CO2; it does not infer ICP:IOP from wearables or establish diagnosis."
                    ),
                    next_action=(
                        "Open PB-ENV v1 and PB-SANS v1 (ILLUSTRATIVE); verify CO2 analyzer vs. sensor fault, inspect scrubber, "
                        "and log ocular assessment. Escalate to crew_commander."
                    )
                ),
                playbook=PlaybookRef(id="PB-ENV", version=1),
                secondary_playbooks=["PB-SANS"],
                reassessment_due=last_co2.measured_at
            )

        # Stage 4: Persistence & Multi-signal Combination (Scenario A -> OSD-684)
        evidence_list: List[EvidenceItem] = []
        persistent_metrics: List[str] = []

        for m, items in by_metric.items():
            if m == "visual_change":
                continue
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
                    persistence=f"{abnormal_count}_of_{len(window)} (ILLUSTRATIVE DEMO VALUE)",
                    study_id="OSD-684",
                    study_link="https://osdr.nasa.gov/bio/repo/data/studies/OSD-684",
                    organism_model="human_myobundle_tissue_chip",
                    assay="Skeletal muscle RNA-seq fiber & metabolic gene expression"
                ))

        evidence_list.sort(key=lambda e: abs(e.robust_z or 0.0), reverse=True)

        if len(persistent_metrics) >= 2:
            return RiskEvent(
                id=f"evt_orange_{astronaut_id}_{len(obs_list)}",
                idempotency_key=f"{astronaut_id}-ORANGE-osd684-{now_ts}",
                astronaut_id=astronaut_id,
                domain="muscle_metabolic_fatigue_drift",
                state="ORANGE",
                triggered_at=now_ts,
                evidence=evidence_list,
                rules_triggered=["R-MSK-MET-DRIFT-01 (ILLUSTRATIVE DEMO VALUE)", "R-COMBO-PERSIST-02 (ILLUSTRATIVE DEMO VALUE)"],
                osdr_studies_cited=["OSD-684"],
                data_quality=DataQualityInfo(completeness=0.96, confidence="high"),
                explanation=ExplanationObj(
                    what_changed=(
                        f"{', '.join(persistent_metrics)} changed from the astronaut's approved baseline over 5d window; "
                        f"source=wearable_sim_01; context=steady; quality=good. Rule R-MSK-MET-DRIFT-01 applied using ILLUSTRATIVE DEMO VALUE (3_of_5 persistence, |z|>=2.2)."
                    ),
                    why_it_matters=(
                        "NASA OSDR OSD-684 observed spaceflight-induced fiber-type and metabolic gene expression shifts in human skeletal muscle myobundles using RNA-seq. "
                        "This supports monitoring exercise performance, sleep, and metabolic trends; it does not establish bone/muscle loss or validate this alert."
                    ),
                    next_action=(
                        "Open PB-MSK v1 (ILLUSTRATIVE), plus PB-MET and PB-BEH-SLEEP; confirm source/data quality and follow the approved procedure. "
                        "Escalate to onboard_medical_officer when escalation conditions are met."
                    )
                ),
                playbook=PlaybookRef(id="PB-MSK", version=1),
                secondary_playbooks=["PB-MET", "PB-BEH-SLEEP"],
                reassessment_due=now_ts
            )

        return RiskEvent(
            id=f"evt_green_{astronaut_id}_{len(obs_list)}",
            idempotency_key=f"{astronaut_id}-GREEN-{now_ts}",
            astronaut_id=astronaut_id,
            domain="nominal_monitoring",
            state="GREEN",
            triggered_at=now_ts,
            evidence=[],
            rules_triggered=[],
            osdr_studies_cited=["OSD-684", "OSD-1010", "OSD-816", "OSD-939"],
            data_quality=DataQualityInfo(completeness=1.0, confidence="high"),
            explanation=ExplanationObj(
                what_changed="All monitored physiological, Ares vigilance, exercise, and cabin indicators remain within personal baseline reference bands (ILLUSTRATIVE DEMO VALUE).",
                why_it_matters="NASA OSDR studies (OSD-684, OSD-816, OSD-939, OSD-1010) ground domain selection; current observations show no persistent drift.",
                next_action="Continue scheduled check-ins, Ares cognitive battery, and approved exercise protocol."
            ),
            playbook=PlaybookRef(id="PB-MSK", version=1),
            secondary_playbooks=[],
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
            rules_triggered=["R-DATA-GRAY-01 (ILLUSTRATIVE DEMO VALUE)"],
            osdr_studies_cited=["OSD-816"],
            data_quality=DataQualityInfo(completeness=0.4, confidence="insufficient", mapping_status="quarantined_to_gray"),
            explanation=ExplanationObj(
                what_changed=f"{reason} Rule R-DATA-GRAY-01 applied using ILLUSTRATIVE DEMO VALUE.",
                why_it_matters="Missing, corrupt, stale, or semantically unmappable input ('source_unit_required') yields GRAY, never GREEN.",
                next_action="Open PB-SENSOR-CHECK v1 (ILLUSTRATIVE); confirm source/data quality and restore valid sensor or staging unit mapping."
            ),
            playbook=PlaybookRef(id="PB-SENSOR-CHECK", version=1),
            secondary_playbooks=[],
            reassessment_due=now_ts
        )
""",

    # ---------------- 7. API ROUTES WITH OSDR & ARES ENDPOINTS ----------------
    "backend/app/api/routes.py": """import json
from pathlib import Path
from fastapi import APIRouter
from typing import Dict, Any
from app.sources.synthetic import SyntheticSource, SCENARIO_SEEDS
from app.sources.ares_adapter import ARES_CAMPAIGN_PROFILES
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

OSDR_PATH = Path(__file__).resolve().parents[2] / "config" / "osdr_studies.json"
OSDR_CATALOG = json.loads(OSDR_PATH.read_text(encoding="utf-8"))

CURRENT_STATE = {
    "scenario": "normal",
    "seed": 42,
    "ares_subject": "Subject_1",
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
        "seed": CURRENT_STATE["seed"],
        "ares_subject": CURRENT_STATE["ares_subject"],
        "ares_profiles": ARES_CAMPAIGN_PROFILES,
        "osdr_catalog": OSDR_CATALOG,
        "active_event": evt,
        "playbook": pb,
        "observations": obs_list[-72:],
        "playbooks_all": list(alerts.playbooks.values()),
        "checkins": CURRENT_STATE["checkins"]
    }

@router.post("/scenario/{scenario_name}")
def inject_scenario(scenario_name: str, missing_sensor: str = "", noisy: bool = False, unmapped_unit: bool = False):
    CURRENT_STATE["scenario"] = scenario_name
    CURRENT_STATE["seed"] = SCENARIO_SEEDS.get(scenario_name, 42)
    faults: Dict[str, Any] = {}
    if missing_sensor:
        faults["missing_metric"] = missing_sensor
        faults["missing_day"] = 10
    if noisy:
        faults["noisy_day"] = 10
        faults["noisy_metric"] = "heart_rate_resting"
    if unmapped_unit:
        faults["unmapped_unit_metric"] = "radiation_dose"
        faults["unmapped_day"] = 10
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

    # ---------------- 8. V3 FRONTEND WITH NASA OSDR & ARES TRACEABILITY ----------------
    "frontend/index.html": """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>ORBIT Health v3 (NASA OSDR & Ares Grounded)</title>
  <link rel="stylesheet" href="/src/styles.css" />
  <script src="https://unpkg.com/react@18/umd/react.production.min.js" crossorigin></script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js" crossorigin></script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
  <div id="root"></div>

  <script type="text/babel">
    const { useState, useEffect, useRef } = React;
    const API_BASE = '/api';

    const STATE_ICONS = {
      GREEN: '● [OK - NOMINAL]',
      AMBER: '▲ [WATCH]',
      ORANGE: '◆ [WARNING]',
      RED: '■ [CRITICAL OVERRIDE]',
      GRAY: '◌ [INSUFFICIENT / QUARANTINED DATA]'
    };

    const REGION_INFO = {
      head: {
        label: 'Head & Eyes (OSD-816 SANS & OSD-939 / Ares Vigilance)',
        studies: ['OSD-816', 'OSD-939', 'BRSMPT-ARES-C1'],
        playbooks: ['PB-SANS', 'PB-BEH-SLEEP', 'PB-RAD'],
        metrics: ['sustained_attention_task', 'sleep_duration', 'fatigue_self_report']
      },
      chest: {
        label: 'Heart, Chest & Cardiovascular',
        studies: ['OSD-684'],
        playbooks: ['PB-MSK'],
        metrics: ['heart_rate_resting', 'spo2']
      },
      abdomen: {
        label: 'Abdomen, GI/Immune & Metabolic (OSD-1010 & OSD-684)',
        studies: ['OSD-1010', 'OSD-684'],
        playbooks: ['PB-GI-IMMUNE', 'PB-MET', 'PB-RAD'],
        metrics: ['glucose']
      },
      limbs: {
        label: 'Legs, Bones & Skeletal Muscle (OSD-684 Myobundle Context)',
        studies: ['OSD-684'],
        playbooks: ['PB-MSK'],
        metrics: ['exercise_performance_index', 'exercise_completion']
      },
      cabin: {
        label: 'Whole-Body Radiation & Cabin Habitat (OSD-1010, OSD-939, OSD-816)',
        studies: ['OSD-1010', 'OSD-939', 'OSD-816'],
        playbooks: ['PB-RAD', 'PB-ENV', 'PB-BEH-SLEEP'],
        metrics: ['radiation_dose', 'co2']
      }
    };

    function TrendChart({ labels, values, label }) {
      const canvasRef = useRef(null);
      const chartRef = useRef(null);

      useEffect(() => {
        if (!canvasRef.current) return;
        if (chartRef.current) chartRef.current.destroy();

        chartRef.current = new Chart(canvasRef.current, {
          type: 'line',
          data: {
            labels: labels,
            datasets: [{
              label: label,
              data: values,
              borderColor: '#38bdf8',
              backgroundColor: 'rgba(56, 189, 248, 0.2)',
              tension: 0.25,
              pointRadius: 5,
              fill: true
            }]
          },
          options: {
            responsive: true,
            plugins: { legend: { labels: { color: '#f8fafc' } } },
            scales: {
              x: { ticks: { color: '#cbd5e1' }, grid: { color: '#1e293b' } },
              y: { ticks: { color: '#cbd5e1' }, grid: { color: '#1e293b' } }
            }
          }
        });

        return () => { if (chartRef.current) chartRef.current.destroy(); };
      }, [labels.join(','), values.join(','), label]);

      return <canvas ref={canvasRef} height="115"></canvas>;
    }

    function App() {
      const [data, setData] = useState(null);
      const [selectedRegion, setSelectedRegion] = useState('limbs');
      const [selectedMetric, setSelectedMetric] = useState('exercise_performance_index');
      const [showEvidence, setShowEvidence] = useState(true);
      const [streak, setStreak] = useState(6);

      const fetchState = async () => {
        try {
          const res = await fetch(`${API_BASE}/state`);
          setData(await res.json());
        } catch (e) {
          console.error(e);
        }
      };

      useEffect(() => { fetchState(); }, []);

      const triggerScenario = async (name, missing = '', noisy = false, unmapped = false) => {
        const q = new URLSearchParams({
          missing_sensor: missing,
          noisy: String(noisy),
          unmapped_unit: String(unmapped)
        }).toString();
        const res = await fetch(`${API_BASE}/scenario/${name}?${q}`, { method: 'POST' });
        setData(await res.json());
        if (name === 'scenario_a') { setSelectedRegion('limbs'); setSelectedMetric('exercise_performance_index'); }
        if (name === 'scenario_b') { setSelectedRegion('head'); setSelectedMetric('sustained_attention_task'); }
        if (name === 'scenario_c') { setSelectedRegion('cabin'); setSelectedMetric('co2'); }
      };

      const toggleComms = async () => {
        const nextMode = data.online ? 'offline' : 'online';
        await fetch(`${API_BASE}/comms/${nextMode}`, { method: 'POST' });
        fetchState();
      };

      if (!data) return <div className="app-container"><div className="card"><h2>Loading ORBIT Health v3 (NASA OSDR Grounded)...</h2></div></div>;

      const evt = data.active_event;
      const pb = data.playbook;
      const metricObs = data.observations.filter((o) => o.metric === selectedMetric && o.quality === 'good');

      const fillRegion = (r) => {
        if (evt.state === 'GRAY') return '#64748b';
        if (evt.state === 'RED' && (r === 'cabin' || r === 'head' || r === 'abdomen')) return '#ef4444';
        if (evt.state === 'ORANGE' && (r === 'limbs' || r === 'abdomen' || r === 'head')) return '#f97316';
        return '#10b981';
      };

      return (
        <div className="app-container">
          <div className="top-bar">
            <div className="top-bar-title">
              ORBIT HEALTH v3 (NASA OSDR & ARES GROUNDED) | SEED: {data.seed}
            </div>
            <div className="top-bar-status">
              <span className={`badge ${data.online ? 'badge-online' : 'badge-offline'}`}>
                LINK: {data.online ? 'ONLINE (SYNCHRONIZED)' : 'OFFLINE (LOCAL AUTONOMY)'}
              </span>
              <span className="badge badge-outbox">
                OUTBOX QUEUE: {data.outbox_count} | DELIVERED: {data.delivered_count}
              </span>
            </div>
          </div>

          <div className="judge-panel">
            <div style={{ marginBottom: '8px', fontWeight: 'bold', color: '#c7d2fe' }}>
              JUDGE CONTROL PANEL — SECTION 12.4 SEEDED SCENARIOS (ALL NUMERIC VALUES ARE ILLUSTRATIVE DEMO VALUES)
            </div>
            <button className="btn btn-primary" onClick={() => triggerScenario('normal')}>
              Nominal (Seed 42 - GREEN)
            </button>
            <button className="btn btn-warning" onClick={() => triggerScenario('scenario_a')}>
              Scenario A (Seed 4101): Muscle/Metabolic/Fatigue Drift [OSD-684 -> ORANGE]
            </button>
            <button className="btn btn-danger" onClick={() => triggerScenario('scenario_b')}>
              Scenario B (Seed 939): Radiation + Vigilance Drop [OSD-939 & OSD-1010 -> RED]
            </button>
            <button className="btn btn-danger" onClick={() => triggerScenario('scenario_c')}>
              Scenario C (Seed 816): Cabin CO2 + SANS Visual + Offline [OSD-816 -> RED]
            </button>
            <button className="btn" onClick={() => triggerScenario('normal', 'visual_change', false, false)}>
              Kill Visual Input (GRAY State)
            </button>
            <button className="btn" onClick={() => triggerScenario('normal', '', false, true)}>
              Inject 'source_unit_required' Sentinel (Quarantine -> GRAY)
            </button>
            <button className="btn" onClick={toggleComms}>
              Toggle Earth Link ({data.online ? 'Go Offline' : 'Reconnect & Flush Outbox'})
            </button>
          </div>

          <div className="main-grid">
            <div className="col-left">
              <div className="card" style={{ textAlign: 'center' }}>
                <h2>Section 12.5 2D Body Map & OSDR Index</h2>
                <svg width="210" height="310" viewBox="0 0 210 310">
                  <rect x="8" y="8" width="194" height="294" rx="12" fill="none" stroke={fillRegion('cabin')} strokeWidth="4" strokeDasharray="6,4" className="body-region" onClick={() => { setSelectedRegion('cabin'); setSelectedMetric('radiation_dose'); }} />
                  <text x="105" y="25" fill="#cbd5e1" fontSize="9.5" textAnchor="middle">WHOLE-BODY (OSD-1010 / OSD-939)</text>

                  <circle cx="105" cy="62" r="22" fill={fillRegion('head')} className="body-region" onClick={() => { setSelectedRegion('head'); setSelectedMetric('sustained_attention_task'); }} />
                  <text x="105" y="66" fill="#0f172a" fontSize="9" fontWeight="bold" textAnchor="middle">HEAD/EYES</text>

                  <rect x="72" y="92" width="66" height="60" rx="8" fill={fillRegion('chest')} className="body-region" onClick={() => { setSelectedRegion('chest'); setSelectedMetric('heart_rate_resting'); }} />
                  <text x="105" y="125" fill="#0f172a" fontSize="9.5" fontWeight="bold" textAnchor="middle">HEART/CHEST</text>

                  <rect x="76" y="158" width="58" height="44" rx="6" fill={fillRegion('abdomen')} className="body-region" onClick={() => { setSelectedRegion('abdomen'); setSelectedMetric('glucose'); }} />
                  <text x="105" y="184" fill="#0f172a" fontSize="9" fontWeight="bold" textAnchor="middle">ABDOMEN (GI)</text>

                  <rect x="42" y="95" width="24" height="85" rx="6" fill={fillRegion('limbs')} className="body-region" onClick={() => { setSelectedRegion('limbs'); setSelectedMetric('exercise_performance_index'); }} />
                  <rect x="144" y="95" width="24" height="85" rx="6" fill={fillRegion('limbs')} className="body-region" onClick={() => { setSelectedRegion('limbs'); setSelectedMetric('exercise_performance_index'); }} />
                  <rect x="76" y="208" width="25" height="80" rx="6" fill={fillRegion('limbs')} className="body-region" onClick={() => { setSelectedRegion('limbs'); setSelectedMetric('exercise_performance_index'); }} />
                  <rect x="109" y="208" width="25" height="80" rx="6" fill={fillRegion('limbs')} className="body-region" onClick={() => { setSelectedRegion('limbs'); setSelectedMetric('exercise_performance_index'); }} />
                </svg>

                <div style={{ marginTop: '8px', padding: '10px', background: '#1e293b', borderRadius: '6px', textAlign: 'left', fontSize: '0.84rem' }}>
                  <div><strong>Region:</strong> {REGION_INFO[selectedRegion].label}</div>
                  <div><strong>OSDR Grounding:</strong> {REGION_INFO[selectedRegion].studies.join(', ')}</div>
                  <div><strong>Linked Playbooks:</strong> {REGION_INFO[selectedRegion].playbooks.join(', ')}</div>
                </div>
              </div>
            </div>

            <div className="col-center">
              <div className={`alert-banner state-${evt.state}`}>
                <h3 style={{ marginBottom: '8px' }}>
                  {STATE_ICONS[evt.state]} — STATE: {evt.state} ({evt.domain.toUpperCase()})
                </h3>
                <p style={{ marginBottom: '8px' }}><strong>1. NEXT ACTION:</strong> {evt.explanation.next_action}</p>
                <p style={{ marginBottom: '8px' }}><strong>2. WHAT CHANGED:</strong> {evt.explanation.what_changed}</p>
                <p style={{ marginBottom: '8px' }}><strong>3. WHY IT MATTERS (OSDR MECHANISM & LIMITATIONS):</strong> {evt.explanation.why_it_matters}</p>

                {pb && (
                  <div className="playbook-box">
                    <div>
                      <strong>Primary Playbook:</strong> {pb.id} v{pb.version} ({pb.approval_status})
                      {evt.secondary_playbooks.length > 0 && ` | Linked: ${evt.secondary_playbooks.join(', ')}`}
                    </div>
                    <div><strong>Initial Step:</strong> {pb.initial_action}</div>
                    <div><strong>Responsible Authority:</strong> {pb.responsible_authority}</div>
                  </div>
                )}

                <div style={{ marginTop: '10px', fontSize: '0.84rem' }}>
                  <span><strong>Tx:</strong> {evt.tx_status} | <strong>Delivery:</strong> {evt.delivery_status} | <strong>Ack:</strong> {evt.ack_status}</span>
                  <button className="btn" style={{ marginLeft: '10px', padding: '4px 8px', fontSize: '0.76rem' }} onClick={() => setShowEvidence(!showEvidence)}>
                    {showEvidence ? 'Hide OSDR Provenance' : 'Show OSDR Provenance & Quality'}
                  </button>
                </div>

                {showEvidence && (
                  <div className="playbook-box" style={{ fontSize: '0.8rem' }}>
                    <div><strong>OSDR Studies Cited:</strong> {evt.osdr_studies_cited.join(', ')}</div>
                    <div><strong>Rules Triggered:</strong> {evt.rules_triggered.join(', ') || 'Nominal'}</div>
                    <div><strong>Mapping Status:</strong> {evt.data_quality.mapping_status} | <strong>Confidence:</strong> {evt.data_quality.confidence}</div>
                  </div>
                )}
              </div>

              <div className="card">
                <h2>Trend vs. Personal Baseline: {selectedMetric}</h2>
                <div style={{ marginBottom: '8px' }}>
                  {[
                    'exercise_performance_index', 'sustained_attention_task', 'sleep_duration',
                    'fatigue_self_report', 'heart_rate_resting', 'glucose', 'radiation_dose', 'co2'
                  ].map((m) => (
                    <button key={m} className="btn" style={{ padding: '4px 8px', fontSize: '0.74rem' }} onClick={() => setSelectedMetric(m)}>
                      {m}
                    </button>
                  ))}
                </div>
                <TrendChart
                  labels={metricObs.map((o) => `Day ${o.context?.mission_day || 1}`)}
                  values={metricObs.map((o) => o.value)}
                  label={`${selectedMetric} (${metricObs[0]?.unit || ''}) [ILLUSTRATIVE DEMO VALUE]`}
                />
              </div>
            </div>

            <div className="col-right">
              <div className="card">
                <h2>NASA OSDR & BRSMPT Ares Catalog</h2>
                <div style={{ fontSize: '0.8rem' }}>
                  <p style={{ marginBottom: '6px' }}><strong>OSD-1010 (fixes OSD-1018):</strong> Human gut-on-chip heavy-ion RNA-seq (PB-RAD, PB-GI-IMMUNE).</p>
                  <p style={{ marginBottom: '6px' }}><strong>OSD-684:</strong> Human skeletal muscle myobundle RNA-seq (PB-MSK, PB-MET).</p>
                  <p style={{ marginBottom: '6px' }}><strong>OSD-816:</strong> Ex vivo human ocular ICP:IOP SANS model (PB-SANS).</p>
                  <p style={{ marginBottom: '6px' }}><strong>OSD-939:</strong> Proton radiation rPVT sustained attention (PB-BEH-SLEEP).</p>
                  <p><strong>BRSMPT Ares Campaign 1:</strong> Subjects 1-3 SRT, Running Memory & mRTC mapped to <code>sustained_attention_task</code>.</p>
                </div>
              </div>

              <div className="card">
                <h2>Voluntary Check-In & Adherence ({streak}d Streak)</h2>
                <div className="input-group">
                  <label>Fatigue Self-Report (1-5)</label>
                  <select><option>1 - Well Rested</option><option>3 - Moderate Fatigue</option><option>4 - High Fatigue</option></select>
                </div>
                <div className="input-group">
                  <label>GI / Visual Symptoms (Neutral Reporting)</label>
                  <select>
                    <option>None</option>
                    <option>GI Discomfort (OSD-1010 Context)</option>
                    <option>Visual Focus Shift (OSD-816 SANS Pathway)</option>
                  </select>
                </div>
                <button className="btn btn-primary" style={{ width: '100%' }} onClick={() => setStreak(streak + 1)}>
                  Log Local Check-In (+1 Adherence Streak)
                </button>
              </div>
            </div>
          </div>
        </div>
      );
    }

    ReactDOM.createRoot(document.getElementById('root')).render(<App />);
  </script>
</body>
</html>
""",

    # ---------------- 9. V3 TESTS ----------------
    "backend/tests/test_v3_nasa_grounded.py": """from app.sources.synthetic import SyntheticSource
from app.sources.ares_adapter import AresCampaignAdapter
from app.baseline.baseline_service import PersonalBaselineService
from app.risk.engine import RiskEngine

def test_scenario_a_seed_4101_osd684_orange():
    src = SyntheticSource(scenario="scenario_a", days=10)
    assert src.seed == 4101
    evt = RiskEngine(PersonalBaselineService()).evaluate(list(src.stream()))
    assert evt.state == "ORANGE"
    assert "OSD-684" in evt.osdr_studies_cited
    assert evt.playbook.id == "PB-MSK"
    assert "ILLUSTRATIVE DEMO VALUE" in evt.explanation.what_changed

def test_scenario_b_seed_939_osd939_and_osd1010_red():
    src = SyntheticSource(scenario="scenario_b", days=5)
    assert src.seed == 939
    evt = RiskEngine(PersonalBaselineService()).evaluate(list(src.stream()))
    assert evt.state == "RED"
    assert "OSD-939" in evt.osdr_studies_cited
    assert "OSD-1010" in evt.osdr_studies_cited
    assert evt.playbook.id == "PB-RAD"

def test_scenario_c_seed_816_osd816_and_missing_visual_gray():
    src = SyntheticSource(scenario="scenario_c", days=5)
    assert src.seed == 816
    evt = RiskEngine(PersonalBaselineService()).evaluate(list(src.stream()))
    assert evt.state == "RED"
    assert "OSD-816" in evt.osdr_studies_cited

    # Fault: missing visual input -> GRAY, never GREEN
    src_gray = SyntheticSource(scenario="normal", days=5, faults={"missing_metric": "visual_change", "missing_day": 5})
    evt_gray = RiskEngine(PersonalBaselineService()).evaluate(list(src_gray.stream()))
    assert evt_gray.state == "GRAY"

def test_source_unit_required_sentinel_quarantined_to_gray():
    src = SyntheticSource(scenario="normal", days=5, faults={"unmapped_unit_metric": "radiation_dose", "unmapped_day": 5})
    evt = RiskEngine(PersonalBaselineService()).evaluate(list(src.stream()))
    assert evt.state == "GRAY"
    assert evt.data_quality.mapping_status == "quarantined_to_gray"

def test_ares_campaign_adapter_streams_sustained_attention():
    adapter = AresCampaignAdapter(subject_id="Subject_1", days=5, radiation_lag=True)
    obs = list(adapter.stream())
    assert len(obs) == 5
    assert obs[-1].metric == "sustained_attention_task"
    assert obs[-1].unit == "task_score"
"""
}

for filepath, content in files.items():
    p = Path(filepath)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")

print("ORBIT Health upgraded to v3 (NASA OSDR + BRSMPT Ares Grounded) successfully!")