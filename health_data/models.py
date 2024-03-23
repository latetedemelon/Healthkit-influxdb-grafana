"""Models for the data returned from the requests."""

from typing import Optional, List
from pydantic import BaseModel

class DataRecord(BaseModel):
    date: str
    qty: Optional[float] = None
    source: Optional[str] = None

class Metric(BaseModel):
    data: List[DataRecord]
    name: str
    units: str

class SleepAnalysisRecord(DataRecord):
    asleep: float
    awake: float
    core: float
    deep: float
    inBed: float
    rem: float

    inBedEnd: str
    inBedStart: str
    sleepEnd: str
    sleepStart: str

class SleepAnalysisMetric(Metric):
    data: List[SleepAnalysisRecord]


def metric_from_dict(data: dict) -> Metric | SleepAnalysisMetric:
    if data["name"] == "sleep_analysis":
        return SleepAnalysisMetric(**data)
    return Metric(**data)
