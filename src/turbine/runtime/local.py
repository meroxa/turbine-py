import json
import time
import typing as t
from pprint import pprint

from .types import AppConfig
from .types import Record, Resource , RegisteredFunctions
from .types import Records
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
                            key=rec['key'],
                            value=rec['value'],
                            timestamp=time.time()
                        )
                    )
    except FileNotFoundError:
        print(
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

    async def records(self, collection: str) -> Records:
        return Records(
            records=await read_fixtures(self.fixtures_path, collection),
            stream=""
        )

    async def write(self, rr: Records, collection: str) -> None:

        pprint(f"===================to {self.name} resource===================")

        if rr.records:
            [print(json.dumps(record.value, indent=4)) for record in rr.records]
        print("{} records written".format(len(rr.records)))

        return None


class LocalRuntime(Runtime):
    appConfig = {}
    pathToApp = ""
    _registeredFunctions = {}

    def __init__(self, config: AppConfig, path_to_app: str) -> None:
        self.appConfig = config
        self.pathToApp = path_to_app

    async def resources(self, name: str):
        resourced_fixture_path = None
        resources = self.appConfig.resources

        fixtures_path = resources.get(name)
        if fixtures_path:
            resourced_fixture_path = f"{self.pathToApp}/{fixtures_path}"

        return LocalResource(name, resourced_fixture_path)

    async def process(self,
                      records: Records,
                      fn: t.Callable[[t.List[Record]], t.List[Record]],
                      env_vars=None) -> Records:
        self._registeredFunctions[fn.__name__] = fn
        return Records(
            records=fn(records.records),
            stream=""
        )

    async def list_functions(self):
        return print("List of application functions : \n {}".format("\n".join(self._registeredFunctions)))

    async def has_functions(self):
        if self._registeredFunctions:
            return True  
        return False 
       
