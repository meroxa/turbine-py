import importlib.util
import json
import os
import sys

from ..runtime import InfoRuntime, LocalRuntime, AppConfig


class BaseRunner:
    path_to_data_app: str
    info_runtime = None
    local_runtime = None

    def __init__(self, path_to_data_app: str):
        # use setter to get the app_json and set the local value lmao this is silly

        self.path_to_data_app = path_to_data_app
        self.info_runtime = InfoRuntime(self.app_config, self.path_to_data_app)
        self.local_runtime = LocalRuntime(self.app_config, self.path_to_data_app)

    @property
    def app_config(self):
        config = {}
        try:
            with open(os.path.abspath(f"{self.path_to_data_app}") + "/app.json") as fd:
                config = AppConfig(**json.load(fd))
        except OSError as e:
            print(f"Unable to locate app config: {e}", file=sys.stderr)
        return config

    @property
    def data_app(self):
        spec = importlib.util.spec_from_file_location(
            "main.py", os.path.join(self.path_to_data_app, "main.py")
        )
        data_app = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(data_app)
        return data_app

    async def run_app_local(self):
        await self.data_app.__getattribute__("App").run(self.local_runtime)

    async def list_functions(self):
        try:
            await self.data_app.__getattribute__("App").run(self.info_runtime)
            return self.info_runtime.functions_list()
        except Exception as e:
            print(f"something broke{e}")

    async def has_functions(self):
        try:
            await self.data_app.__getattribute__("App").run(self.info_runtime)
            return str(self.info_runtime.has_functions()).lower()
        except Exception as e:
            print(f"something broke{e}")
