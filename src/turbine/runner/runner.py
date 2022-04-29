import os
import shutil
import tempfile
from urllib.parse import urlparse

from .baserunner import BaseRunner
from ..runtime import PlatformRuntime, ClientOptions

_ROOT = os.path.abspath(os.path.dirname(__file__))


class Runner(BaseRunner):
    async def build_function(self):
        temp_dir = tempfile.gettempdir()
        temp_dir_turbine_path = os.path.join(temp_dir + "/turbine")
        deploy_dir = os.path.join(_ROOT, "../function-deploy")

        shutil.rmtree(temp_dir_turbine_path, ignore_errors=True)
        os.mkdir(os.path.join(temp_dir_turbine_path))
        try:
            shutil.copytree(deploy_dir, temp_dir_turbine_path, dirs_exist_ok=True)
            shutil.copytree(
                self.path_to_data_app,
                temp_dir_turbine_path + "/data-app",
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

    async def run_app_platform(self, image_name):
        parsed_url = urlparse(os.environ.get("MEROXA_API_URL"))

        environment = PlatformRuntime(
            client_options=ClientOptions(
                auth=os.environ.get("MEROXA_ACCESS_TOKEN"),
                url=f"https://{parsed_url.netloc}",
            ),
            image_name=image_name,
            config=self.app_config,
        )

        try:
            await self.data_app.run(environment)
            return
        except Exception as e:
            print(f"{e}")
            return
