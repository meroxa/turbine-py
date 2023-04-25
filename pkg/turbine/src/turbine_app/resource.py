
from .proto_gen import Resource, ReadCollectionRequest, WriteCollectionRequest, Collection, Config

class TurbineResource():
    def __init__(self, resource: Resource, app) -> None:
        self.resource = resource 
        self.app = app
    async def records(self, read_collection: str, connector_config: dict[str, str] = None) -> Collection:
        req = ReadCollectionRequest(resource=self.resource,
                                        collection=read_collection)
        if connector_config: 
            map_config = [Config(field = key, value = item) for key, item in connector_config.items]
            req.configs = map_config
        return self.app.core_server.ReadCollection(request=req)
            
    async def write(self, records: Collection, write_collection: str, connector_config: dict[str, str] = None):
        req = WriteCollectionRequest(resource=self.resource, 
                                     sourceCollection=records,
                                     targetCollection=write_collection)
        if connector_config: 
            map_config = [Config(field = key, value = item) for key, item in connector_config.items]
            req.configs = map_config
        self.app.core_server.WriteCollectionToResource(request=req) 