import sqlite3
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
