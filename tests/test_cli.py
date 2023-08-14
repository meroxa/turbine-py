from importlib.metadata import distribution
from unittest.mock import patch

from turbine.cli import build_parser

APP_NAME = "app_name"
FUNCTION_NAME = "python_app"
PATH_TO_APP = "path/to/app"
PATH_TO_TEMP = "path/to/temp"
IMAGE_NAME = "image"
GIT_SHA = "d1342f0915946464fb04f29fa246308f7e664c13"
SPEC = "latest"
VERSION = distribution("turbine-py").version


class TestCli:
    @patch("turbine.cli.TurbineClient")
    @patch("turbine.cli.asyncio")
    def test_app_run_test(self, mock_async, mock_runner):
        parser = build_parser()
        args = parser.parse_args(["run", PATH_TO_APP, GIT_SHA])
        args.func(**vars(args))

        mock_runner.assert_called_with(PATH_TO_APP)
        mock_async.run.assert_called_with(mock_runner().run())

    @patch("turbine.cli.TurbineClient")
    @patch("turbine.cli.asyncio")
    def test_app_records_test(self, mock_async, mock_runner):
        parser = build_parser()
        args = parser.parse_args(["record", PATH_TO_APP, GIT_SHA])
        args.func(**vars(args))

        mock_runner.assert_called_with(PATH_TO_APP)
        mock_async.run.assert_called_with(mock_runner().records())

    @patch("turbine.cli.TurbineClient")
    @patch("turbine.cli.asyncio")
    def test_app_build_test(self, mock_async, mock_runner):
        parser = build_parser()
        args = parser.parse_args(["build", PATH_TO_APP])
        args.func(**vars(args))

        mock_runner.assert_called_with(PATH_TO_APP)
        mock_async.run.assert_called_with(mock_runner().build_function())

    def test_return_version(self, capsys):
        parser = build_parser()
        args = parser.parse_args(["version", PATH_TO_APP])
        args.func(**vars(args))

        output = capsys.readouterr()
        assert output.out.strip("\n") == f"turbine-response: {VERSION}"
