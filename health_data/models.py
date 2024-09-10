"""Models for the data returned from the requests."""

from typing import Optional, List, Generator
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class DataRecord(BaseModel):
    date: str
    qty: Optional[float] = None
    Min: Optional[float] = None
    Max: Optional[float] = None
    Avg: Optional[float] = None
    source: Optional[str] = None

class Metric(BaseModel):
    data: List<DataRecord]
    name: str
    units: str

    def points(self) -> Generator[str, None, None]:
        """
        Generate Prometheus-compatible line protocol strings for VictoriaMetrics.
        """
        for record in self.data:
            for value_name in ["qty", "Min", "Max", "Avg"]:
                if (val := getattr(record, value_name)) is not None:
                    # Create a line in the format: metric_name{label_name="label_value", ...} value timestamp
                    line = (
                        f'{self.name}{{source="{record.source}", units="{self.units}", agg="{value_name}"}} '
                        f'{val} {self.convert_timestamp(record.date)}'
                    )
                    yield line

    @staticmethod
    def convert_timestamp(timestamp: str) -> int:
        """
        Convert timestamp string to a Unix epoch time (in nanoseconds).
        VictoriaMetrics expects time in nanoseconds.
        """
        from datetime import datetime
        dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
        return int(dt.timestamp() * 1_000_000_000)  # Convert to nanoseconds

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

    def points(self) -> Generator[str, None, None]:
        """
        Generate Prometheus-compatible line protocol strings for VictoriaMetrics.
        """
        field_names = self.fields()
        for record in self.data:
            for field in field_names["durations"]:
                line = (
                    f'{field}{{source="{record.source}", type="sleep", units="{self.units}"}} '
                    f'{getattr(record, field)} {self.convert_timestamp(record.date)}'
                )
                yield line

            # Line for in_bed time range
            yield (
                f'in_bed{{source="{record.source}", type="sleep", range="True"}} '
                f'start="{record.inBedStart}", end="{record.inBedEnd}" {self.convert_timestamp(record.date)}'
            )

            # Line for sleeping time range
            yield (
                f'sleeping{{source="{record.source}", type="sleep", range="True"}} '
                f'start="{record.sleepStart}", end="{record.sleepEnd}" {self.convert_timestamp(record.date)}'
            )

def metric_from_dict(data: dict) -> Metric | SleepAnalysisMetric:
    """
    Convert a dictionary into a Metric or SleepAnalysisMetric object.
    """
    if data["name"] == "sleep_analysis":
        return SleepAnalysisMetric(**data)
    try:
        return Metric(**data)
    except Exception as err:
        logger.error(f"Error converting dictionary to Metric: {err}")
        raise ValueError("Invalid metric data provided")
