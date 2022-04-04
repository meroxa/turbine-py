#!/usr/bin/env python3

import argparse
import json
import os
import shutil

_ROOT = os.path.abspath(os.path.dirname(__file__))

# Hacky work around to make sure the __pychache__ for turbine-py
# is not included in the copied files.
FILES_TO_IGNORE_ON_COPY = '__pycache__'


def generate_app(name: str, pathname: str):
    app_name = name or "my-app"

    app_location = os.path.join(pathname, app_name)

    template_directory = os.path.join(_ROOT, 'templates/python')

    try:
        shutil.copytree(template_directory, app_location,
                        ignore=shutil.ignore_patterns(FILES_TO_IGNORE_ON_COPY))

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


def build_parser():
    parser = argparse.ArgumentParser(
        prog="turbine",
        description="Command line utility for interacting with turbine-py",
    )

    # generate name pathname
    parser.add_argument('--generate', nargs=2, default=None,
                        metavar=('appName', 'appPath'),
                        help="Generate a turbine-py application")

    return parser


def main():
    parser = build_parser()
    arguments = vars(parser.parse_args())

    if arguments.get('generate') is not None:
        generate_app(*arguments.get('generate'))
        return


if __name__ == "__main__":
    main()
