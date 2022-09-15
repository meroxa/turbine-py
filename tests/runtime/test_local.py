import pytest

from turbine.runtime import AppConfig
from turbine.runtime import LocalResource
from turbine.runtime import LocalRuntime
from turbine.runtime import Record
from turbine.runtime import read_fixtures
from turbine.runtime.types import RecordList


@pytest.fixture()
def local_runtime():
    return LocalRuntime(
        config=AppConfig(name="APP_NAME", language="py", resources={}),
        path_to_app="path_to_app",
    )


@pytest.fixture(autouse=True)
def reset(local_runtime):
    local_runtime._registered_functions = []
    local_runtime._secrets = {}


FIXTURES_PATH = "tests/utils/template-records.json"


class TestReadFixtures:
    @pytest.mark.asyncio
    async def test_read_fixtures_error(self):
        with pytest.raises(Exception):
            await read_fixtures(path="fake/path", collection="fake")

    @pytest.mark.asyncio
    async def test_read_fixtures_success(self):
        fixtures = await read_fixtures(path=FIXTURES_PATH, collection="user_activity")

        assert len(fixtures) == 3
        assert isinstance(fixtures[1], Record)


class TestLocalResource:
    @pytest.mark.asyncio
    async def test_records(self):
        resource = LocalResource(name="name", fixtures_path=FIXTURES_PATH)

        records = await resource.records(collection="user_activity", config=None)

        assert records.records is not None
        assert len(records.records.data) == 3

    @pytest.mark.asyncio
    async def test_write(self, capsys):
        resource = LocalResource(name="name", fixtures_path=FIXTURES_PATH)

        records = await resource.records(collection="user_activity", config=None)

        await resource.write(rr=records, collection="user_activity")

        capture = capsys.readouterr()

        assert capture.out is not None
        assert capture.err == ""


class TestLocalRuntime:
    @pytest.mark.asyncio
    async def test_resources_no_fixtures_path(self, local_runtime):
        lr = await local_runtime.resources("test")

        assert lr.name == "test"
        assert lr.fixtures_path is None

    @pytest.mark.asyncio
    async def test_resources_fixtures_path(self, local_runtime):
        local_runtime.app_config.resources = {"test": FIXTURES_PATH}
        lr = await local_runtime.resources("test")

        assert lr.name == "test"
        assert lr.fixtures_path == f"{local_runtime.path_to_app}/{FIXTURES_PATH}"

    @pytest.mark.asyncio
    async def test_process(self, local_runtime):
        def test_func(x: RecordList):
            return x

        resource = LocalResource(name="name", fixtures_path=FIXTURES_PATH)

        records = await resource.records(collection="user_activity", config=None)

        results = await local_runtime.process(records, test_func)

        assert len(results.records) == 3
        assert len(local_runtime._registeredFunctions) == 1
        assert local_runtime._registeredFunctions.get(test_func.__name__) == test_func

    def test_register_secrets(self, local_runtime, monkeypatch):
        monkeypatch.setenv("TEST", "testvalue")
        monkeypatch.setenv("TEST2", "testvalue2")
        monkeypatch.setenv("TEST3", "testvalue3")

        local_runtime.register_secrets("TEST")
        local_runtime.register_secrets("TEST2")
        local_runtime.register_secrets("TEST3")

        assert (
            local_runtime._secrets.items()
            <= dict(TEST="testvalue", TEST2="testvalue2", TEST3="testvalue3").items()
        )
