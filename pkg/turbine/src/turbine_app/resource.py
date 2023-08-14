from .proto_gen import Config
from .proto_gen import ReadCollectionRequest
from .proto_gen import Resource
from .proto_gen import WriteCollectionRequest
from .types import Records
from .utils import collection_to_record
from .utils import record_to_collection


class TurbineResource:
    def __init__(self, resource: Resource, app) -> None:
        self.resource = resource
        self.app = app

    async def records(
        self, read_collection: str, connector_config: dict[str, str] = None
    ) -> Records:
        req = ReadCollectionRequest(resource=self.resource, collection=read_collection)
        if connector_config:
            map_config = [
                Config(field=key, value=item) for key, item in connector_config.items()
            ]
            req.configs = map_config
        ret_collection = self.app.core_server.ReadCollection(request=req)
        processed_records = collection_to_record(collection=ret_collection)
        return processed_records

    async def write(
        self,
        records: Records,
        write_collection: str,
        connector_config: dict[str, str] = None,
    ):
        req = WriteCollectionRequest(
            resource=self.resource,
            sourceCollection=record_to_collection(records),
            targetCollection=write_collection,
        )
        if connector_config:
            map_config = [
                Config(field=key, value=item) for key, item in connector_config.items
            ]
            req.configs = map_config
        self.app.core_server.WriteCollectionToResource(request=req)
