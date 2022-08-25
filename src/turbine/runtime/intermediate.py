import json
import os
import typing as t

import meroxa

from .types import AppConfig
from .types import RecordList
from .types import Records
from .types import Runtime


class IntermediateResource:
    def __init__(self, resource_name: str):
        self._resource = resource_name
        self.resource_type: str = ""
        self.collection: str = ""
        self.config: dict = {}

    def _persist(
        self, resource_type: str, collection: str, config: dict[str, str] = None
    ):
        self.resource_type = resource_type
        self.collection = collection
        self.config.update(config)

    async def records(self, collection: str, config: dict[str, str] = None) -> None:
        if config is None:
            config = {}
        self._persist("source", collection, config)

    async def write(
        self, records, collection: str, config: dict[str, str] = None
    ) -> None:
        if config is None:
            config = {}
        self._persist("destination", collection, config)

    def __repr__(self):
        return json.dumps(
            {
                "type": self.resource_type,
                "resource": self._resource,
                "collection": self.collection,
            }
        )


class IntermediateFunction:
    name: str
    image: str

    def __init__(self, name: str, commit_hash: str, image: str):
        self.name = f"{name}-{commit_hash[:8]}"
        self.image = image

    def __repr__(self):
        return json.dumps(
            {
                "name": self.name,
                "image": self.image,
            }
        )


class IntermediateRuntime(Runtime):
    _registered_resources = []
    _registered_functions = []
    _secrets = {}

    def __init__(
        self,
        client_options: meroxa.ClientOptions,
        image_name: str,
        git_sha: str,
        version: str,
        spec: str,
        config: AppConfig,
    ) -> None:
        self._client_opts = client_options
        self._image_name = image_name
        self._git_sha = git_sha
        self._version = version
        self._spec = spec
        self._app_config = config

    def definition(self):
        return {
            "app_name": self._app_config.name,
            "git_sha": self._git_sha,
            "metadata": {
                "turbine": {
                    "language": "py",
                    "version": self._version,
                },
                "spec_version": self._spec,
            },
        }

    async def resources(self, resource_name: str) -> IntermediateResource:
        resource = IntermediateResource(resource_name)
        self._registered_resources.append(resource)
        return resource

    async def process(
        self, records: Records, fn: t.Callable[[RecordList], RecordList]
    ) -> None:  # Create new function
        function = IntermediateFunction(fn.__name__, self._git_sha, self._image_name)
        self._registered_functions.append(function)

    def register_secrets(self, name: str) -> None:
        sec = os.getenv(name)
        if not sec:
            raise Exception(f"Secret invalid or unset: {name}")

        self._secrets.update({name: sec})

    def serialize(self) -> dict:
        return {
            "connectors": self._registered_resources,
            "secrets": self._secrets,
            "functions": self._registered_functions,
            "definition": self.definition(),
        }
