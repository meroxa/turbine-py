import json
import os
import shutil
import sys
from pathlib import Path
import grpc
from importlib.metadata import distribution
from .app import TurbineApp
from .proto_gen import InitRequest
from .proto_gen import TurbineServiceStub

TURBINE_CORE_SERVER = os.getenv("TURBINE_CORE_SERVER")
LANGUAGE = "PYTHON"
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


class TurbineClient:
    def __init__(self, app_path: str = None) -> None:
        self.app_path = app_path

    @property
    def data_app(self):
        # Append the user's data application to the execution path
        # for the runners
        sys.path.append(self.app_path)
        from main import App

        return App

    async def init_core_server(self, git_sha: str = None) -> TurbineApp:
        channel = grpc.insecure_channel(
            TURBINE_CORE_SERVER, options=(("grpc.enable_http_proxy", 0),)
        )
        core_server = TurbineServiceStub(channel)
        config_file_path = self.app_path
        print(config_file_path)
        with open(Path(config_file_path, "app.json"), "r") as myfile:
            data = myfile.read()
        app_config = json.loads(data)
        dist = distribution("turbine-py")
        request = InitRequest(
            appName=app_config["name"],
            language=LANGUAGE,
            configFilePath=config_file_path,
            gitSHA=git_sha,
            turbineVersion=dist.version,
        )
        core_server.Init(request)
        return TurbineApp(core_server)

    async def run(self):
        turbine = await self.init_core_server()
        await self.data_app().run(turbine)

    async def records(self, git_sha: str):
        turbine = await self.init_core_server(git_sha=git_sha)
        await self.data_app().run(turbine)

    async def build_function(self):
        docker_file = os.path.join(_ROOT, "function_deploy", "Dockerfile")
        try:
            shutil.copyfile(docker_file, Path(self.app_path, "Dockerfile"))
            return f"turbine-response: {self.app_path}"
        except Exception as e:
            self.clean_temp_directory(self.app_path)
            print(f"build failed: {e}")
        except FileExistsError as err:
            print(f"unable to build: {err}")

    @staticmethod
    def clean_temp_directory(tmp_dir):
        shutil.rmtree(tmp_dir, ignore_errors=True)
