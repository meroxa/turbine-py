import argparse
import asyncio

from .src.turbine_app import TurbineClient

# from importlib.metadata import distribution


def app_record(git_sha, **kwargs):
    t = TurbineClient()
    asyncio.run(t.record(git_sha))


def app_build(path_to_data_app, **kwargs):
    pass


def app_run(git_sha, **kwargs):
    t = TurbineClient()
    asyncio.run(t.run(git_sha))


def build_parser():
    parser = argparse.ArgumentParser(
        prog="turbine-py",
        description="Command line utility for interacting with the meroxa platform",
    )

    subparser = parser.add_subparsers(dest="command")

    # execute record command
    record = subparser.add_parser("record")
    record.add_argument(
        "git_sha",
        help="The SHA of the current git commit of the app",
    )
    record.set_defaults(func=app_record)

    # execute build command
    build = subparser.add_parser("build")
    build.add_argument(
        "git_sha",
        help="The SHA of the current git commit of the app",
    )
    build.set_defaults(func=app_build)

    # execute run command
    run = subparser.add_parser("run")
    run.add_argument(
        "git_sha",
        help="The SHA of the current git commit of the app",
    )
    run.set_defaults(func=app_run)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(**vars(args))


if __name__ == "__main__":
    main()
