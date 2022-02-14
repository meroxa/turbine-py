import abc

from .runtime import Runtime
from .runtime import LocalRuntime
from .runtime import AppConfig

class Turbine(Runtime):
    def __init__(self, config: AppConfig, pathToApp: str, is_local: bool) -> Runtime:

        return (LocalRuntime(config=config, pathToApp=pathToApp) if is_local
                else LocalRuntime(config=config, pathToApp=pathToApp))

    # How to enforce this interface
    @abc.abstractmethod
    def function():
        ...
