import asyncio
import os
import shutil
import sys
import json 
from turbine import turbine

_ROOT = os.path.abspath(os.path.dirname(__file__))


def generate_app(name: str, pathname: str, ignore_files: str, **kwargs):
    app_name = name or "my-app"

    app_location = os.path.join(pathname, app_name)

    template_directory = os.path.join(_ROOT, 'templates/python')

    try:
        shutil.copytree(template_directory, app_location,
                        ignore=shutil.ignore_patterns(ignore_files))

        generate_app_json(name, pathname)
    except Exception as e:
        print(e)
        raise


def generate_app_json(name: str, pathname: str):
    app_json = dict(
        name=name,
        language="python",
        resources=dict(
            source_name="fixtures/none.json"))

    app_location = os.path.join(pathname, name)
    try:
        with open(app_location + '/app.json', 'w', encoding='utf-8') as fp:
            json.dump(app_json, fp, ensure_ascii=False, indent=4)
    except Exception as e:
        print(e)