"""Models for the data returned from the requests."""

from typing import Optional, List, Generator
from pydantic import BaseModel

from influxdb_client import Point

class DataRecord(BaseModel):
    date: str
    qty: Optional[float] = None
    source: Optional[str] = None

class Metric(BaseModel):
    data: List[DataRecord]
    name: str
    units: str

    def points(self) -> Generator[Point, None, None]:
        for record in self.data:
            yield Point.from_dict({
                "measurement": self.name,
                "fields": {"value": record.qty, "units": self.units},
                "tags": {"source": record.source},
                "time": record.date,
            })

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

    def fields(self) -> dict:
        return {
            "times": ["inBedEnd", "inBedStart", "sleepEnd", "sleepStart"],
            "durations": ["asleep", "awake", "core", "deep", "inBed", "rem"],
        }

    def points(self) -> Generator[Point, None, None]:
        field_names = self.fields()
        for record in self.data:
            for field in field_names["durations"]:
                yield Point.from_dict({
                    "measurement": field,
                    "fields": {"value": getattr(record, field), "units": self.units},
                    "tags": {"source": record.source, "type": "sleep"},
                    "time": record.date,
                })

            yield Point.from_dict({
                "measurement": "in_bed",
                "fields": {"start": record.inBedStart, "end": record.inBedEnd},
                "tags": {"source": record.source, "type": "sleep", "range": True},
                "time": record.date,
            })

            yield Point.from_dict({
                "measurement": "sleeping",
                "fields": {"start": record.sleepStart, "end": record.sleepEnd},
                "tags": {"source": record.source, "type": "sleep", "range": True},
                "time": record.date,
            })


def metric_from_dict(data: dict) -> Metric | SleepAnalysisMetric:
    if data["name"] == "sleep_analysis":
        return SleepAnalysisMetric(**data)
    try:
        return Metric(**data)
    except:
        raise ValueError("Invalid metric data provided")
