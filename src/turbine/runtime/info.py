import typing as t

from .types import AppConfig
from .types import Record, Resource
from .types import Records
from .types import Runtime


class InfoResource(Resource):
    async def records(self, collection: str, config: dict[str, str] = None) -> None:
        ...

    async def write(
        self, rr: Records, collection: str, config: dict[str, str] = {}
    ) -> None:
        ...


class InfoRuntime(Runtime):
    appConfig = {}
    pathToApp = ""
    registeredFunctions: dict[str, t.Callable[[t.List[Record]], t.List[Record]]] = {}
    registeredResources: list[str] = []

    def __init__(self, config: AppConfig, path_to_app: str) -> None:
        self.appConfig = config
        self.pathToApp = path_to_app

    def functions_list(self) -> str:
        return f"turbine-response: {list(self.registeredFunctions)}"

    def has_functions(self) -> str:
        return f"turbine-response: {bool(len(list(self.registeredFunctions)))}"

    def resources_list(self) -> str:
        return f"turbine-response: {self.registeredResources}"

    async def resources(self, name: str):
        self.registeredResources.append(name)
        return InfoResource()

    async def process(
        self, records: Records, fn: t.Callable[[t.List[Record]], t.List[Record]]
    ) -> None:
        self.registeredFunctions[getattr(fn, "__name__", "Unknown")] = fn
