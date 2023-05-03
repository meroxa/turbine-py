import os
import typing

from .proto_gen import Collection
from .proto_gen import GetResourceRequest
from .proto_gen import ProcessCollectionRequest
from .proto_gen import Record
from .proto_gen import Secret
from .proto_gen import TurbineService
from .resource import TurbineResource


class TurbineApp:
    def __init__(self, core_server: TurbineService) -> None:
        self.core_server = core_server

    async def resources(self, resouce_name) -> TurbineResource:
        req = GetResourceRequest(name=resouce_name)
        ret = self.core_server.GetResource(request=req)
        return TurbineResource(ret, self)

    async def process(
        self, records: Collection, fn: typing.Callable[[Record], Record]
    ) -> Collection:
        records.stream
        req = ProcessCollectionRequest(
            process=ProcessCollectionRequest.Process(name=fn.__name__),
            collection=records,
        )
        return self.core_server.AddProcessToCollection(request=req)

    def register_secrets(self, secret) -> None:
        req = Secret(name=secret, value=os.getenv(secret))
        self.core_server.RegisterSecret(request=req)
