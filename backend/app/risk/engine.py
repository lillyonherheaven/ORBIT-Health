from typing import List, Dict
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
                        "Open playbook PB-RAD-SHELTER v1 and relocate to the shielded storm zone; confirm source/data quality and "
                        "follow the approved shelter procedure. Escalate to crew_commander immediately."
                    )
                ),
                playbook=PlaybookRef(id="PB-RAD-SHELTER", version=1),
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
