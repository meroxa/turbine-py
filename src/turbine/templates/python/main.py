import hashlib
import sys
import typing as t
import json

from turbine.runtime import Record, Runtime


def anonymize(records: t.List[Record]) -> t.List[Record]:
    updated = []
    for record in records:
        try:
            record_value_from_json = json.loads(record.value)
            hashed_email = hashlib.sha256(
                record_value_from_json["payload"]["customer_email"].encode("utf-8")
            ).hexdigest()
            record_value_from_json["payload"]["customer_email"] = hashed_email
            updated.append(
                Record(
                    key=record.key,
                    value=record_value_from_json,
                    timestamp=record.timestamp,
                )
            )
        except Exception as e:
            print("Error occurred while parsing records: " + str(e))
            updated.append(
                Record(
                    key=record.key,
                    value=record_value_from_json,
                    timestamp=record.timestamp,
                )
            )
    return updated


class App:
    @staticmethod
    async def run(turbine: Runtime):
        try:
            # To configure your data stores as resources on the Meroxa Platform
            # use the Meroxa Dashboard, CLI, or Meroxa Terraform Provider.
            # For more details refer to: https://docs.meroxa.com/

            # Identify an upstream data store for your data app
            # with the `Resources` function.
            # Replace `source_name` with the resource name the
            # data store was configured with on Meroxa.
            source = await turbine.resources("source_name")

            # Specify which upstream records to pull
            # with the `Records` function.
            # Replace `collection_name` with a table, collection,
            # or bucket name in your data store.
            records = await source.records("collection_name")

            # Specify which secrets in environment variables should be passed
            # into the Process.
            secrets = turbine.register_secrets(name="PWD")

            # Specify what code to execute against upstream records
            # with the `Process` function.
            # Replace `Anonymize` with the name of your function code.
            anonymized = await turbine.process(records, anonymize, secrets)

            # Identify a downstream data store for your data app
            # with the `Resources` function.
            # Replace `destination_name` with the resource name the
            # data store was configured with on Meroxa.
            destination_db = await turbine.resources("destination_name")

            # Specify where to write records downstream
            # using the `Write` function
            # Replace `collection_archive` with a table, collection,
            # or bucket name in your data store
            await destination_db.write(anonymized, "collection_archive")
        except Exception as e:
            print(e, file=sys.stderr)
