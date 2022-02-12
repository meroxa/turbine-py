
from importlib import resources

from .types import Record
from .types import Records
from .types import Runtime

import typing as t

class LocalResource

class LocalRuntime(Runtime):

    appConfig = {}
    pathToApp = ""

    def __init__(self, config: AppConfig, pathToApp: str) -> None:
        self.appConfig = config
        self.pathToApp = pathToApp

    def resources(self, name: str):
        resources = self.appConfig.resources
        fixturesPath = resources[name]

        resourcedFixturePath = "{pathToApp}/{fixturesPath}".format(
            self.pathToApp,
            fixturesPath
        )

        return LocalResource( name, resourcedFixturePath )

    def process(
            records: Records,
            fn: t.Callable[[t.List[Record]], t.List[Record]]) -> Records:

            processed = fn(records)

            return Records( processed, "")


