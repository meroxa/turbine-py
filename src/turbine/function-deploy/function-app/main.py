import asyncio
import logging
import importlib
import importlib.util
import os
import sys

import grpc

import service_pb2
import service_pb2_grpc
from record import TurbineRecord

"""
Process function given to GRPC server
"""
TEMP_ADDRESS = "[::]:5005"
FUNCTION_NAME = ""
FUNCTION_ADDRESS = os.getenv("MEROXA_FUNCTION_ADDR")
PATH_TO_DATA_APP = "../data-app"


if spec := importlib.util.find_spec(os.path.abspath(PATH_TO_DATA_APP), 'main') is not None:
    data_app_module = importlib.util.module_from_spec(spec)
    sys.modules["dataapp"] = data_app_module
    spec.loader.exec_module(data_app_module)
    logging.info(f"{PATH_TO_DATA_APP!r} has been imported")
else:
    logging.error(f"unable to load module located at: {PATH_TO_DATA_APP!r}")


class Funtime(service_pb2_grpc.FunctionServicer):
    def Process(
        self,
        request: service_pb2.ProcessRecordRequest,
        context: grpc.aio.ServicerContext,
    ) -> service_pb2.ProcessRecordResponse:
        # map from rpc => something we can work with
        input_records = [TurbineRecord(record) for record in request.records]

        # Get the data app function
        # data_app_function = data_app[FUNCTION_NAME]

        # Generate output
        # output_records = data_app_function(input_records)
        output_records = []

        # Serialize and return
        grpc_records = [record.serialize() for record in input_records]

        return service_pb2.ProcessRecordResponse(records=grpc_records)


async def serve() -> None:
    server = grpc.aio.server()
    service_pb2_grpc.add_FunctionServicer_to_server(Funtime(), server)
    server.add_insecure_port(TEMP_ADDRESS)

    logging.info(f"Starting server on {TEMP_ADDRESS}")

    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(serve())
