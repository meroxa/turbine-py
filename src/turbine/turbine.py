import abc

from .runtime import Runtime
from .runtime import LocalRuntime
from .runtime import AppConfig
from .runtime import Record, Records

import typing as t

class Turbine(Runtime):

    runtime = None

    def __init__(self, config: AppConfig, pathToApp: str, is_local: bool) -> None:

        self.runtime = (LocalRuntime(config=config, pathToApp=pathToApp) if is_local
                else LocalRuntime(config=config, pathToApp=pathToApp))

    
    @abc.abstractmethod
    def process(
            records: Records,
            fn: t.Callable[[t.List[Record]], t.List[Record]]) -> Records:
        ...
