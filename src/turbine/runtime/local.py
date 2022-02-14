from .types import AppConfig
from .types import Record, Resource
from .types import Records
from .types import Runtime

import typing as t

import time

import pprint


def readFixtures(path: str, collection: str, resourceName: str):

    fixtures = []

    with open(path, "r") as content:
        fc = json.load(content)
        for rec in fc[collection]:
            fixtures.append(
                Record(
                    key = rec['key'],
                    value= rec['value'],
                    timestamp= time.time()
                )
            )
    
    pprint("=====================from ${resourceName} resource=====================".format(resourceName))

    [ pprint( fixture ) for fixture in fixtures ]

    return fixtures

class LocalResource(Resource):
    name = ""
    fixturesPath = "" 

    def __init__(self, name: str, fixturesPath: str) -> None:
        self.name = name
        self.fixturesPath = fixturesPath

    def records(self, collection: str) -> Records:
        return readFixtures(self.fixturesPath, collection, self.name)

    def write(records: Records, collection: str) -> None:
        return None


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


