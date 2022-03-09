import json
import typing as t

import meroxa

from .types import AppConfig
from .types import Record
from .types import Records
from .types import Resource
from .types import Runtime


class PlatformResponse(object):
    def __init__(self, resp: str):
        self.__dict__ = json.loads(resp)


class PlatformResource(Resource):
    def __init__(self, resource, clientOpts, appConfig: AppConfig) -> None:
        self.resource = resource
        self.appConfig = appConfig
        self.session = meroxa.createSession(clientOpts)

    async def records(self, session, collection: str) -> Records:

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

        # Error Handling: Duplicate connector
        # Check for `bad_request`
        connector = await meroxa.Client(session).connectors.create(connectorInput)

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

        async with self.session as ctx:
            client = meroxa.Client(ctx)
            connector = await client.connectors.create(connectorInput)

        resp = json.loads(connector)
        return Records(records=[], stream=resp['streams']['output'])


class PlatformRuntime(Runtime):

    _registeredFunctions = None
    _session = None

    def __init__(self, clientOptions: meroxa.ClientOptions, imageName: str, config: AppConfig) -> None:
        self._imageName = imageName
        self._appConfig = config
        self._clientOpts = clientOptions

        self._session = meroxa.createSession(clientOptions)

    async def resources(self, session, resourceName: str):
        # Error checking if a resource does not exist.
        # Response is simple string. We could massage that into a structured item
        # e.g. (Option[resp], Option[error])
         
        resource = await meroxa.Client(session).resources.get(resourceName)

        print(resource)
        return PlatformResource(PlatformResponse(resource), self._clientOpts, self._appConfig)

    async def process(self,
                      session,
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

        createdFunction = await meroxa.Client(session).functions.create(createFuncParams)

        print(createdFunction)

        records.stream = json.loads(createdFunction)['output_stream']

        return records
