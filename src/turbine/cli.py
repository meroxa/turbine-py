import argparse
import asyncio
from importlib.metadata import distribution

from .runner import generate_app
from .runner import Runner


def app_run_test(app_name, path_to_data_app, **kwargs):
    r = Runner(path_to_data_app, app_name)
    asyncio.run(r.run_app_local())


def app_run_platform(app_name, path_to_data_app, image_name, git_sha, **kwargs):
    r = Runner(path_to_data_app, app_name)
    spec = kwargs.get("spec")
    if spec:
        dist = distribution("turbine-py")
        asyncio.run(
            r.run_app_platform_v2(image_name, git_sha.strip(), dist.version, spec)
        )
    else:
        asyncio.run(r.run_app_platform(image_name, git_sha))


def app_list_resources(path_to_data_app, **kwargs):
    r = Runner(path_to_data_app)
    print(asyncio.run(r.list_resources()))


def app_list_functions(path_to_data_app, **kwargs):
    r = Runner(path_to_data_app)
    print(asyncio.run(r.list_functions()))


def app_has_functions(path_to_data_app, **kwargs):
    r = Runner(path_to_data_app)
    print(asyncio.run(r.has_functions()))


def app_build(path_to_data_app, **kwargs):
    r = Runner(path_to_data_app)
    print(asyncio.run(r.build_function()))


def app_clean_up(path_to_temp, **kwargs):
    Runner.clean_temp_directory(path_to_temp)


def app_return_version(path_to_data_app, **kwargs):
    dist = distribution("turbine-py")
    print(f"turbine-response: {dist.version}")


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
    run = subparser.add_parser("run")
    run.add_argument("path_to_data_app", help="path to app")
    run.add_argument(
        "app_name",
        help="desired name of application",
        nargs="?",
    )
    run.set_defaults(func=app_run_test)

    # meroxa apps deploy
    clideploy = subparser.add_parser("clideploy")
    clideploy.add_argument("path_to_data_app", help="path to app to run")
    clideploy.add_argument(
        "image_name",
        help="Docker image name",
    )
    clideploy.add_argument(
        "app_name",
        help="desired name of application",
    )
    clideploy.add_argument(
        "git_sha",
        help="The SHA of the current git commit of the app",
    )
    clideploy.add_argument(
        "spec",
        help="Spec version to use during deploy",
        nargs="?",
    )
    clideploy.set_defaults(func=app_run_platform)

    # meroxa apps build
    list_functions = subparser.add_parser("functions")
    list_functions.add_argument("path_to_data_app", help="path to app ")
    list_functions.set_defaults(func=app_list_functions)

    # check if application has functions
    has_functions = subparser.add_parser("hasFunctions")
    has_functions.add_argument("path_to_data_app", help="path to app ")
    has_functions.set_defaults(func=app_has_functions)

    # list resources used by this application
    list_resources = subparser.add_parser("listResources")
    list_resources.add_argument("path_to_data_app", help="path to app ")
    list_resources.set_defaults(func=app_list_resources)

    # "build" the application
    clibuild = subparser.add_parser("clibuild")
    clibuild.add_argument("path_to_data_app", help="path to app ")
    clibuild.set_defaults(func=app_build)

    # "clean" the application
    cliclean = subparser.add_parser("cliclean")
    cliclean.add_argument("path_to_temp", help="path to temp directory ")
    cliclean.set_defaults(func=app_clean_up)

    # return the current version of turbine-py
    lib_version = subparser.add_parser("version")
    lib_version.add_argument("path_to_data_app", help="path to app ", nargs="?")
    lib_version.set_defaults(func=app_return_version)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(**vars(args))


if __name__ == "__main__":
    main()
