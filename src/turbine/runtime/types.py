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
    def records(self, collection: str, config: dict[str, str] = None) -> Records:
        ...

    @abstractmethod
    def write(self, records: Records, collection: str) -> None:
        ...


class Runtime(ABC):
    async def resources(self, name: str):
        ...

    async def process(
        self, records: Records, fn: t.Callable[[t.List[Record]], t.List[Record]]
    ) -> Records:
        ...

    def register_secrets(self, name: str) -> None:
        ...


class AppConfig:
    def __init__(
        self, name: str, language: str, resources: dict, environment=None
    ) -> None:
        self.name = name
        self.language = language
        self.resources = resources
        self.environment = environment


class ClientOptions:
    def __init__(self, auth: str, url: str) -> None:
        self.auth = auth
        self.url = url
