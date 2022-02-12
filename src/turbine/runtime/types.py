from abc import ABC, abstractmethod

import typing as t


class Record:
    def __init__(self, key: str, value: ..., timestamp: float):
        self.key = key
        self.value = value
        self.timestamp = timestamp


class Records:
    def __init__(self, records: t.List[Record], stream: str):
        self.records = records
        self.stream = stream


class Resource(ABC):
    @abstractmethod
    def records(collection: str) -> Records:
        ...

    @abstractmethod
    def write(records: Records, collection: str) -> None:
        ...


class Runtime(ABC):

    @abstractmethod
    def resources(name: str):
        ...

    @abstractmethod
    def process(
            records: Records,
            fn: t.Callable[[t.List[Record]], t.List[Record]]) -> Records:
        ...
