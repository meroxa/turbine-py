import asyncio
import logging
import os


import importlib.util

import grpc

import service_pb2
import service_pb2_grpc
from record import TurbineRecord

"""
Process function given to GRPC server
"""
TEMP_ADDRESS = "[::]:5005"
FUNCTION_NAME = "anonymize"
FUNCTION_ADDRESS = os.getenv("MEROXA_FUNCTION_ADDR")

PACKAGE_NAME = "dataapp"

PATH_TO_DATA_APP = os.path.normpath(os.path.dirname(__file__) + '/../dataapp/main.py')


class Funtime(service_pb2_grpc.FunctionServicer):
    def Process(
            self,
            request: service_pb2.ProcessRecordRequest,
            context: grpc.aio.ServicerContext,
    ) -> service_pb2.ProcessRecordResponse:

        spec = importlib.util.spec_from_file_location("dataapp.main", PATH_TO_DATA_APP)
        data_app = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(data_app)

        # print(data_app.__getattribute__(FUNCTION_NAME))

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
    # TODO: properly import this
    # if (spec := importlib.util.find_spec(PACKAGE_NAME, PATH_TO_DATA_APP)) is not None:
    #
    #     # create python module based on given spec
    #     mod = importlib.util.module_from_spec(spec)
    #
    #     sys.modules["dataapp"] = mod
    #
    #     spec.loader.exec_module(mod)
    #     mod.App.run()
    #
    #     logging.info(f"{PATH_TO_DATA_APP!r} has been imported")
    # else:
    #     logging.error(f"unable to load module located at: {PATH_TO_DATA_APP!r}")

    server = grpc.aio.server()
    service_pb2_grpc.add_FunctionServicer_to_server(Funtime(), server)
    server.add_insecure_port(TEMP_ADDRESS)

    logging.info(f"Starting server on {TEMP_ADDRESS}")

    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(serve())
