import os
from .proto_gen import GetResourceRequest
from .proto_gen import ProcessCollectionRequest
from .types import RecordList, Records
from .utils import collection_to_record, record_to_collection
from .proto_gen import Secret
from .proto_gen import TurbineService
from .resource import TurbineResource


class TurbineApp:
    def __init__(self, core_server: TurbineService, run_process: bool) -> None:
        self.core_server = core_server
        self.run_process = run_process

    async def resources(self, resouce_name) -> TurbineResource:
        req = GetResourceRequest(name=resouce_name)
        ret = self.core_server.GetResource(request=req)
        return TurbineResource(ret, self)

    async def process(self, process_records: Records, fn: RecordList) -> Records:
        process_collection = record_to_collection(records=process_records)
        req = ProcessCollectionRequest(
            process=ProcessCollectionRequest.Process(name=fn.__name__),
            collection=process_collection,
        )
        col = self.core_server.AddProcessToCollection(request=req)
        records_output = collection_to_record(collection=col)
        if self.run_process:
            records_output.records = fn(records_output.records)
        return records_output

    def register_secrets(self, secret) -> None:
        req = Secret(name=secret, value=os.getenv(secret))
        self.core_server.RegisterSecret(request=req)
