## Functions App
This application serves as an interface between `turbine-py` and `funtime`, the Meroxa Functions Runtime.

### Requirements
```pycon
grpcio             1.44.0
grpcio-tools       1.44.0
```

### Testing the gRPC Client
#### Local Testing
This application is an implementation of an RPC contract. Given that, we are not only able to define the end that listens, but also the side that publishes.

The following code is an example client that uses `grpc.io` and the generated code to transmit values to the server.

##### Prereqs
- A turbine data app copied into `../data_app`
- The below client example colocated with `/protos`
- A fixtures file

An example client:
```python
import asyncio
import json
import time

import grpc.aio

# Generated service code
import service_pb2
import service_pb2_grpc

FIXTURES_FILE = ""
COLLECTION_NAME = ""

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
                            key=str(rec["key"]),
                            value=json.dumps(rec["value"]),
                            timestamp=int(time.time()),
                        )
                    )
    except FileNotFoundError:
        print(
            f"{path} not found: must specify fixtures path to data for source"
            f" resources in order to run locally"
        )

    return fixtures


async def run() -> None:

    records = await read_fixtures(FIXTURES_FILE, COLLECTION_NAME)
    print(records)

    async with grpc.aio.insecure_channel("localhost:5005") as channel:
        stub = service_pb2_grpc.FunctionStub(channel)
        resp = await stub.Process(service_pb2.ProcessRecordRequest(records=records))

        print(len(resp.records))


if __name__ == "__main__":
    asyncio.run(run())

```


### Troubleshooting

#### Apple Silicon (M1) issues
```mach-o file, but is an incompatible architecture (have 'x86_64', need 'arm64e'))```

As of April 8, 2022 the default wheel for grpcio and grpcio-tools is not working on M1 processors. In order to use these tools you may have to force pip to build the wheel locally with the following commands

```bash
pip install --no-binary :all: grpcio grpcio-tools --ignore-installed
```
