from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor
GOLANG: Language
JAVASCRIPT: Language
PYTHON: Language
RUBY: Language

class Collection(_message.Message):
    __slots__ = ["name", "records", "stream"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    RECORDS_FIELD_NUMBER: _ClassVar[int]
    STREAM_FIELD_NUMBER: _ClassVar[int]
    name: str
    records: _containers.RepeatedCompositeFieldContainer[Record]
    stream: str
    def __init__(self, stream: _Optional[str] = ..., records: _Optional[_Iterable[_Union[Record, _Mapping]]] = ..., name: _Optional[str] = ...) -> None: ...

class Config(_message.Message):
    __slots__ = ["field", "value"]
    FIELD_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    field: str
    value: str
    def __init__(self, field: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class Configs(_message.Message):
    __slots__ = ["config"]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    config: _containers.RepeatedCompositeFieldContainer[Config]
    def __init__(self, config: _Optional[_Iterable[_Union[Config, _Mapping]]] = ...) -> None: ...

class GetResourceRequest(_message.Message):
    __slots__ = ["name"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class GetSpecRequest(_message.Message):
    __slots__ = ["image"]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    image: str
    def __init__(self, image: _Optional[str] = ...) -> None: ...

class GetSpecResponse(_message.Message):
    __slots__ = ["spec"]
    SPEC_FIELD_NUMBER: _ClassVar[int]
    spec: bytes
    def __init__(self, spec: _Optional[bytes] = ...) -> None: ...

class InitRequest(_message.Message):
    __slots__ = ["appName", "configFilePath", "gitSHA", "language", "turbineVersion"]
    APPNAME_FIELD_NUMBER: _ClassVar[int]
    CONFIGFILEPATH_FIELD_NUMBER: _ClassVar[int]
    GITSHA_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    TURBINEVERSION_FIELD_NUMBER: _ClassVar[int]
    appName: str
    configFilePath: str
    gitSHA: str
    language: Language
    turbineVersion: str
    def __init__(self, appName: _Optional[str] = ..., configFilePath: _Optional[str] = ..., language: _Optional[_Union[Language, str]] = ..., gitSHA: _Optional[str] = ..., turbineVersion: _Optional[str] = ...) -> None: ...

class ListResourcesResponse(_message.Message):
    __slots__ = ["resources"]
    RESOURCES_FIELD_NUMBER: _ClassVar[int]
    resources: _containers.RepeatedCompositeFieldContainer[Resource]
    def __init__(self, resources: _Optional[_Iterable[_Union[Resource, _Mapping]]] = ...) -> None: ...

class ProcessCollectionRequest(_message.Message):
    __slots__ = ["collection", "process"]
    class Process(_message.Message):
        __slots__ = ["name"]
        NAME_FIELD_NUMBER: _ClassVar[int]
        name: str
        def __init__(self, name: _Optional[str] = ...) -> None: ...
    COLLECTION_FIELD_NUMBER: _ClassVar[int]
    PROCESS_FIELD_NUMBER: _ClassVar[int]
    collection: Collection
    process: ProcessCollectionRequest.Process
    def __init__(self, process: _Optional[_Union[ProcessCollectionRequest.Process, _Mapping]] = ..., collection: _Optional[_Union[Collection, _Mapping]] = ...) -> None: ...

class ReadCollectionRequest(_message.Message):
    __slots__ = ["collection", "configs", "resource"]
    COLLECTION_FIELD_NUMBER: _ClassVar[int]
    CONFIGS_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    collection: str
    configs: Configs
    resource: Resource
    def __init__(self, resource: _Optional[_Union[Resource, _Mapping]] = ..., configs: _Optional[_Union[Configs, _Mapping]] = ..., collection: _Optional[str] = ...) -> None: ...

class Record(_message.Message):
    __slots__ = ["key", "timestamp", "value"]
    KEY_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: str
    timestamp: _timestamp_pb2.Timestamp
    value: bytes
    def __init__(self, key: _Optional[str] = ..., value: _Optional[bytes] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Resource(_message.Message):
    __slots__ = ["collection", "destination", "name", "source"]
    COLLECTION_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    collection: str
    destination: bool
    name: str
    source: bool
    def __init__(self, name: _Optional[str] = ..., source: bool = ..., destination: bool = ..., collection: _Optional[str] = ...) -> None: ...

class Secret(_message.Message):
    __slots__ = ["name", "value"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    name: str
    value: str
    def __init__(self, name: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class WriteCollectionRequest(_message.Message):
    __slots__ = ["configs", "resource", "sourceCollection", "targetCollection"]
    CONFIGS_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    SOURCECOLLECTION_FIELD_NUMBER: _ClassVar[int]
    TARGETCOLLECTION_FIELD_NUMBER: _ClassVar[int]
    configs: Configs
    resource: Resource
    sourceCollection: Collection
    targetCollection: str
    def __init__(self, resource: _Optional[_Union[Resource, _Mapping]] = ..., sourceCollection: _Optional[_Union[Collection, _Mapping]] = ..., targetCollection: _Optional[str] = ..., configs: _Optional[_Union[Configs, _Mapping]] = ...) -> None: ...

class Language(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
