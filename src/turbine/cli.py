import argparse
import asyncio

from .runner import generate_app, Runner


def app_run_test(path_to_data_app, **kwargs):
    r = Runner(path_to_data_app)
    asyncio.run(r.run_app_local())


def app_run_platform(path_to_data_app, image_name, **kwargs):
    r = Runner(path_to_data_app)
    asyncio.run(r.run_app_platform(image_name))


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
    run.add_argument("path_to_data_app", help="path to app ")
    run.set_defaults(func=app_run_test)

    # meroxa apps deploy
    clideploy = subparser.add_parser("clideploy")
    clideploy.add_argument("path_to_data_app", help="path to app to run")
    clideploy.add_argument(
        "image_name", help="Docker image name", default="", nargs="?", const="const"
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

    # "build" the application
    clibuild = subparser.add_parser("clibuild")
    clibuild.add_argument("path_to_data_app", help="path to app ")
    clibuild.set_defaults(func=app_build)

    # "clean" the application
    cliclean = subparser.add_parser("cliclean")
    cliclean.add_argument("path_to_temp", help="path to temp directory ")
    cliclean.set_defaults(func=app_clean_up)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(**vars(args))


if __name__ == "__main__":
    main()
