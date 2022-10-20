import json
import os
import re
import typing as t

import meroxa
from meroxa import Meroxa
from meroxa.pipelines import PipelineIdentifiers
from meroxa.types import ResourceType

from .types import AppConfig
from .types import ClientOptions
from .types import RecordList
from .types import Records
from .types import Resource
from .types import Runtime

global __application_uuid


class PlatformResponse(object):
    def __init__(self, resp: str):
        self.__dict__ = json.loads(resp)


class PlatformResource(Resource):
    _pipeline_name = ""

    def __init__(
        self, resource, client_options: ClientOptions, app_config: AppConfig
    ) -> None:
        self.resource = resource
        self.app_config = app_config
        self.client_opts = client_options
        self._pipeline_name = f"turbine-pipeline-{app_config.name}"

    async def _create_application(self, pipeline_name: str):
        app_input = meroxa.CreateApplicationParams(
            name=self.app_config.name,
            language="python",
            git_sha=self.app_config.git_sha,
            pipeline=meroxa.PipelineIdentifiers(name=pipeline_name),
        )

        async with Meroxa(
            auth=self.client_opts.auth,
            api_route=self.client_opts.url,
            meroxa_account_uuid=self.client_opts.meroxa_account_uuid,
        ) as m:
            resp = await m.applications.create(app_input)

        if resp[0] is not None:
            raise ChildProcessError(
                f"Error creating Application "
                f"{self.app_config.name} : {resp[0].message}"
            )

        return resp[1].uuid

    async def _create_pipeline(self):
        pipeline_input = meroxa.CreatePipelineParams(
            name=self._pipeline_name,
            metadata={"turbine": True, "app": self.app_config.name},
            environment=self.app_config.environment,
        )
        async with Meroxa(
            auth=self.client_opts.auth,
            api_route=self.client_opts.url,
            meroxa_account_uuid=self.client_opts.meroxa_account_uuid,
        ) as m:
            resp = await m.pipelines.create(pipeline_input)

        if resp[0] is not None:
            raise ChildProcessError(
                f"Error creating a pipeline for "
                f"application {self.app_config.name} : {resp[0].message}"
            )
        return resp[1].uuid

    async def records(self, collection: str, config: dict[str, str] = None) -> Records:
        print(f"Checking if pipeline exists for application: {self.app_config.name}")

        try:
            if config is None:
                config = {}
            if self.resource.type in (
                ResourceType.KAFKA.value,
                ResourceType.CONFLUENTCLOUD.value,
            ):
                config["conduit"] = "true"

            async with Meroxa(
                auth=self.client_opts.auth,
                api_route=self.client_opts.url,
                meroxa_account_uuid=self.client_opts.meroxa_account_uuid,
            ) as m:
                resp = await m.pipelines.get(self._pipeline_name)

            if resp[0] is not None:
                if resp[0].code == "not_found":
                    print(
                        f"No pipeline found, creating a new pipeline: "
                        f"{self._pipeline_name}"
                    )
                    await self._create_pipeline()

                else:
                    raise ChildProcessError(
                        f"Error looking up the application - "
                        f"{self.resource.name} : {resp[0].message}"
                    )

            print(f"Creating SOURCE connector from resource: {self.resource.name}")

            if config is None:
                config = {}
            config["input"] = collection

            connector_input = meroxa.CreateConnectorParams(
                resource_name=self.resource.name,
                pipeline_name=self._pipeline_name,
                config=config,
                metadata={
                    "mx:connectorType": "source",
                },
            )

            async with Meroxa(
                auth=self.client_opts.auth,
                api_route=self.client_opts.url,
                meroxa_account_uuid=self.client_opts.meroxa_account_uuid,
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

                return Records(records=RecordList(), stream=stream)
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
                ResourceType.SQLSERVER.value,
            ):  # JDBC sink
                config["table.name.format"] = str(collection).lower()
            elif self.resource.type == ResourceType.MONGODB.value:
                config["collection"] = str(collection).lower()
            elif self.resource.type in (
                ResourceType.KAFKA.value,
                ResourceType.CONFLUENTCLOUD.value,
            ):
                config["conduit"] = "true"
                config["topic"] = str(collection).lower()
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
                pipeline_name=self._pipeline_name,
                config=config,
                metadata={
                    "mx:connectorType": "destination",
                },
            )

            async with Meroxa(
                auth=self.client_opts.auth,
                api_route=self.client_opts.url,
                meroxa_account_uuid=self.client_opts.meroxa_account_uuid,
            ) as m:
                resp = await m.connectors.create(connector_input)
            if resp[0] is not None:
                raise ChildProcessError(
                    f"Error creating destination connector "
                    f"from stream {records.stream} : {resp[0].message}"
                )
            else:
                print(f"Successfully created {resp[1].name} connector")

            if not globals().get("__application_uuid"):
                print(f"Creating application: {self.app_config.name}")
                res = await self._create_application(self._pipeline_name)
                globals().update({"__application_uuid": res})
                print(f"Successfully created application: {self.app_config.name}")

        except ChildProcessError as cpe:
            raise ChildProcessError(cpe)
        except Exception as e:
            raise Exception(e)


class PlatformRuntime(Runtime):
    _registeredFunctions = {}
    _secrets = {}

    def __init__(
        self,
        client_options: ClientOptions,
        image_name: str,
        git_sha: str,
        config: AppConfig,
    ) -> None:
        self._client_opts = client_options
        self._image_name = image_name
        self._git_sha = git_sha
        self._app_config = config

    async def resources(self, resource_name: str):
        print(f"Fetching resource named '{resource_name}'")

        try:
            async with Meroxa(
                auth=self._client_opts.auth,
                api_route=self._client_opts.url,
                meroxa_account_uuid=self._client_opts.meroxa_account_uuid,
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
        self, records: Records, fn: t.Callable[[RecordList], RecordList]
    ) -> Records:

        pipeline_id = PipelineIdentifiers(
            name=f"turbine-pipeline-{self._app_config.name}"
        )
        func_name_git_sha = f"{fn.__name__}-{self._git_sha[:8]}"
        # Create function parameters
        create_func_params = meroxa.CreateFunctionParams(
            input_stream=records.stream,
            output_stream="",
            name=f"{func_name_git_sha}",
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
            auth=self._client_opts.auth,
            api_route=self._client_opts.url,
            meroxa_account_uuid=self._client_opts.meroxa_account_uuid,
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
