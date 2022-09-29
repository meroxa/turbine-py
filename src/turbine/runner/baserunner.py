import json
import os
import sys

from ..runtime import AppConfig
from ..runtime import InfoRuntime
from ..runtime import LocalRuntime


class BaseRunner:
    path_to_data_app: str
    info_runtime = None
    local_runtime = None
    app_name = None

    def __init__(self, path_to_data_app: str, name: str = None):
        self.path_to_data_app = path_to_data_app
        self.app_name = name
        self.info_runtime = InfoRuntime(self.app_config, self.path_to_data_app)
        self.local_runtime = LocalRuntime(self.app_config, self.path_to_data_app)

    @property
    def app_config(self):
        config = {}
        try:
            with open(os.path.abspath(f"{self.path_to_data_app}") + "/app.json") as fd:
                config = AppConfig(**json.load(fd))
                if self.app_name != "":
                    config.name = self.app_name
        except OSError as e:
            print(f"Unable to locate app config: {e}", file=sys.stderr)
        return config

    @property
    def data_app(self):
        # Append the user's data application to the execution path
        # for the runners
        sys.path.append(self.path_to_data_app)
        from main import App

        return App

    async def run_app_local(self):
        await self.data_app.run(self.local_runtime)

    async def list_functions(self):
        try:
            await self.data_app.run(self.info_runtime)
            return self.info_runtime.functions_list()
        except Exception as e:
            print(f"something went wrong: {e}")

    async def has_functions(self):
        try:
            await self.data_app.run(self.info_runtime)
            return str(self.info_runtime.has_functions()).lower()
        except Exception as e:
            print(f"something went wrong: {e}")

    async def list_resources(self):
        try:
            await self.data_app.run(self.info_runtime)
            return self.info_runtime.resources_list()
        except Exception as e:
            print(f"something went wrong: {e}")
