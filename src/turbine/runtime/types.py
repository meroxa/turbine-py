import typing as t

from abc import ABC, abstractmethod


class Record:
    def __init__(self, key: str, value: ..., timestamp: float):
        self.key = key
        self.value = value
        self.timestamp = timestamp

    def __repr__(self):
        from pprint import pformat
        return pformat(vars(self), indent=4, width=1)


class Records:
    records = []
    stream = ""

    def __init__(self, records: t.List[Record], stream: str):
        self.records = records
        self.stream = stream

    def __repr__(self):
        from pprint import pformat
        return pformat(vars(self), indent=4, width=1)


class Resource(ABC):
    @abstractmethod
    def records(collection: str) -> Records:
        ...

    @abstractmethod
    def write(records: Records, collection: str) -> None:
        ...


class Runtime(ABC):

    def resources(name: str):
        ...

    def process(
            records: Records,
            fn: t.Callable[[t.List[Record]], t.List[Record]]) -> Records:
        ...


class AppConfig:
    def __init__(
            self,
            name: str,
            language: str,
            environment: str,
            pipeline: str,
            resources: dict) -> None:
        self.name = name
        self.language = language
        self.environment = environment
        self.pipeline = pipeline
        self.resources = resources


class ClientOptions:
    def __init__(self, auth: str, url: str) -> None:
        self.auth = auth
        self.url = url
