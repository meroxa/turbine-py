import json
import typing as t
import os
import re

import meroxa
from meroxa import Meroxa
from meroxa.pipelines import PipelineIdentifiers
from meroxa.types import ResourceType

from .types import AppConfig
from .types import Record
from .types import Records
from .types import Resource
from .types import Runtime


class PlatformResponse(object):
    def __init__(self, resp: str):
        self.__dict__ = json.loads(resp)


class PlatformResource(Resource):
    _pipelineName = ""

    def __init__(
        self, resource, client_options: meroxa.ClientOptions, app_config: AppConfig
    ) -> None:
        self.resource = resource
        self.app_config = app_config
        self.client_opts = client_options
        self._pipelineName = f"turbine-pipeline-{app_config.name}"

    async def records(self, collection: str, config: dict[str, str] = None) -> Records:
        print(f"Checking if pipeline exists for application: {self.app_config.name}")

        try:
            async with Meroxa(
                auth=self.client_opts.auth, api_route=self.client_opts.url
            ) as m:
                resp = await m.pipelines.get(self._pipelineName)

            if resp[0] is not None:
                if resp[0].code == "not_found":
                    print(
                        f"No pipeline found, creating a new pipeline: "
                        f"{self._pipelineName}"
                    )
                    pipeline_input = meroxa.CreatePipelineParams(
                        name=self._pipelineName,
                        metadata={"turbine": True, "app": self.app_config.name},
                        environment=self.app_config.environment,
                    )
                    async with Meroxa(
                        auth=self.client_opts.auth, api_route=self.client_opts.url
                    ) as m:
                        resp = await m.pipelines.create(pipeline_input)

                    if resp[0] is not None:
                        raise ChildProcessError(
                            f"Error creating a pipeline for "
                            f"application {self.resource.name} : {resp[0].message}"
                        )
                    pipeline_uuid = resp[1].uuid
                    print(
                        'pipeline: "{}" ("{}")'.format(
                            self._pipelineName, pipeline_uuid
                        )
                    )
                else:
                    raise ChildProcessError(
                        f"Error looking up the application - "
                        f"{self.resource.name} : {resp[0].message}"
                    )
            else:
                pipeline_uuid = resp[1].uuid
                print(f'pipeline: "{self._pipelineName}" ("{pipeline_uuid}")')

            print(f"Creating SOURCE connector from resource: {self.resource.name}")

            if config is None:
                config = {}
            config["input"] = collection

            connector_input = meroxa.CreateConnectorParams(
                resource_name=self.resource.name,
                pipeline_name=self._pipelineName,
                config=config,
                metadata={
                    "mx:connectorType": "source",
                },
            )

            async with Meroxa(
                auth=self.client_opts.auth, api_route=self.client_opts.url
            ) as m:
                connector: meroxa.ConnectorsResponse
                # Error Handling: Duplicate connector
                # Check for `bad_request`
                resp = await m.connectors.create(connector_input)
            if resp[0] is not None:
                raise ChildProcessError(
                    f"Error creating source connector from resource"
                    f" {self.resource.name} : {resp[0].message}"
                )
            else:
                connector = resp[1]
                output = connector.streams["output"]
                if isinstance(output, list):
                    stream = output[0]
                else:
                    stream = output
                print(f"Successfully created {connector.name} connector")

                return Records(records=[], stream=stream)
        except ChildProcessError as cpe:
            raise ChildProcessError(cpe)
        except Exception as e:
            raise Exception(e)

    async def write(
        self, records: Records, collection: str, config: dict[str, str] = None
    ) -> None:
        print(f"Creating DESTINATION connector from stream: {records.stream}")

        try:
            # Connector config
            # Move the non-shared logics to a separate function
            if config is None:
                config = {}
            config["input"] = records.stream
            if self.resource.type in (
                ResourceType.REDSHIFT.value,
                ResourceType.POSTGRES.value,
                ResourceType.MYSQL.value,
            ):  # JDBC sink
                config["table.name.format"] = str(collection).lower()
            elif self.resource.type == ResourceType.MONGODB.value:
                config["collection"] = str(collection).lower()
            elif self.resource.type == ResourceType.S3.value:
                config["aws_s3_prefix"] = str(collection).lower() + "/"
            elif self.resource.type == ResourceType.SNOWFLAKE.value:
                result = re.match("^[a-zA-Z]{1}[a-zA-Z0-9_]*$", str(collection))
                if result is None:
                    raise ChildProcessError(
                        f"'{str(collection)}' is an invalid Snowflake name - "
                        f"must start with a letter and contain only letters, "
                        f"numbers, and underscores"
                    )
                else:
                    config[
                        "snowflake.topic2table.map"
                    ] = f"{records.stream}:{str(collection)}"

            connector_input = meroxa.CreateConnectorParams(
                resource_name=self.resource.name,
                pipeline_name=self._pipelineName,
                config=config,
                metadata={
                    "mx:connectorType": "destination",
                },
            )

            async with Meroxa(
                auth=self.client_opts.auth, api_route=self.client_opts.url
            ) as m:
                resp = await m.connectors.create(connector_input)
            if resp[0] is not None:
                raise ChildProcessError(
                    f"Error creating destination connector "
                    f"from stream {records.stream} : {resp[0].message}"
                )
            else:
                print(f"Successfully created {resp[1].name} connector")
                return None
        except ChildProcessError as cpe:
            raise ChildProcessError(cpe)
        except Exception as e:
            raise Exception(e)


class PlatformRuntime(Runtime):
    _registeredFunctions = {}
    _secrets = {}

    def __init__(
        self, client_options: meroxa.ClientOptions, image_name: str, config: AppConfig
    ) -> None:
        self._image_name = image_name
        self._app_config = config
        self._client_opts = client_options

    async def resources(self, resource_name: str):
        try:
            async with Meroxa(
                auth=self._client_opts.auth, api_route=self._client_opts.url
            ) as m:
                resp = await m.resources.get(resource_name)

            if resp[0] is not None:
                raise ChildProcessError(
                    "Error finding resource {} : {}".format(
                        resource_name, resp[0].message
                    )
                )
            else:
                return PlatformResource(
                    resource=resp[1],
                    client_options=self._client_opts,
                    app_config=self._app_config,
                )
        except ChildProcessError as cpe:
            raise ChildProcessError(cpe)
        except Exception as e:
            raise Exception(e)

    async def process(
        self, records: Records, fn: t.Callable[[t.List[Record]], t.List[Record]]
    ) -> Records:

        pipeline_id = PipelineIdentifiers(
            name=f"turbine-pipeline-{self._app_config.name}"
        )

        # Create function parameters
        create_func_params = meroxa.CreateFunctionParams(
            input_stream=records.stream,
            output_stream="",
            name="",
            command=["python"],
            args=["function_server.py", fn.__name__],
            image=self._image_name,
            pipeline=pipeline_id,
            env_vars=self._secrets,
        )

        if self._image_name == "":
            raise Exception("Process image name not provided")

        print(f"Deploying Process: {getattr(fn, '__name__', 'Unknown')}")

        async with Meroxa(
            auth=self._client_opts.auth, api_route=self._client_opts.url
        ) as m:
            resp = await m.functions.create(create_func_params)
        try:
            if resp[0] is not None:
                raise ChildProcessError(
                    f"Error deploying Process "
                    f"{getattr(fn, '__name__', 'Unknown')} : {resp[0].message}"
                )
            else:
                func = resp[1]
                records.stream = func.output_stream
                return records
        except ChildProcessError as cpe:
            raise ChildProcessError(cpe)
        except Exception as e:
            raise Exception(e)

    def register_secrets(self, name: str) -> None:

        sec = os.getenv(name)
        if not sec:
            raise Exception(f"Secret invalid or unset: {name}")

        self._secrets.update({name: sec})
