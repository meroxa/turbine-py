import asyncio
import logging
import os
import sys

import grpc
import grpc.aio
from grpc_health.v1 import health
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc
from grpc_reflection.v1alpha import reflection

import service_pb2
import service_pb2_grpc
from record import proto_records_to_turbine_records, turbine_records_to_proto_records

"""
Process function given to GRPC server
"""

FUNCTION_NAME = sys.argv[1]
FUNCTION_ADDRESS = os.getenv("MEROXA_FUNCTION_ADDR")
PATH_TO_DATA_APP = os.path.normpath(os.path.dirname(__file__) + "/../data-app/")

# Coroutines to be invoked when the event loop is shutting down.
_cleanup_coroutines = []


class Funtime(service_pb2_grpc.FunctionServicer):
    @staticmethod
    def _obtain_client_data_app_function(path_to_data_app: str, function_name: str):
        sys.path.append(path_to_data_app)
        import main

        return main.__getattribute__(function_name)

    def Process(
        self,
        request: service_pb2.ProcessRecordRequest,
        context: grpc.aio.ServicerContext,
    ) -> service_pb2.ProcessRecordResponse:
        # map from rpc => something we can work with
        input_records = proto_records_to_turbine_records(request.records)

        # Get the data app function
        data_app_function = self._obtain_client_data_app_function(
            path_to_data_app=PATH_TO_DATA_APP, function_name=FUNCTION_NAME
        )

        # Generate output
        output_records = data_app_function(input_records)

        # Serialize and return
        grpc_records = turbine_records_to_proto_records(output_records)

        return service_pb2.ProcessRecordResponse(records=grpc_records)


async def serve() -> None:
    server = grpc.aio.server()
    service_pb2_grpc.add_FunctionServicer_to_server(Funtime(), server)

    # Create a health check servicer. We use the non-blocking implementation
    # to avoid thread starvation.
    health_servicer = health.HealthServicer(experimental_non_blocking=True)

    # Create a tuple of all the services we want to export via reflection.
    services = tuple(
        service.full_name for service in health_pb2.DESCRIPTOR.services_by_name.values()
    ) + (reflection.SERVICE_NAME, "function")

    # Mark all services as healthy.
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
    for service in services:
        health_servicer.set(service, health_pb2.HealthCheckResponse.SERVING)
    reflection.enable_server_reflection(services, server)
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

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(serve())
    finally:
        loop.run_until_complete(*_cleanup_coroutines)
        loop.close()
