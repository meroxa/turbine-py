import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
import grpc

from .app import TurbineApp
from .proto_gen import InitRequest
from .proto_gen import TurbineServiceStub

TURBINE_CORE_SERVER = os.getenv("TURBINE_CORE_SERVER")
LANGUAGE = "PYTHON"
_ROOT = os.path.abspath(os.path.dirname(__file__))


class TurbineClient:
    def __init__(self) -> None:
        pass

    @property
    def data_app(self):
        # Append the user's data application to the execution path
        # for the runners
        sys.path.append(os.getcwd())
        from main import App

        return App

    async def init_core_server(self, git_sha: str) -> TurbineApp:
        channel = grpc.insecure_channel(TURBINE_CORE_SERVER)
        core_server = TurbineServiceStub(channel)
        config_file_path = os.getcwd()
        with open(Path(config_file_path, "app.json"), "r") as myfile:
            data = myfile.read()
        app_config = json.loads(data)

        request = InitRequest(
            appName=app_config["name"],
            language=LANGUAGE,
            configFilePath=config_file_path,
            gitSHA=git_sha,
        )
        core_server.Init(request)
        return TurbineApp(core_server)

    async def run(self, git_sha: str):
        turbine = await self.init_core_server(git_sha=git_sha)
        await self.data_app().run(turbine)

    async def records(self, git_sha: str):
        turbine = self.init_core_server(git_sha=git_sha)
        await self.data_app().run(turbine)

    async def build_function(self):
        temp_dir = tempfile.mkdtemp()
        temp_dir_turbine_path = os.path.join(temp_dir, "turbine")
        deploy_dir = os.path.join(_ROOT, "..", "function_deploy")

        shutil.rmtree(temp_dir_turbine_path, ignore_errors=True)
        os.mkdir(temp_dir_turbine_path)
        try:
            shutil.copytree(deploy_dir, temp_dir_turbine_path, dirs_exist_ok=True)
            shutil.copytree(
                self.path_to_data_app,
                os.path.join(temp_dir_turbine_path, "data_app"),
                dirs_exist_ok=True,
            )
            return f"turbine-response: {temp_dir_turbine_path}"
        except Exception as e:
            self.clean_temp_directory(temp_dir_turbine_path)
            print(f"build failed: {e}")
        except FileExistsError as err:
            print(f"unable to build: {err}")

    @staticmethod
    def clean_temp_directory(tmp_dir):
        shutil.rmtree(tmp_dir, ignore_errors=True)
