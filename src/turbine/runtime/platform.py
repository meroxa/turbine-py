from importlib.metadata import metadata
import json
from os import environ
import typing as t

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
        self._pipelineName = "turbine-pipeline-{}".format(app_config.name)

    async def records(self, collection: str) -> Records:
        print(f"Check if pipeline exists for application: {self.app_config.name}")

        try:
            async with Meroxa(auth=self.client_opts.auth) as m:
                resp = await m.pipelines.get(self._pipelineName)

            if resp[0] is not None:
                if resp[0].code == "not_found":
                    print(
                        f"No pipeline found, creating a new pipeline: {self._pipelineName}"
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
                            "Error creating a pipeline for application {} : {}".format(
                                self.resource.name, resp[0].message
                            )
                        )
                    pipeline_uuid = resp[1].uuid
                    print(
                        'pipeline: "{}" ("{}")'.format(
                            self._pipelineName, pipeline_uuid
                        )
                    )
                else:
                    raise ChildProcessError(
                        "Error looking up the application - {} : {}".format(
                            self.resource.name, resp[0].message
                        )
                    )
            else:
                pipeline_uuid = resp[1].uuid
                print(
                    'pipeline: "{}" ("{}")'.format(
                        self._pipelineName, pipeline_uuid
                    )
                )

            print(f"Creating SOURCE connector from source: {self.resource.name}")
            connector_config = {}
            connector_config["input"] = collection
            if self.resource.type in ("redshift", "postgres", "mysql"):
                connector_config["transforms"] = "createKey,extractInt"
                connector_config["transforms.createKey.fields"] = "id"
                connector_config[
                    "transforms.createKey.type"
                ] = "org.apache.kafka.connect.transforms.ValueToKey"
                connector_config["transforms.extractInt.field"] = "id"
                connector_config[
                    "transforms.extractInt.type"
                ] = "org.apache.kafka.connect.transforms.ExtractField$Key"

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
                    "Error creating source connector from resource {} : {}".format(
                        self.resource.name, resp[0].message
                    )
                )
            else:
                connector = resp[1]
                return Records(records=[], stream=connector.streams.output)
        except ChildProcessError as cpe:
            raise ChildProcessError(cpe)
        except Exception as e:
            raise Exception(e)

    async def write(self, records: Records, collection: str) -> None:
        print(f"Creating DESTINATION connector from stream: {records.stream[0]}")

        try:
            # Connector config
            # Move the non-shared logics to a separate function
            connector_config = {}
            connector_config["input"] = records.stream[0]
            if self.resource.type in ("redshift", "postgres", "mysql"): # JDBC sink
                connector_config["table.name.format"] = str(collection).lower()
                connector_config["pk.mode"] = "record_value"
                connector_config["pk.fields"] = "id"
                if self.resource.type != "redshift":
                    connector_config["insert.mode"] = "upsert"

            elif self.resource.type == "s3":
                connector_config["aws_s3_prefix"] = str(collection).lower() + "/"
                connector_config["value.converter"] = "org.apache.kafka.connect.json.JsonConverter"
                connector_config["value.converter.schemas.enable"] = "true"
                connector_config["format.output.type"] = "jsonl"
                connector_config["format.output.envelope"] = "true"

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
                    "Error creating destination connector from stream {} : {}".format(
                        records.stream[0], resp[0].message
                    )
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

    def __init__(
        self, client_options: meroxa.ClientOptions, image_name: str, config: AppConfig
    ) -> None:
        self._image_name = image_name
        self._app_config = config
        self._client_opts = client_options

    async def resources(self, resource_name: str):
        async with Meroxa(auth=self._client_opts.auth) as m:
            resp = await m.resources.get(resource_name)

        try:
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
                    "Error deploying Process {} : {}".format(
                        getattr(fn, "__name__", "Unknown"), resp[0].message
                    )
                )
            else:
                func = resp[1]
                records.stream = func.output_stream
                return records
        except ChildProcessError as cpe:
            raise ChildProcessError(cpe)
        except Exception as e:
            raise Exception(e)

    async def list_functions(self):
        return print(
            "List of application Processes : \n {}".format(
                "\n".join(self.registered_functions)
            )
        )

    async def has_functions(self):
        if self._registeredFunctions:
            return True
        return False
