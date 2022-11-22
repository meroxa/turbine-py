from importlib.metadata import distribution
from unittest.mock import patch

from turbine.cli import build_parser

APP_NAME = "app_name"
PATH_TO_APP = "path/to/app"
PATH_TO_TEMP = "path/to/temp"
IMAGE_NAME = "image"
GIT_SHA = "d1342f0915946464fb04f29fa246308f7e664c13"
SPEC = "latest"
VERSION = distribution("turbine-py").version


class TestCli:
    @patch("turbine.cli.Runner")
    @patch("turbine.cli.asyncio")
    def test_app_run_test(self, mock_async, mock_runner):
        parser = build_parser()
        args = parser.parse_args(["run", PATH_TO_APP, APP_NAME])
        args.func(**vars(args))

        mock_runner.assert_called_with(PATH_TO_APP, APP_NAME)
        mock_async.run.assert_called_with(mock_runner().run_app_local())

    @patch("turbine.cli.Runner")
    @patch("turbine.cli.asyncio")
    def test_app_run_platform(self, mock_async, mock_runner):
        parser = build_parser()
        args = parser.parse_args(
            ["clideploy", PATH_TO_APP, IMAGE_NAME, APP_NAME, GIT_SHA]
        )
        args.func(**vars(args))

        mock_runner.assert_called_with(PATH_TO_APP, APP_NAME)
        mock_async.run.assert_called_with(
            mock_runner().run_app_platform(IMAGE_NAME, GIT_SHA)
        )

    @patch("turbine.cli.Runner")
    @patch("turbine.cli.asyncio")
    def test_app_run_platform_v2(self, mock_async, mock_runner):
        parser = build_parser()
        args = parser.parse_args(
            ["clideploy", PATH_TO_APP, IMAGE_NAME, APP_NAME, GIT_SHA, SPEC]
        )
        args.func(**vars(args))

        mock_runner.assert_called_with(PATH_TO_APP, APP_NAME)
        mock_async.run.assert_called_with(
            mock_runner().run_app_platform_v2(IMAGE_NAME, GIT_SHA, VERSION, SPEC)
        )

    @patch("turbine.cli.Runner")
    @patch("turbine.cli.asyncio")
    def test_app_list_functions(self, mock_async, mock_runner):
        parser = build_parser()
        args = parser.parse_args(["functions", PATH_TO_APP])
        args.func(**vars(args))

        mock_runner.assert_called_with(PATH_TO_APP)
        mock_async.run.assert_called_with(mock_runner().list_functions())

    @patch("turbine.cli.Runner")
    @patch("turbine.cli.asyncio")
    def test_app_has_functions(self, mock_async, mock_runner):
        parser = build_parser()
        args = parser.parse_args(["hasFunctions", PATH_TO_APP])
        args.func(**vars(args))

        mock_runner.assert_called_with(PATH_TO_APP)
        mock_async.run.assert_called_with(mock_runner().has_functions())

    @patch("turbine.cli.Runner")
    @patch("turbine.cli.asyncio")
    def test_app_list_resources(self, mock_async, mock_runner):
        parser = build_parser()
        args = parser.parse_args(["listResources", PATH_TO_APP])
        args.func(**vars(args))

        mock_runner.assert_called_with(PATH_TO_APP)
        mock_async.run.assert_called_with(mock_runner().list_resources())

    @patch("turbine.cli.Runner")
    @patch("turbine.cli.asyncio")
    def test_app_build(self, mock_async, mock_runner):
        parser = build_parser()
        args = parser.parse_args(["clibuild", PATH_TO_APP])
        args.func(**vars(args))

        mock_runner.assert_called_with(PATH_TO_APP)
        mock_async.run.assert_called_with(mock_runner().build_function())

    @patch("turbine.cli.Runner")
    def test_clean(self, mock_runner):
        parser = build_parser()
        args = parser.parse_args(["cliclean", PATH_TO_TEMP])
        args.func(**vars(args))

        mock_runner.clean_temp_directory.assert_called_with(PATH_TO_TEMP)

    def test_return_version(self, capsys):
        parser = build_parser()
        args = parser.parse_args(["version", PATH_TO_TEMP])
        args.func(**vars(args))

        output = capsys.readouterr()
        assert output.out.strip("\n") == f"turbine-response: {VERSION}"
