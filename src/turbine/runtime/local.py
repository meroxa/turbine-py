import json
import os
import time
import typing as t
from pprint import pprint

from .types import AppConfig
from .types import Record
from .types import RecordList
from .types import Records
from .types import Resource
from .types import Runtime


async def read_fixtures(path: str, collection: str):
    fixtures = []
    try:
        with open(path, "r") as content:
            fc = json.load(content)

            if collection in fc:
                for rec in fc[collection]:
                    fixtures.append(
                        Record(
                            key=rec["key"], value=rec["value"], timestamp=time.time()
                        )
                    )
    except FileNotFoundError:
        raise Exception(
            f"{path} not found: must specify fixtures path to data for"
            f" source resources in order to run locally"
        )

    return fixtures


class LocalResource(Resource):
    name = ""
    fixtures_path = ""

    def __init__(self, name: str, fixtures_path: str) -> None:
        self.name = name
        self.fixtures_path = fixtures_path

    async def records(self, collection: str, config: dict[str, str] = None) -> Records:
        return Records(
            records=RecordList(await read_fixtures(self.fixtures_path, collection)),
            stream="",
        )

    async def write(
        self, rr: Records, collection: str, config: dict[str, str] = None
    ) -> None:

        pprint(f"===================to {self.name} resource===================")

        if rr.records:
            [print(json.dumps(record.value, indent=4)) for record in rr.records]
        print(f"{len(rr.records)} records written")

        return None


class LocalRuntime(Runtime):
    app_config = {}
    path_to_app = ""
    _registeredFunctions = {}
    _secrets = {}

    def __init__(self, config: AppConfig, path_to_app: str) -> None:
        self.app_config = config
        self.path_to_app = path_to_app

    async def resources(self, name: str):
        resourced_fixture_path = None
        resources = self.app_config.resources

        fixtures_path = resources.get(name)
        if fixtures_path:
            resourced_fixture_path = f"{self.path_to_app}/{fixtures_path}"

        return LocalResource(name, resourced_fixture_path)

    async def process(
        self, records: Records, fn: t.Callable[[RecordList], RecordList]
    ) -> Records:
        self._registeredFunctions[fn.__name__] = fn
        return Records(records=RecordList(fn(records.records)), stream="")

    def register_secrets(self, name: str) -> None:

        sec = os.getenv(name)
        if not sec:
            raise Exception(f"Secret invalid or unset: {name}")

        self._secrets.update({name: sec})
