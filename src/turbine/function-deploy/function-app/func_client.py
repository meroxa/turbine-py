import asyncio
import json
import uuid

import grpc.aio

import service_pb2
import service_pb2_grpc


async def run() -> None:
    records = [
        service_pb2.Record(
            key=str(uuid.uuid4()),
            value=json.dumps(dict(test="value")),
            timestamp=1649445639,
        )
    ]

    async with grpc.aio.insecure_channel("localhost:5005") as channel:
        stub = service_pb2_grpc.FunctionStub(channel)
        resp = await stub.Process(service_pb2.ProcessRecordRequest(records=records))

        print(len(resp.records))


if __name__ == "__main__":
    asyncio.run(run())
