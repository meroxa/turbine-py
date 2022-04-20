import hashlib
import sys
import typing as t
import json

from turbine.runtime import Record, Runtime


def anonymize(records: t.List[Record]) -> t.List[Record]:
    updated = []
    for record in records:
        record_value_from_json = json.loads(record.value)
        hashed_email = hashlib.sha256(
            record_value_from_json["payload"]["customer_email"].encode("utf-8")
        ).hexdigest()
        print(f"hashed email: {hashed_email}")
        record_value_from_json["payload"]["customer_email"] = hashed_email
        updated.append(
            Record(
                key=record.key, value=record_value_from_json, timestamp=record.timestamp
            )
        )
    return updated


class App:
    @staticmethod
    async def run(turbine: Runtime):
        try:
            # Get remote resource
            source = await turbine.resources("source_name")

            # Read from remote resource
            records = await source.records("collection_name")

            # Deploy function with source as input
            anonymized = await turbine.process(records, anonymize, {})

            # Get destination
            destination_db = await turbine.resources("destination_name")

            # Write results out
            await destination_db.write(anonymized, "collection_archive")
        except Exception as e:
            print(e, file=sys.stderr)
