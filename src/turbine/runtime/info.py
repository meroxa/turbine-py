import typing as t

from .types import AppConfig
from .types import Record, Resource
from .types import Records
from .types import Runtime


class InfoResource(Resource):
    async def records(self, collection: str) -> None:
        ...

    async def write(self, rr: Records, collection: str, config: dict[str, str] = {}) -> None:
        ...


class InfoRuntime(Runtime):
    appConfig = {}
    pathToApp = ""
    registeredFunctions: dict[str, t.Callable[[t.List[Record]], t.List[Record]]] = {}

    def __init__(self, config: AppConfig, path_to_app: str) -> None:
        self.appConfig = config
        self.pathToApp = path_to_app

    def functions_list(self) -> str:
        return f"turbine-response: {list(self.registeredFunctions)}"

    def has_functions(self) -> str:
        return f"turbine-response: {bool(len(list(self.registeredFunctions)))}"

    async def resources(self, name: str):
        return InfoResource()

    async def process(
        self,
        records: Records,
        fn: t.Callable[[t.List[Record]], t.List[Record]],
        env_vars=None,
    ) -> None:
        self.registeredFunctions[getattr(fn, "__name__", "Unknown")] = fn
