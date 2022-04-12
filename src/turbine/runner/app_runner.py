import asyncio
import os
import sys
from turbine import turbine


def run_app_local(path_to_data_app: str, runtime: str, *args, **kwargs):
    sys.path.append(os.path.abspath(path_to_data_app))

    from main import App

    client = turbine.Turbine(runtime, path_to_data_app)
    asyncio.run(App.run(client))

    if kwargs["command"] == "functions":
        asyncio.run(client.list_functions())
    elif kwargs["command"] == "hasFunctions":
        asyncio.run(client.has_functions())
