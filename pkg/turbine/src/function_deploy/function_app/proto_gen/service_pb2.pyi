from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import (
    ClassVar as _ClassVar,
    Iterable as _Iterable,
    Mapping as _Mapping,
    Optional as _Optional,
    Union as _Union,
)

DESCRIPTOR: _descriptor.FileDescriptor

class ProcessRecordRequest(_message.Message):
    __slots__ = ["records"]
    RECORDS_FIELD_NUMBER: _ClassVar[int]
    records: _containers.RepeatedCompositeFieldContainer[Record]
    def __init__(
        self, records: _Optional[_Iterable[_Union[Record, _Mapping]]] = ...
    ) -> None: ...

class ProcessRecordResponse(_message.Message):
    __slots__ = ["records"]
    RECORDS_FIELD_NUMBER: _ClassVar[int]
    records: _containers.RepeatedCompositeFieldContainer[Record]
    def __init__(
        self, records: _Optional[_Iterable[_Union[Record, _Mapping]]] = ...
    ) -> None: ...

class Record(_message.Message):
    __slots__ = ["key", "timestamp", "value"]
    KEY_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: str
    timestamp: int
    value: str
    def __init__(
        self,
        key: _Optional[str] = ...,
        value: _Optional[str] = ...,
        timestamp: _Optional[int] = ...,
    ) -> None: ...
