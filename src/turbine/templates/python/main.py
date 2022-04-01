import os
import asyncio
import hashlib

from turbine import Turbine
from turbine.runtime import Record, Records


def anonymize(records: Records) -> Records:
    updated = []
    for record in records.records:
        value_to_update = record.value
        hashed_email = hashlib.sha256(
            value_to_update['payload']['after']['email'].encode()).hexdigest()
        value_to_update['payload']['after']['email'] = hashed_email
        updated.append(
            Record(
                key=record.key,
                value=value_to_update,
                timestamp=record.timestamp
            )
        )
    return Records(records=updated, stream="")


class App:

    @staticmethod
    async def run(turbine: Turbine):
        # Get remote resource
        source = await turbine.resources("source_name")

        # Read from remote resource
        records = await source.records("collection_name")

        # Deploy function with source as input
        anonymized = await turbine.process(records, anonymize)

        # Get destination
        destination_db = await turbine.resources("destination_name")

        # Write results out
        await destination_db.write(anonymized, "collection_name")


def main():
    curr = os.path.abspath(os.path.dirname(__file__))

    asyncio.run(
        App.run(
            Turbine(
                runtime="local",
                path_to_data_app=curr
            )
        )
    )


if __name__ == "__main__":
    main()
