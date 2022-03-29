import os
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

        return await run_process(turbine)

"""
Issues:
 - local is not async, platform is. Mixing is :(


Maybe solution(s):
 - make the local runtime async 
 - setting a flag that chooses b/w local or platform runtime. 
"""
async def main():

    curr = os.path.abspath(os.path.dirname(__file__))

    return await App.run(Turbine('local', curr))

if __name__ == "__main__":
    asyncio.run(main())