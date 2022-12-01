import json

# KTLO: https://github.com/meroxa/turbine-py/issues/151
try:
    import service_pb2
except ModuleNotFoundError:
    from . import service_pb2

from turbine.runtime import Record


def proto_records_to_turbine_records(p_record: list[service_pb2.Record]):
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
        service_pb2.Record(
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
