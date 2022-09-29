import json
import os
import shutil

_ROOT = os.path.abspath(os.path.dirname(__file__))

FILES_TO_IGNORE_ON_COPY = "__pycache__"


def generate_app(name: str, pathname: str, **kwargs):
    app_name = name or "my-app"

    app_location = os.path.join(pathname, app_name)

    template_directory = os.path.join(_ROOT, "../", "templates/python")

    try:
        shutil.copytree(
            template_directory,
            app_location,
            ignore=shutil.ignore_patterns(FILES_TO_IGNORE_ON_COPY),
        )

        generate_app_json(name, pathname)
    except Exception as e:
        print(e)
        raise


def generate_app_json(name: str, pathname: str):
    app_json = dict(
        name=name,
        language="python",
        resources=dict(source_name="fixtures/demo-cdc.json"),
    )

    app_location = os.path.join(pathname, name)
    try:
        with open(app_location + "/app.json", "w", encoding="utf-8") as fp:
            json.dump(app_json, fp, ensure_ascii=False, indent=4)
    except Exception as e:
        print(e)
