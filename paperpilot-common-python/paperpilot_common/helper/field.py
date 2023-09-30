import datetime
from dataclasses import MISSING
from decimal import Decimal
from typing import Any, Optional

from google.protobuf.message import Message  # type: ignore
from google.protobuf.pyext._message import RepeatedCompositeContainer, RepeatedScalarContainer  # type: ignore
from google.protobuf.timestamp_pb2 import Timestamp  # type: ignore


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


def repeat_to_list(repeat: RepeatedScalarContainer) -> list:
    """replace proto.repeat to python list"""
    return list(repeat)


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


def proto_load(obj: Any) -> Any:
    """python obj to proto obj"""
    if isinstance(obj, list):
        return [proto_load(i) for i in obj]
    elif isinstance(obj, dict):
        return {key: proto_load(value) for key, value in obj.items()}
    elif isinstance(obj, datetime.datetime):
        return datetime_to_timestamp(obj)
    elif isinstance(obj, datetime.date):
        return date_to_timestamp(obj)
    elif isinstance(obj, Decimal):
        if "." in str(obj):
            return str(obj)
        else:
            return int(obj)
    else:
        return obj


def proto_dump(obj: Any, default: Any = MISSING) -> Any:
    """proto obj to python obj"""
    if isinstance(obj, RepeatedCompositeContainer):
        return [proto_dump(i, default) for i in obj]
    # Timestamp is Message's instance
    elif isinstance(obj, Timestamp):
        return timestamp_to_datetime(obj, default=default)
    elif isinstance(obj, Message):
        return {item.name: proto_dump(getattr(obj, item.name), default) for item in obj.DESCRIPTOR.fields}
    else:
        return obj
