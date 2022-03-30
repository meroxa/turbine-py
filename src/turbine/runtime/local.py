import json
import time
import typing as t

from pprint import pprint

from .types import AppConfig
from .types import Record, Resource
from .types import Records
from .types import Runtime

"""
Members in this module need to be updated to async.

"""


async def readFixtures(path: str, collection: str, resourceName: str):

    fixtures = []

    with open(path, "r") as content:
        fc = json.load(content)
        for rec in fc[collection]:
            fixtures.append(
                Record(
                    key=rec['key'],
                    value=rec['value'],
                    timestamp=time.time()
                )
            )

    pprint("=====================from {} resource=====================".format(
        resourceName))

    [pprint(fixture) for fixture in fixtures]

    return fixtures


class LocalResource(Resource):
    name = ""
    fixturesPath = ""

    def __init__(self, name: str, fixturesPath: str) -> None:
        self.name = name
        self.fixturesPath = fixturesPath

    async def records(self, collection: str) -> Records:
        return Records(
            records=await readFixtures(self.fixturesPath, collection, self.name),
            stream=""
        )

    async def write(self, rr: Records, collection: str) -> None:
        pprint(
            "=====================to {} resource=====================".format(
                self.name))

        for record in rr.records:
            pprint(record)

        return None


class LocalRuntime(Runtime):

    appConfig = {}
    pathToApp = ""

    def __init__(self, config: AppConfig, pathToApp: str) -> None:
        self.appConfig = config
        self.pathToApp = pathToApp

    async def resources(self, name: str):
        resources = self.appConfig.resources
        fixturesPath = resources[name]

        resourcedFixturePath = "{}/{}".format(
            self.pathToApp,
            fixturesPath
        )

        return LocalResource(name, resourcedFixturePath)

    async def process(self,
                      records: Records,
                      fn: t.Callable[[t.List[Record]], t.List[Record]]) -> Records:
        return fn(records)
