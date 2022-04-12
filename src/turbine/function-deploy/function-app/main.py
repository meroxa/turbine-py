import asyncio
import importlib.util
import logging
import os
import sys

import grpc

import service_pb2
import service_pb2_grpc
from record import TurbineRecord

"""
Process function given to GRPC server
"""

FUNCTION_NAME = sys.argv[1]
FUNCTION_ADDRESS = os.getenv("MEROXA_FUNCTION_ADDR")
PATH_TO_DATA_APP = os.path.normpath(os.path.dirname(__file__) + "/../data-app/main.py")

# Coroutines to be invoked when the event loop is shutting down.
_cleanup_coroutines = []


class Funtime(service_pb2_grpc.FunctionServicer):
    def Process(
        self,
        request: service_pb2.ProcessRecordRequest,
        context: grpc.aio.ServicerContext,
    ) -> service_pb2.ProcessRecordResponse:
        spec = importlib.util.spec_from_file_location("data-app.main", PATH_TO_DATA_APP)
        data_app = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(data_app)

        # map from rpc => something we can work with
        input_records = [TurbineRecord(record) for record in request.records]

        # Get the data app function
        data_app_function = data_app.__getattribute__(FUNCTION_NAME)

        # Generate output
        output_records = data_app_function(input_records)

        # Serialize and return
        grpc_records = [record.serialize() for record in output_records]

        return service_pb2.ProcessRecordResponse(records=grpc_records)


async def serve() -> None:
    server = grpc.aio.server()
    service_pb2_grpc.add_FunctionServicer_to_server(Funtime(), server)
    server.add_insecure_port(FUNCTION_ADDRESS)

    logging.info(f"Starting server on {FUNCTION_ADDRESS}")

    await server.start()

    async def shutdown():
        logging.info("Shutting python gRPC server down..")
        await server.stop(grace=5)

    _cleanup_coroutines.append(shutdown())
    await server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info(f"arguments {sys.argv}")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(serve())
    finally:
        loop.run_until_complete(*_cleanup_coroutines)
        loop.close()
