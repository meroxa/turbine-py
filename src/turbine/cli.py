#!/usr/bin/env python3

import argparse
import imp
import json
import os
from posixpath import dirname
import shutil
from .runner import *



# Hacky work around to make sure the __pychache__ for turbine-py
# is not included in the copied files.
FILES_TO_IGNORE_ON_COPY = "__pycache__"


def run_app_platform(*args, **kwargs):
    raise NotImplementedError


def build_parser():
    parser = argparse.ArgumentParser(
        prog="turbine-py",
        description="Command line utility for interacting with the meroxa platform",
    )

    subparser = parser.add_subparsers(dest = "command")

    # meroxa apps init
    generate = subparser.add_parser("generate")
    generate.add_argument("name", help="desired name of application")
    generate.add_argument("pathname", help="desired location of application")
    generate.add_argument("ignore_files", help="files to ignore on generate", default=FILES_TO_IGNORE_ON_COPY)
    generate.set_defaults(func=generate_app)

    # meroxa apps run
    # Run using local runtime
    generate = subparser.add_parser("run")
    generate.add_argument("runtime", default = "local", help="select local or platform runtime")
    generate.add_argument("path_to_data_app", help="path to app to run")
    generate.set_defaults(func=run_app_local)

    #meroxa functions 
    #list  application functions 
    generate = subparser.add_parser("functions")
    generate.add_argument("runtime", default = "local", help="select local or platform runtime")
    generate.add_argument("path_to_data_app", help="path to app ")
    generate.set_defaults(func=run_app_local)
    
    #meroxa functions 
    #check if application has functions 
    generate = subparser.add_parser("hasFunctions")
    generate.add_argument("runtime", default = "local", help="select local or platform runtime")
    generate.add_argument("path_to_data_app", help="path to app ")
    generate.set_defaults(func=run_app_local)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(**vars(args))


if __name__ == "__main__":
    main()
