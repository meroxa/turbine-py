#!/usr/bin/env python3

import argparse
import json
import os
import shutil

_ROOT = os.path.abspath(os.path.dirname(__file__))

# Hacky work around to make sure the __pychache__ for turbine-py
# is not included in the copied files.
FILES_TO_IGNORE_ON_COPY = '__pycache__'


def run_app_local(*args, **kwargs):
    raise NotImplementedError


def run_app_platform(*args, **kwargs):
    raise NotImplementedError


def generate_app(name: str, pathname: str, **kwargs):
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
        prog="turbine-py",
        description="Command line utility for interacting with the meroxa platform",
    )

    subparser = parser.add_subparsers()

    # meroxa apps init
    generate = subparser.add_parser("generate")
    generate.add_argument("name", help="desired name of application")
    generate.add_argument("pathname", help="desired location of application")
    generate.set_defaults(func=generate_app)

    # meroxa apps run 
    # Run using local runtime
    generate = subparser.add_parser("run")
    generate.add_argument("app_path", help="path to app to run")
    generate.set_defaults(func=run_app_local)

    # meroxa apps deploy 
    # Run using platform runtime
    generate = subparser.add_parser("deploy")
    generate.add_argument("app_path", help="path to app to run")
    generate.set_defaults(func=run_app_local)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(**vars(args))


if __name__ == "__main__":
    main()
