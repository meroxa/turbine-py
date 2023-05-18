import argparse
import asyncio
from .src.turbine_app import TurbineClient
from .src.function_deploy import serve
from importlib.metadata import distribution


def app_record(path_to_data_app, git_sha, **kwargs):
    t = TurbineClient(path_to_data_app)
    asyncio.run(t.records(git_sha))


def app_build(path_to_data_app, **kwargs):
    t = TurbineClient(path_to_data_app)
    asyncio.run(t.build_function())


def app_serve(function_name, **kwargs):
    asyncio.run(serve(function_name=function_name))


def app_run(path_to_data_app, git_sha, **kwargs):
    t = TurbineClient(path_to_data_app)
    asyncio.run(t.run(git_sha))


def app_version(path_to_data_app, **kwargs):
    dist = distribution("turbine-py")
    print(f"turbine-response: {dist.version}")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="turbine-py",
        description="Command line utility for interacting with the meroxa platform",
    )

    subparser = parser.add_subparsers(dest="command")

    # execute record command
    record = subparser.add_parser("record")
    record.add_argument("path_to_data_app", help="path to app")
    record.add_argument(
        "git_sha",
        help="The SHA of the current git commit of the app",
    )
    record.set_defaults(func=app_record)

    # execute build command
    build = subparser.add_parser("build")
    build.add_argument("path_to_data_app", help="path to app")
    build.set_defaults(func=app_build)

    # execute run command
    run = subparser.add_parser("run")
    run.add_argument("path_to_data_app", help="path to app")
    run.add_argument(
        "git_sha",
        help="The SHA of the current git commit of the app",
    )
    run.set_defaults(func=app_run)

    version = subparser.add_parser("version")
    version.add_argument("path_to_data_app", help="path to app ", nargs="?")
    version.set_defaults(func=app_version)

    serve = subparser.add_parser("serve")
    serve.add_argument("function_name", help="function name", nargs="?")
    serve.set_defaults(func=app_serve)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(**vars(args))


if __name__ == "__main__":
    main()
