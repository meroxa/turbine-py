import json
import os
import typing as t
from os.path import join, dirname

from .runtime import AppConfig
from .runtime import LocalRuntime
from .runtime import PlatformRuntime
from .runtime import Record, Records, ClientOptions
from .runtime import Runtime


class Turbine(Runtime):
    _runtime = None

    def __init__(self, runtime: str, path_to_data_app: str, image_name: str):
        with open(os.path.abspath(f"{path_to_data_app}") + "/app.json") as fd:
            config = AppConfig(**json.load(fd))
        if runtime != "platform":
            self._runtime = self.runtime = LocalRuntime(
                config=config, path_to_app=path_to_data_app
            )
        else:
            self._runtime = PlatformRuntime(
                config=config,
                client_options=ClientOptions(
                    auth=os.environ.get("MEROXA_ACCESS_TOKEN"),
                    url=os.environ.get("MEROXA_API_URL"),
                ),
                image_name=image_name,
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

    async def list_functions(self):
        return await self._runtime.list_functions()

    async def has_functions(self):
        return await self._runtime.has_functions()
