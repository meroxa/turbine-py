import json
import os
import typing as t

from .runtime import AppConfig
from .runtime import LocalRuntime
from .runtime import PlatformRuntime
from .runtime import Record, Records, ClientOptions
from .runtime import Runtime

MEROXA_ACCESS_TOKEN = "MEROXA_ACCESS_TOKEN"
MEROXA_API_URL = "MEROXA_API_URL"
DOCKER_HUB_USERNAME = "DOCKER_HUB_USERNAME"

PLATFORM_RUNTIME = "platform"


class Turbine(Runtime):
    _runtime = None

    def __init__(self, runtime: str, path_to_data_app: str):
        with open(os.path.abspath(f"{path_to_data_app}") + "/app.json") as fd:
            config = AppConfig(**json.load(fd))

        if runtime is not PLATFORM_RUNTIME:
            self._runtime = self.runtime = LocalRuntime(
                config=config, path_to_app=path_to_data_app
            )

            return

        self._runtime = PlatformRuntime(
            config=config,
            client_options=ClientOptions(
                auth=os.getenv(MEROXA_ACCESS_TOKEN), url=os.getenv(MEROXA_API_URL)
            ),
            image_name="{}/{}".format(os.getenv(DOCKER_HUB_USERNAME), config.name),
        )

    async def resources(self, name: str):
        return await self._runtime.resources(name)

    async def process(
        self,
        records: Records,
        fn: t.Callable[[t.List[Record]], t.List[Record]],
        env_vars=None,
    ) -> Records:
        return await self._runtime.process(records, fn, env_vars)
