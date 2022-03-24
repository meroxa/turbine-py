#!/usr/bin/env python3

import argparse
import shutil
import json
import os


_ROOT = os.path.abspath(os.path.dirname(__file__))

# Hacky work around to make sure the __pychache__ for turbine-py
# is not incldued in the copied files.
FILES_TO_IGNORE_ON_COPY = '__pycache__'


def generate_app(name: str, pathname: str):
    app_name = name or "my-app"

    app_location = os.path.join(pathname, app_name)

    template_directory = os.path.join(_ROOT, 'templates/python')

    try:
        dest_directory = shutil.copytree(
            template_directory, app_location,
            ignore=shutil.ignore_patterns(FILES_TO_IGNORE_ON_COPY))

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
        with open(app_name + '/app.json', 'w', encoding='utf-8') as fp:
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
