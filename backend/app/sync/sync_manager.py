from typing import List, Dict
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
