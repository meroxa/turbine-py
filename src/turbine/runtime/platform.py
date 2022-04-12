import json
import sys
import typing as t

import meroxa
from meroxa import Meroxa
from meroxa.types import PipelineIdentifiers

from .types import AppConfig
from .types import Record
from .types import Records
from .types import Resource
from .types import Runtime
from .types import RegisteredFunctions

class PlatformResponse(object):
    def __init__(self, resp: str):
        self.__dict__ = json.loads(resp)


class PlatformResource(Resource):
    def __init__(
        self, resource, client_options: meroxa.ClientOptions, app_config: AppConfig
    ) -> None:
        self.resource = resource
        self.app_config = app_config
        self.client_opts = client_options

    async def records(self, collection: str) -> Records:
        print(f"Creating SOURCE connector from source: {self.resource.name}")

        # Postgres initial funtimes

        connector_config = dict(input="public.{}".format(collection))
        connector_input = meroxa.CreateConnectorParams(
            name="source",
            metadata={
                "mx:connectorType": "source",
            },
            config=connector_config,
            resourceId=self.resource.uuid,
            pipelineName=self.app_config.name,
            pipelineId=None,
        )

        async with Meroxa(auth=self.client_opts.auth) as m:
            connector: meroxa.ConnectorsResponse
            # Error Handling: Duplicate connector
            # Check for `bad_request`
            resp = await m.connectors.create(connector_input)

        if resp[0] is not None:
            return ChildProcessError("Error creating source connector from resource {} : {}".format(self.resource.name, resp[0].message))
        else:
            connector = resp[1]
            return Records(records=[], stream=connector.streams.output)

    async def write(self, records: Records, collection: str) -> None:
        print(f"Creating DESTINATION connector from stream: {records.stream}")

        # Connector config
        # Move the non-shared logics to a separate function
        connector_config = {
            "input": records.stream,
            # === ^ shared ^ =====  V S3 specific V ==#
            "aws_s3_prefix": "{}".format(str.lower(collection)),
            "value.converter": "org.apache.kafka.connect.json.JsonConverter",
            "value.converter.schemas.enable": "true",
            "format.output.type": "jsonl",
            "format.output.envelope": "true",
        }

        connector_input = meroxa.CreateConnectorParams(
            name="destination",
            metadata={
                "mx:connectorType": "destination",
            },
            config=connector_config,
            resourceId=self.resource.id,
            pipelineName=self.app_config.name,
            pipelineId=None,
        )

        async with Meroxa(auth=self.client_opts.auth) as m:
            resp = await m.connectors.create(connector_input)

        if resp[0] is not None:
            return ChildProcessError("Error creating destination connector from stream {} : {}".format(records.stream, resp[0].message))
        else:
            return None


class PlatformRuntime(Runtime):
    _registeredFunctions = {}

    def __init__(
        self, client_options: meroxa.ClientOptions, image_name: str, config: AppConfig
    ) -> None:
        self._image_name = image_name
        self._app_config = config
        self._client_opts = client_options

    async def resources(self, resource_name: str):
        # Error checking if a resource does not exist.
        # Response is simple string. We could massage that into a structured item
        # e.g. (Option[resp], Option[error])

        async with Meroxa(auth=self._client_opts.auth) as m:
            resp = await m.resources.get(resource_name)

        if resp[0] is not None:
            return  ChildProcessError("Error finding resource {} : {}".format(resource_name, resp[0].message))
        else:
            return PlatformResource(
                resource=resp[1],
                client_options=self._client_opts,
                app_config=self._app_config,
            )

    async def process(
        self,
        records: Records,
        fn: t.Callable[[t.List[Record]], t.List[Record]],
        env_vars: dict,
    ) -> Records:

        # Create function parameters
        create_func_params = meroxa.CreateFunctionParams(
            inputStream=records.stream[0],
            command=["python"],
            args=["main.py", fn.__name__],
            image=self._image_name,
            pipelineIdentifiers=PipelineIdentifiers(name=self._app_config.name),
            envVars=env_vars,
        )

        print("deploying function: {}".format(getattr(fn, "__name__", "Unknown")))

        async with Meroxa(auth=self._client_opts.auth) as m:
            resp = await m.functions.create(create_func_params)

        if resp[0] is not None:
            return ChildProcessError("Error deploying function {} : {}".format(getattr(fn, "__name__", "Unknown"), resp[0].message))
        else:
            func = resp[1]
            records.stream = func.output_stream
            return records

    async def list_functions(self):
        return print("List of application functions : \n {}".format("\n".join(self.registered_functions)))

    async def has_functions(self):
        if self._registeredFunctions:
            return True 
        return False
       


