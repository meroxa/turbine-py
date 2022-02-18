import typing as t

from .runtime import Runtime
from .runtime import LocalRuntime
from .runtime import AppConfig
from .runtime import Record, Records


class Turbine(Runtime):

    runtime = None

    def __init__(
            self,
            config: AppConfig,
            pathToApp: str,
            is_local: bool) -> None:

        if is_local:
            self.runtime = LocalRuntime(
                config=config,
                pathToApp=pathToApp)
        else:
            self.runtime = LocalRuntime(
                config=config,
                pathToApp=pathToApp)

    def resources(self, name: str):
        return self.runtime.resources(name)

    def process(
            self,
            records: Records,
            fn: t.Callable[[t.List[Record]], t.List[Record]]) -> Records:
        return self.runtime.process(records, fn)
