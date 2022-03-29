import asyncio
import hashlib

from turbine import Turbine
from turbine.runtime import Record, Records


def anonymize(records: Records) -> Records:
    updated = []
    for record in records:
        valueToUpdate = record.value
        hashedEmail = hashlib.sha256(
            valueToUpdate['payload']['after']['email'].encode()).hexdigest()
        valueToUpdate['payload']['after']['email'] = hashedEmail
        updated.append(
            Record(
                key=record.key,
                value=valueToUpdate,
                timestamp=record.timestamp
            )
        )
    return Records(records=updated, stream="")


class App:

    async def run(turbine: Turbine):

        async def run_process(turbine: Turbine):
            # Get remote resource
            source = await turbine.resources("source_name")

            # Read from remote resource
            records = await source.records("collection_name")

            # Deploy function with source as input
            anonymized = await turbine.process(records, anonymize)

            # Get destination
            destinationDb = await turbine.resources("destination_name")

            # Write results out
            await destinationDb.write(anonymized, "collection_name")

        asyncio.run(run_process(turbine))


async def main():
    return await App.run(Turbine('local', '.'))

if __name__ == "__main__":
    asyncio.run(main())