from email.mime import image
from http import client
from importlib.metadata import metadata
import json
from re import L
import time
import typing as t
from wsgiref.types import InputStream


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


class LocalResource(Resource):
    name = ""
    fixturesPath = ""

    def __init__(self, name: str, fixturesPath: str) -> None:
        self.name = name
        self.fixturesPath = fixturesPath

    def records(self, collection: str) -> Records:
        return Records(
            records=readFixtures(self.fixturesPath, collection, self.name),
            stream=""
        )

    def write(self, rr: Records, collection: str) -> None:
        pprint(
            "=====================to {} resource=====================".format(
                self.name))

        for record in rr.records:
            pprint(record)

        return None




#  resource: ResourceResponse;
#   client: Client;
#   appConfig: AppConfig;

#   constructor(
#     resource: ResourceResponse,
#     client: Client,
#     appConfig: AppConfig
#   ) {
#     this.resource = resource;
#     this.client = client;
#     this.appConfig = appConfig;
#   }

class PlatformResource(Resource):
    def __init__(self, resource, client: meroxa.Client, appConfig: AppConfig) -> None:
        self.resource = resource
        self.client = client
        self.appConfig = appConfig

    async def records(self, collection: str) -> Records:

        # Add logging message here: Creating log source connector from...


        # Postgres initial funtimes
        connectorConfig = dict( input = "public.{}".format(collection))
        connectorInput = meroxa.CreateConnectorParams(
            name =  "source",
            config = connectorConfig,
            metadata= {
                "mx:connectorType": "source",
            },
            resourceId = self.resource.id,
            pipelineName = self.appConfig.name,
            pipelineId = None
        )

        connector = await self.client.connectors.create(connectorInput)
        return super().records()

    async def write(records: Records, collection: str) -> None:
        pass
        

class PlatformRuntime(Runtime):

    _registeredFunctions = None

    def __init__(self, client: meroxa.Client, imageName: str, config: AppConfig) -> None:
        self._client = client
        self._imageName = imageName
        self._appConfig = config

    async def resources(self, resourceName: str):
        resource = await self._client.resources.get(resourceName)
        return PlatformResource(resource, self._client, self._appConfig)

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
