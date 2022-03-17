import json
import os
import typing as t

from .runtime import Runtime
from .runtime import LocalRuntime
from .runtime import PlatformRuntime
from .runtime import AppConfig
from .runtime import Record, Records, ClientOptions


MEROXA_ACCESS_TOKEN = "MEROXA_ACCESS_TOKEN"
MEROXA_API_URL = 'MEROXA_API_URL'
DOCKER_HUB_USERNAME = 'DOCKER_HUB_USERNAME'

PLATFORM_RUNTIME = 'platform'


class Turbine(Runtime):

    _runtime = None

    def __init__(self, runtime: str, path_to_data_app: str):

        with open(os.path.abspath("{}/app.json").format(path_to_data_app)) as fd:
            config = AppConfig(**json.load(fd))

        if runtime is not PLATFORM_RUNTIME:
            self._runtime = self.runtime = LocalRuntime(
                config=config,
                pathToApp=path_to_data_app
            )

            return

        # We do some docker things here presumably eventually 
        
        print(os.getenv(MEROXA_ACCESS_TOKEN))
        self._runtime = PlatformRuntime(
            config=config,
            clientOptions=ClientOptions(
                auth=os.getenv(MEROXA_ACCESS_TOKEN),
                url=os.getenv(MEROXA_API_URL)
            ),
            imageName='{}/{}'.format(
                os.getenv(DOCKER_HUB_USERNAME),
                config.name
            )
        )

    def resources(self, name: str):
        return self._runtime.resources(name)

    def process(
            self,
            records: Records,
            fn: t.Callable[[t.List[Record]], t.List[Record]]) -> Records:
        return self._runtime.process(records, fn)
