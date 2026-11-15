import pytest
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
