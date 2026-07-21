from datetime import time


class TimeRange:
    def __init__(self, start_time: time, end_time: time):
        if start_time >= end_time:
            raise ValueError("start_time must be before end_time")
        if not isinstance(start_time, time) or not isinstance(end_time, time):
            raise TypeError("start_time and end_time must be datetime.time objects")
        self._start = start_time
        self._end = end_time

    @property
    def start(self) -> time:
        return self._start

    @property
    def end(self) -> time:
        return self._end

    def overlaps(self, other: "TimeRange") -> bool:
        return self._start < other._end and other._start < self._end

    def duration_minutes(self) -> int:
        return int(
            (self._end.hour * 60 + self._end.minute)
            - (self._start.hour * 60 + self._start.minute)
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TimeRange):
            return NotImplemented
        return self._start == other._start and self._end == other._end

    def __str__(self) -> str:
        return f"{self._start.isoformat()}-{self._end.isoformat()}"
