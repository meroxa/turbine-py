from email.mime import image
from http import client
from importlib.metadata import metadata
import json
from re import L
import time
import typing as t

import meroxa

from pprint import pprint

from .types import AppConfig
from .types import Record, Resource
from .types import Records
from .types import Runtime


def readFixtures(path: str, collection: str, resourceName: str):

    fixtures = []

    with open(path, "r") as content:
        fc = json.load(content)
        for rec in fc[collection]:
            fixtures.append(
                Record(
                    key=rec['key'],
                    value=rec['value'],
                    timestamp=time.time()
                )
            )

    pprint("=====================from {} resource=====================".format(
        resourceName))

    [pprint(fixture) for fixture in fixtures]

    return fixtures

class PlatformResource(Resource):
    def __init__(self, resource, clientOpts, appConfig: AppConfig) -> None:

        print("entered resource")

        self.resource = resource
        self.appConfig = appConfig
        self.session = meroxa.createSession(clientOpts)

        print(self.session)

    async def records(self, collection: str) -> Records:

        # Add logging message here: Creating log source connector from...


        # Postgres initial funtimes
        connectorConfig = dict( input = "public.{}".format(collection))
        connectorInput = meroxa.CreateConnectorParams(
            name =  "source",
            metadata= {
                "mx:connectorType": "source",
            },
            resourceId = self.resource.id,
            pipelineName = None,
            pipelineId = "acb53bf7-8f2e-4058-8411-90418e7bb8a4"
        )


        print(vars(connectorInput))
        async with self.session as ctx:
            client = meroxa.Client(ctx)
            connector = await client.connectors.create(connectorInput)
            print(connector)

    async def write(records: Records, collection: str) -> None:
        pass
        

class PlatResp(object):
    def __init__(self, resp: str):
        self.__dict__ = json.loads(resp)

class PlatformRuntime(Runtime):

    _registeredFunctions = None
    _session = None

    def __init__(self, clientOptions: meroxa.ClientOptions, imageName: str, config: AppConfig) -> None:
        self._imageName = imageName
        self._appConfig = config
        self._clientOpts = clientOptions

        self._session = meroxa.createSession(clientOptions)

    async def resources(self, resourceName: str):
        async with self._session as ctx:
            client = meroxa.Client(ctx)
            resource = await client.resources.get(resourceName)

        return PlatformResource(PlatResp(resource), self._clientOpts, self._appConfig)

    async def process(self,
                records: Records,
                fn: t.Callable[[t.List[Record]], t.List[Record]],
                envVars: dict) -> Records:

        functionParams = meroxa.CreateFunctionParams(
            inputStream = records.stream,
            command = [""],
            args = ["", fn.__name__],
            image = self._imageName,
            pipelineIdentifiers = {
                "name": self._appConfig.name
            },
            envVars = envVars
        )

        # log message, deploying function

        # Need to package this response in some sort of reasonable way
        res = await self._client.functions.create(functionParams)
        records.stream = res.output_stream
        return records
