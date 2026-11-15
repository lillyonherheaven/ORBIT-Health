import pytest
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
