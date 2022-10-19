import logging
import typing as t
from abc import ABC
from abc import abstractmethod
from collections import UserList

logging.basicConfig()


class Record:
    def __init__(self, key: str, value: ..., timestamp: float):
        self.key = key
        self.value = value
        self.timestamp = timestamp

    def __repr__(self):
        from pprint import pformat

        return pformat(vars(self), indent=4, width=1)

    @property
    def is_json_schema(self):
        return all(x in self.value for x in ("payload", "schema"))

    @property
    def is_cdc_format(self):
        return self.is_json_schema and bool(self.value.get("payload").get("source"))

    def unwrap(self) -> None:
        if self.is_cdc_format:
            payload = self.value["payload"]

            try:
                schema_fields = self.value["schema"]["fields"]
                after_field = next(sf for sf in schema_fields if sf["field"] == "after")

                del after_field["field"]
                after_field["name"] = self.value["schema"]["name"]
                self.value["schema"] = after_field
            except (StopIteration or KeyError) as e:
                logging.error(f"CDC envelope is malformed: {e}")

            self.value["payload"] = payload["after"]


class RecordList(UserList):
    def unwrap(self):
        [rec.unwrap() for rec in self.data]


class Records:
    records: RecordList = None
    stream = ""

    def __init__(self, records: RecordList, stream: str):
        self.records = records
        self.stream = stream

    def __repr__(self):
        from pprint import pformat

        return pformat(vars(self), indent=4, width=1)

    def unwrap(self):
        [rec.unwrap() for rec in self.records.data]


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
        self, records: Records, fn: t.Callable[[RecordList], RecordList]
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
        self.git_sha = None


class ClientOptions:
    def __init__(self, auth: str, url: str, meroxa_account_uuid: str) -> None:
        self.auth = auth
        self.url = url
        self.meroxa_account_uuid = meroxa_account_uuid
