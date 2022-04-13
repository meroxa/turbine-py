import asyncio
import os
import sys

from turbine import turbine


def run_app_local(path_to_data_app: str, *args, **kwargs):
    sys.path.append(os.path.abspath(path_to_data_app))

    from main import App

    client = turbine.Turbine("local", path_to_data_app)
    asyncio.run(App.run(client))
