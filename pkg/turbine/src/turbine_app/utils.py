from .types import RecordList, Records
from . import proto_gen as pg
import json


def record_to_collection(records: Records) -> pg.Collection:
    record_list = []
    for rr in records.records:
        record_list.append(
            pg.Record(
                key=rr.key,
                value=str.encode(json.dumps(rr.value)),
                timestamp=rr.timestamp,
            )
        )
    return pg.Collection(
        name=records.name,
        stream=records.stream,
        records=record_list,
    )


def collection_to_record(collection: pg.Collection) -> Records:
    record_list = RecordList()
    for rr in collection.records:
        record_list.add_record(record=rr)
    return Records(
        records=record_list,
        stream=collection.stream,
        name=collection.name,
    )
