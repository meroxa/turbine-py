import json

from service_pb2 import Record as ProtoRecord

from turbine.runtime import Record


def proto_records_to_turbine_records(p_record: list[ProtoRecord]):
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
        ProtoRecord(
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
