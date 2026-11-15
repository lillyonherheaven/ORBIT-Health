import csv
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
