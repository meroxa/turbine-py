import sys
import typing as t

from turbine.runtime import Record

def noop(records: t.List[Record]) -> t.List[Record]:
    return records


class App:
    @staticmethod
    async def run(turbine):
        try:
            # Get remote resource
            source = await turbine.resources("my-mysql")

            # Read from remote resource
            records = await source.records("User")

            # Deploy function with source as input
            anonymized = await turbine.process(records, noop, {})

            # Get destination
            destination_db = await turbine.resources("tbp-source")

            # Write results out
            await destination_db.write(anonymized, "collection_archive")
        except Exception as e:
            print(e, file=sys.stderr)
