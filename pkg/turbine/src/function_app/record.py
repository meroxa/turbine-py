import json
from collections import UserList
import logging
# KTLO: https://github.com/meroxa/turbine-py/issues/151
from ..turbine_app import Record, RecordList
def proto_records_to_turbine_records(p_record: list[Record]):
    return [
        Record(
            key=record.key,
            value=decode_record(record),
            timestamp=record.timestamp,
        )
        for record in p_record
    ]


def turbine_records_to_proto_records(t_record: list[Record]):
    return [
        Record(
            key=record.key,
            value=encode_record(record),
            timestamp=record.timestamp,
        )
        for record in t_record
    ]


def decode_record(record: Record):
    try:
        return json.loads(record.value)
    except json.decoder.JSONDecodeError:
        return record.value


def encode_record(record: Record):
    try:
        return json.dumps(record.value)
    except json.decoder.JSONDecodeError:
        return record.value
