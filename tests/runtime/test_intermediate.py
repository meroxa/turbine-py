import json

import pytest

from turbine.runtime import AppConfig
from turbine.runtime import ClientOptions
from turbine.runtime import IntermediateFunction
from turbine.runtime import IntermediateResource
from turbine.runtime import IntermediateRuntime

from turbine.runtime.types import Records
from turbine.runtime.types import RecordList


@pytest.fixture(scope="function")
def intermediate_runtime():
    return IntermediateRuntime(
        client_options=ClientOptions(auth="TOKEN", url="URL"),
        image_name="IMAGE",
        git_sha="SHASHASHA",
        version="1.3.0",
        spec="latest",
        config=AppConfig(name="APP_NAME", language="py", resources={}),
    )


@pytest.fixture(autouse=True)
def reset(intermediate_runtime):
    intermediate_runtime._registered_resources = []
    intermediate_runtime._registered_functions = []
    intermediate_runtime._secrets = {}


@pytest.fixture
def record():
    return Records(records=RecordList(), stream="")


def intermediate_resource():
    return IntermediateRuntime


class TestIntermediateResource:
    @pytest.mark.asyncio
    async def test_records_errors_without_collection(self):
        resource = IntermediateResource(resource_name="no_collection")
        with pytest.raises(Exception):
            await resource.records(collection="", config={})

    @pytest.mark.asyncio
    async def test_records_errors_more_than_one_source(self):
        resource = IntermediateResource(resource_name="duplicate_source")
        await resource.records(collection="test_collection", config={})

        with pytest.raises(Exception):
            await resource.records(collection="test_collection", config={})

    @pytest.mark.asyncio
    async def test_records_success(self):
        test_config = {"test": "value"}
        resource = IntermediateResource(resource_name="database_UwU")
        await resource.records(collection="collection", config=test_config)

        assert resource.has_source is True
        assert isinstance(resource.config, dict)
        assert resource.config.items() <= test_config.items()
        assert resource.resource_type is "source"
        assert resource.collection is "collection"

    @pytest.mark.asyncio
    async def test_write_errors_without_collection(self):
        resource = IntermediateResource(resource_name="no_collection")
        with pytest.raises(Exception):
            await resource.write(records=None, collection="", config={})

    @pytest.mark.asyncio
    async def test_write_success(self):
        test_config = {"test": "value"}
        resource = IntermediateResource(resource_name="database_UwU")
        await resource.write(records=None, collection="collection", config=test_config)

        assert resource.has_source is False
        assert isinstance(resource.config, dict)
        assert resource.config.items() <= test_config.items()
        assert resource.resource_type is "destination"
        assert resource.collection is "collection"

    @pytest.mark.asyncio
    async def test_write_repr(self):
        test_config = {"test": "value"}
        resource = IntermediateResource(resource_name="database_UwU")
        await resource.write(records=None, collection="collection", config=test_config)

        res = resource.__repr__()
        assert (
            json.loads(res).items()
            <= {
                "type": "destination",
                "resource": "database_UwU",
                "collection": "collection",
                "config": test_config,
            }.items()
        )


class TestIntermediateFunction:
    def test_init(self):
        func = IntermediateFunction("funcname", "1234567890", "coolimage")

        assert func.name == "funcname-12345678"
        assert func.image == "coolimage"

    def test_repr(self):
        func = IntermediateFunction("funcname", "1234567890", "coolimage")
        res = func.__repr__()

        assert (
            json.loads(res).items()
            <= {"name": "funcname-12345678", "image": "coolimage"}.items()
        )


class TestIntermediateRuntime:
    def test_definition(self, intermediate_runtime):
        expected = {
            "app_name": "APP_NAME",
            "git_sha": "SHASHASHA",
            "metadata": {
                "turbine": {
                    "language": "py",
                    "version": "1.3.0",
                },
                "spec_version": "latest",
            },
        }

        res = intermediate_runtime.definition()

        assert res.items() <= expected.items()

    @pytest.mark.asyncio
    async def test_resources(self, intermediate_runtime):

        res1 = await intermediate_runtime.resources("test_resource")

        assert len(intermediate_runtime._registered_resources) == 1
        assert res1 in intermediate_runtime._registered_resources

        res2 = await intermediate_runtime.resources("test_resource_2")

        assert len(intermediate_runtime._registered_resources) == 2
        assert res2 in intermediate_runtime._registered_resources

    @pytest.mark.asyncio
    async def test_functions(self, intermediate_runtime, record):

        await intermediate_runtime.process(
            records=record,
            fn=lambda x: x,
        )

        rf = intermediate_runtime._registered_functions[0]
        assert len(intermediate_runtime._registered_functions) == 1
        assert rf.name == "<lambda>-SHASHASH"

    def test_register_secrets(self, intermediate_runtime, monkeypatch):
        monkeypatch.setenv("TEST", "testvalue")
        monkeypatch.setenv("TEST2", "testvalue2")
        monkeypatch.setenv("TEST3", "testvalue3")

        intermediate_runtime.register_secrets("TEST")

        assert (
            intermediate_runtime._secrets.items()
            <= dict(TEST="testvalue", TEST2="testvalue2", TEST3="testvalue3").items()
        )

    @pytest.mark.asyncio
    async def test_serialize(self, intermediate_runtime, record, monkeypatch):
        monkeypatch.setenv("ENV", "testvalue")

        expected_def = {
            "app_name": "APP_NAME",
            "git_sha": "SHASHASHA",
            "metadata": {
                "turbine": {
                    "language": "py",
                    "version": "1.3.0",
                },
                "spec_version": "latest",
            },
        }

        await intermediate_runtime.resources("test_resource")
        await intermediate_runtime.process(
            records=record,
            fn=lambda x: x,
        )
        intermediate_runtime.register_secrets("ENV")

        res = intermediate_runtime.serialize()
        assert len(res.get("connectors")) == 1
        assert len(res.get("functions")) == 1
        assert len(res.get("secrets")) == 1
        assert res.get("definition").items() <= expected_def.items()
