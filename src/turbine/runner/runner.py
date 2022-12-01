import json
import os
import pprint
import shutil
import tempfile
from urllib.parse import urlparse

from ..runtime import ClientOptions
from ..runtime import IntermediateRuntime
from ..runtime import PlatformRuntime
from .baserunner import BaseRunner

_ROOT = os.path.abspath(os.path.dirname(__file__))


class Runner(BaseRunner):
    async def build_function(self):
        temp_dir = tempfile.gettempdir()
        temp_dir_turbine_path = os.path.join(temp_dir + "/turbine")
        deploy_dir = os.path.join(_ROOT, "../function_deploy")

        shutil.rmtree(temp_dir_turbine_path, ignore_errors=True)
        os.mkdir(os.path.join(temp_dir_turbine_path))
        try:
            shutil.copytree(deploy_dir, temp_dir_turbine_path, dirs_exist_ok=True)
            shutil.copytree(
                self.path_to_data_app,
                temp_dir_turbine_path + "/data_app",
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

    async def run_app_platform(self, image_name, git_sha):
        parsed_url = None
        url = os.environ.get("MEROXA_API_URL")
        if url is not None:
            parsed_url = urlparse(url)
            parsed_url = f"https://{parsed_url.netloc}"

        app_config = self.app_config
        app_config.git_sha = git_sha
        deployment_spec = PlatformRuntime(
            client_options=ClientOptions(
                auth=os.environ.get("MEROXA_ACCESS_TOKEN"),
                url=parsed_url,
                meroxa_account_uuid=os.environ.get("MEROXA_ACCOUNT_UUID"),
            ),
            image_name=image_name,
            git_sha=git_sha,
            config=app_config,
        )

        try:
            await self.data_app.run(deployment_spec)
            return
        except Exception as e:
            print(f"{e}")
            return

    async def run_app_platform_v2(self, image_name, git_sha, version, spec):
        parsed_url = None
        url = os.environ.get("MEROXA_API_URL")
        if url is not None:
            parsed_url = urlparse(url)
            parsed_url = f"https://{parsed_url.netloc}"

        app_config = self.app_config
        app_config.git_sha = git_sha

        deployment_spec = IntermediateRuntime(
            client_options=ClientOptions(
                auth=os.environ.get("MEROXA_ACCESS_TOKEN"),
                url=parsed_url,
                meroxa_account_uuid=os.environ.get("MEROXA_ACCOUNT_UUID"),
            ),
            image_name=image_name,
            git_sha=git_sha,
            version=version,
            spec=spec,
            config=app_config,
        )

        try:
            await self.data_app.run(deployment_spec)
            print(f"turbine-response: {json.dumps(deployment_spec.serialize())}\n")
            return
        except Exception as e:
            pprint.pprint(f"{e}")
            return
