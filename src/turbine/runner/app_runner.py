import asyncio
import os
import sys
from turbine import turbine  
import pdb

def run_app_local(path_to_data_app: str,runtime: str, *args, **kwargs):
    sys.path.append(os.path.abspath(path_to_data_app))

    from main import App
    
    client = turbine.Turbine(runtime, path_to_data_app)
    asyncio.run(App.run(client))

    if kwargs['command'] == 'functions':
        list(path_to_data_app,runtime)


def list_functions(pathname: str, runtime: str, **kwargs):
    client = turbine.Turbine(runtime, pathname)
    asyncio.run(client.list_functions())

