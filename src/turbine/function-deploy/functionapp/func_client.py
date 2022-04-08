import asyncio
import json
import uuid

import grpc.aio

import time
import service_pb2
import service_pb2_grpc


async def read_fixtures(path: str, collection: str):
    fixtures = []
    try:
        with open(path, "r") as content:
            fc = json.load(content)

            print(fc)
            if collection in fc:
                for rec in fc[collection]:
                    fixtures.append(
                        service_pb2.Record(
                            key=str(rec["key"]), value=json.dumps(rec["value"]), timestamp=int(time.time())
                        )
                    )
    except FileNotFoundError:
        print(
            f"{path} not found: must specify fixtures path to data for source"
            f" resources in order to run locally"
        )

    return fixtures


async def run() -> None:

    records = await read_fixtures('demo.json', "collection_name")
    print(records)

    async with grpc.aio.insecure_channel("localhost:5005") as channel:
        stub = service_pb2_grpc.FunctionStub(channel)
        resp = await stub.Process(service_pb2.ProcessRecordRequest(records=records))

        print(len(resp.records))


if __name__ == "__main__":
    asyncio.run(run())
