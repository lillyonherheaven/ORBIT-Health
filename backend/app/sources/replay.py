from typing import Iterable, Iterator, List
from app.contracts.observation import Observation
from app.sources.base import SourceInfo

class ReplaySource:
    def __init__(self, observations: Iterable[Observation], speed: float = 1.0):
        self.observations: List[Observation] = list(observations)
        self.speed = speed

    def describe(self) -> SourceInfo:
        metrics = sorted(list({o.metric for o in self.observations}))
        return SourceInfo(name="replay_source", metrics=metrics, units={}, cadence=f"{self.speed}x")

    def stream(self) -> Iterator[Observation]:
        for obs in sorted(self.observations, key=lambda x: x.measured_at):
            yield obs
