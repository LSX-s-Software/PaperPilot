import datetime
from dataclasses import MISSING
from typing import Any, Optional

from google.protobuf.timestamp_pb2 import Timestamp


def timestamp_to_datetime(t: Timestamp, default: Any = MISSING) -> datetime.datetime:
    """replace proto.timestamp to python datetime.datetime"""
    if t.seconds == 0 and t.nanos == 0 and default != MISSING:
        return default
    return t.ToDatetime()


def timestamp_to_date(t: Timestamp, default: Any = MISSING) -> datetime.date:
    """replace proto.timestamp to python datetime.date"""
    if t.seconds == 0 and t.nanos == 0 and default != MISSING:
        return default
    return t.ToDatetime().date()


def datetime_to_timestamp(d: Optional[datetime.datetime]) -> Timestamp:
    """replace python datetime.datetime to proto.timestamp"""
    t: Timestamp = Timestamp()
    if d:
        t.FromDatetime(d)
    return t


def date_to_timestamp(d: Optional[datetime.date]) -> Timestamp:
    """replace python datetime.date to proto.timestamp"""
    t: Timestamp = Timestamp()
    if d:
        t.FromDatetime(datetime.datetime.combine(d, datetime.datetime.min.time()))
    return t
