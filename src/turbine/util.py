import pathlib
import shutil
import json
import sys
import os

from pathlib import PurePath


def generate_app(name: str, pathname: str):
    # Determine app name and directory
    app_name = name or "my-app"

    print(sys.argv[0])
    print(os.path.split(os.path.abspath(os.path.realpath(sys.argv[0])))[0])

    # construct templates path
    template_directory = pathlib.Path(sys.argv[0] + "/../templates").resolve()

    pwd = pathlib.Path(sys.argv[0]).resolve()
    templates = pathlib.Path('../templates').resolve()
    template_directory = pwd / templates


    # Copy stuff in templates to chosen location
    try:
        # Copy tree from src = template_directory to dest = chosen
        dest_directory = shutil.copytree(template_directory, pathname)

        # Write the app.json file into the directory
        generate_app_json(pathname)
    except Exception as e:
        print(e)
        raise
        

    print("Application successfully initialized!")
    print("You can start interacting with Meroxa in your app located at {}"
          .format(dest_directory))


def generate_app_json(app_name: str):

    app_json = dict(name=app_name, language="python")

    try:
        with open(app_name + '/app.json', 'w') as fp:
            json.dumps(app_json, fp)
    except Exception as e:
        print(e)
