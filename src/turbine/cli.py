#!/usr/bin/env python3

import argparse

import turbine


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
        turbine.generate_app(*arguments.get('generate'))
        return


if __name__ == "__main__":
    main()
