import json
import typing as t

import meroxa

from meroxa import Meroxa

from .types import AppConfig
from .types import Record
from .types import Records
from .types import Resource
from .types import Runtime


class PlatformResponse(object):
    def __init__(self, resp: str):
        self.__dict__ = json.loads(resp)


class PlatformResource(Resource):
    def __init__(self, resource, clientOptions: meroxa.ClientOptions,
                 appConfig: AppConfig) -> None:
        self.resource = resource
        self.appConfig = appConfig
        self.clientOpts = clientOptions

    async def records(self, collection: str) -> Records:
        # Postgres initial funtimes
        connectorConfig = dict(input="public.{}".format(collection))
        connectorInput = meroxa.CreateConnectorParams(
            name="source",
            metadata={
                "mx:connectorType": "source",
            },
            config=connectorConfig,
            resourceId=self.resource.id,
            pipelineName=self.appConfig.name,
            pipelineId=None
        )

        async with Meroxa(auth=self.clientOpts.auth) as m:
            # Error Handling: Duplicate connector
            # Check for `bad_request`
            connector = await m.connectors.create(connectorInput)

        print(connector)
        resp = json.loads(connector)
        return Records(records=[], stream=resp['streams']['output'])

    async def write(self, records: Records, collection: str) -> None:

        # Connector config
        # Move the non-shared logics to a separate function
        connectorConfig = {
            input: records.stream,
            #=== ^ shared ^ =====  V S3 specific V ==#
            "aws_s3_prefix": '{}'.format(str.lower(collection)),
            "value.converter": "org.apache.kafka.connect.json.JsonConverter",
            "value.converter.schemas.enable": "true",
            "format.output.type": "jsonl",
            "format.output.envelope": "true"
        }

        connectorInput = meroxa.CreateConnectorParams(
            name="source",
            metadata={
                "mx:connectorType": "source",
            },
            config=connectorConfig,
            resourceId=self.resource.id,
            pipelineName=self.appConfig.name,
            pipelineId=None
        )

        async with Meroxa(auth=self.clientOpts.auth) as m:
            connector = await m.connectors.create(connectorInput)

        resp = json.loads(connector)
        return Records(records=[], stream=resp['streams']['output'])


class PlatformRuntime(Runtime):

    _registeredFunctions = None

    def __init__(self, clientOptions: meroxa.ClientOptions,
                 imageName: str, config: AppConfig) -> None:
        self._imageName = imageName
        self._appConfig = config
        self._clientOpts = clientOptions

    async def resources(self, resourceName: str):

        # Error checking if a resource does not exist.
        # Response is simple string. We could massage that into a structured item
        # e.g. (Option[resp], Option[error])
        async with Meroxa(auth=self._clientOpts.auth) as m:
            resource = await m.resources.get(resourceName)

        return PlatformResource(
            PlatformResponse(resource),
            self._clientOpts,
            self._appConfig)

    async def process(self,
                      records: Records,
                      fn: t.Callable[[t.List[Record]], t.List[Record]],
                      envVars: dict) -> Records:

        # Create function parameters
        createFuncParams = meroxa.CreateFunctionParams(
            inputStream=records.stream,
            command=["python"],
            args=["main.py", fn.__name__],
            image=self._imageName,
            pipelineIdentifiers={
                "name": self._appConfig.name
            },
            envVars=envVars
        )

        async with Meroxa(auth=self._clientOpts.auth) as m:
            createdFunction = await m.functions.create(createFuncParams)

        records.stream = json.loads(createdFunction)['output_stream']

        return records
