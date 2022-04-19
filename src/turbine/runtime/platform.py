import json
import typing as t
import os

import meroxa
from meroxa import Meroxa
from meroxa.types import PipelineIdentifiers

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

    async def records(self, collection: str) -> Records:
        print(f"Check if pipeline exists for application: {self.app_config.name}")

        try:
            async with Meroxa(auth=self.client_opts.auth) as m:
                resp = await m.pipelines.get(self._pipelineName)

            if resp[0] is not None:
                if resp[0].code == "not_found":
                    print(
                        f"No pipeline found, "
                        f"creating a new pipeline: {self._pipelineName}"
                    )
                    pipeline_input = meroxa.CreatePipelineParams(
                        name=self._pipelineName,
                        metadata={"turbine": True, "app": self.app_config.name},
                        environment=self.app_config.environment,
                    )
                    async with Meroxa(auth=self.client_opts.auth) as m:
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

            print(f"Creating SOURCE connector from source: {self.resource.name}")
            connector_config = {"input": collection}

            connector_input = meroxa.CreateConnectorParams(
                resourceName=self.resource.name,
                pipelineName=self._pipelineName,
                config=connector_config,
                metadata={
                    "mx:connectorType": "source",
                },
            )
            async with Meroxa(auth=self.client_opts.auth) as m:
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
                return Records(records=[], stream=connector.streams.output)
        except ChildProcessError as cpe:
            raise ChildProcessError(cpe)
        except Exception as e:
            raise Exception(e)

    async def write(self, records: Records, collection: str) -> None:
        print(f"Creating DESTINATION connector from stream: {records.stream}")

        try:
            # Connector config
            # Move the non-shared logics to a separate function
            connector_config = {"input": records.stream}
            if self.resource.type in ("redshift", "postgres", "mysql"):  # JDBC sink
                connector_config["table.name.format"] = str(collection).lower()
            elif self.resource.type == "mongodb":
                connector_config["collection"] = str(collection).lower()
            elif self.resource.type == "s3":
                connector_config["aws_s3_prefix"] = str(collection).lower() + "/"
            elif self.resource.type == "snowflake.topic2table.map":
                connector_config["aws_s3_prefix"] = f"{records.stream}:{str(collection).lower()}" + "/"

            connector_input = meroxa.CreateConnectorParams(
                resourceName=self.resource.name,
                pipelineName=self._pipelineName,
                config=connector_config,
                metadata={
                    "mx:connectorType": "destination",
                },
            )
            async with Meroxa(auth=self.client_opts.auth) as m:
                resp = await m.connectors.create(connector_input)
            if resp[0] is not None:
                raise ChildProcessError(
                    f"Error creating destination connector "
                    f"from stream {records.stream[0]} : {resp[0].message}"
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
            async with Meroxa(auth=self._client_opts.auth) as m:
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
            pipelineIdentifiers=PipelineIdentifiers(
                name="turbine-pipeline-{}".format(self._app_config.name)
            ),
            envVars=env_vars,
        )

        if self._image_name == "":
            raise Exception("Process image name not provided")

        print(f"deploying Process: {getattr(fn, '__name__', 'Unknown')}")

        async with Meroxa(auth=self._client_opts.auth) as m:
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
