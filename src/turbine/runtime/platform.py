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
            pipelineName=None,
            pipelineId=3806
        )

        async with self.session as ctx:
            client = meroxa.Client(ctx)
            connector = await client.connectors.create(connectorInput)

        resp = json.loads(connector)
        return Records(records=[], stream=resp['streams']['output'])

    async def write(records: Records, collection: str) -> None:
        pass

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
        return PlatformResource(PlatformResponse(resource), self._clientOpts, self._appConfig)

    async def process(self,
                      records: Records,
                      fn: t.Callable[[t.List[Record]], t.List[Record]],
                      envVars: dict) -> Records:

        # Create function parameters

        # Deploy function and let the robots do some work

        # Return results from the robot
        # Note: the resonse _may_ need some extra processing. Not sure
        #       what it will look like at this point 
        

        # Need to package this response in some sort of reasonable way
        pass 