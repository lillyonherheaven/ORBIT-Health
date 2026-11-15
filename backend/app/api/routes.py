import json
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
