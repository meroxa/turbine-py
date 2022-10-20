import json
import typing as t

from .types import AppConfig
from .types import Record
from .types import Records
from .types import Resource
from .types import Runtime


class InfoResource(Resource):
    def __init__(self, name: str):
        self.name = name
        self.source = False
        self.destination = False
        self.collection = ""

    async def records(self, collection: str, config: dict[str, str] = None):
        self.source = True
        self.collection = collection
        self.destination = self.destination

    async def write(self, rr: Records, collection: str, config: dict[str, str] = None):

        self.destination = True
        self.source = self.source
        self.collection = collection


class InfoRuntime(Runtime):
    appConfig = {}
    pathToApp = ""
    registeredFunctions: dict[str, t.Callable[[t.List[Record]], t.List[Record]]] = {}
    registeredResources: list[Resource] = []

    def __init__(self, config: AppConfig, path_to_app: str) -> None:
        self.appConfig = config
        self.pathToApp = path_to_app

    def functions_list(self) -> str:
        return f"turbine-response: {list(self.registeredFunctions)}"

    def has_functions(self) -> str:
        return f"turbine-response: {bool(len(list(self.registeredFunctions)))}"

    def resources_list(self) -> str:
        resp = json.dumps(
            list(resource.__dict__ for resource in self.registeredResources)
        )
        return f"turbine-response: {resp}"

    async def resources(self, name: str):
        resource = InfoResource(name)
        self.registeredResources.append(resource)
        return resource

    async def process(
        self, records: Records, fn: t.Callable[[t.List[Record]], t.List[Record]]
    ) -> None:
        self.registeredFunctions[getattr(fn, "__name__", "Unknown")] = fn
