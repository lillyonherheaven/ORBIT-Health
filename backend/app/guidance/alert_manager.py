import json
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
        if playbook_id in self.playbooks:
            return self.playbooks[playbook_id]
        for alias in ("PB-RAD", "PB-RAD-SHELTER"):
            if playbook_id == alias:
                for candidate in ("PB-RAD", "PB-RAD-SHELTER"):
                    if candidate != alias and candidate in self.playbooks:
                        return self.playbooks[candidate]
        return None

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
