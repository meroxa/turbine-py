import argparse
from .runner import generate_app, run_app

# Hacky work around to make sure the __pychache__ for turbine-py
# is not included in the copied files.

def build_parser():
    parser = argparse.ArgumentParser(
        prog="turbine-py",
        description="Command line utility for interacting with the meroxa platform",
    )

    subparser = parser.add_subparsers(dest="command")
    # meroxa apps init
    generate = subparser.add_parser("generate")
    generate.add_argument("name", help="desired name of application")
    generate.add_argument("pathname", help="desired location of application")
    generate.set_defaults(func=generate_app)
    # meroxa apps run
    generate = subparser.add_parser("run")
    generate.add_argument(
        "runtime", default="local", help="select local or platform runtime"
    )
    generate.add_argument("path_to_data_app", help="path to app to run")
    generate.add_argument(
        "image_name", help="Docker image name", default="", nargs="?", const="const"
    )

    generate.set_defaults(func=run_app)
    # meroxa functions
    # list  application functions
    generate = subparser.add_parser("functions")
    generate.add_argument(
        "runtime", default="local", help="select local or platform runtime"
    )
    generate.add_argument("path_to_data_app", help="path to app")
    generate.set_defaults(func=run_app)
    # meroxa functions
    # check if application has functions
    generate = subparser.add_parser("hasFunctions")
    generate.add_argument(
        "runtime", default="local", help="select local or platform runtime"
    )
    generate.add_argument("path_to_data_app", help="path to app")
    generate.set_defaults(func=run_app)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(**vars(args))


if __name__ == "__main__":
    main()
