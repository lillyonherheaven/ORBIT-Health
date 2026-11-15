from typing import Protocol, Iterator, List, runtime_checkable
from pydantic import BaseModel
from app.contracts.observation import Observation

class SourceInfo(BaseModel):
    name: str
    metrics: List[str]
    units: dict
    cadence: str

@runtime_checkable
class DataSource(Protocol):
    def stream(self) -> Iterator[Observation]:
        ...
    def describe(self) -> SourceInfo:
        ...
