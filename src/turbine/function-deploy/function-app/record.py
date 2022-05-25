import json

from service_pb2 import Record as ProtoRecord

from turbine.runtime import Record


def proto_records_to_turbine_records(p_record: list[ProtoRecord]):
    return [
        Record(
            key=record.key, value=json.loads(record.value), timestamp=record.timestamp
        )
        for record in p_record
    ]


def turbine_records_to_proto_records(t_record: list[Record]):
    return [
        ProtoRecord(
            key=record.key, value=json.dumps(record.value), timestamp=record.timestamp
        )
        for record in t_record
    ]
