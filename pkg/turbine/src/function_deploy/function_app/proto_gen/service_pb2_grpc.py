# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
from . import service_pb2 as service__pb2


class FunctionStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Process = channel.unary_unary(
            "/io.meroxa.funtime.Function/Process",
            request_serializer=service__pb2.ProcessRecordRequest.SerializeToString,
            response_deserializer=service__pb2.ProcessRecordResponse.FromString,
        )


class FunctionServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Process(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_FunctionServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "Process": grpc.unary_unary_rpc_method_handler(
            servicer.Process,
            request_deserializer=service__pb2.ProcessRecordRequest.FromString,
            response_serializer=service__pb2.ProcessRecordResponse.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        "io.meroxa.funtime.Function", rpc_method_handlers
    )
    server.add_generic_rpc_handlers((generic_handler,))


# This class is part of an EXPERIMENTAL API.
class Function(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Process(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/io.meroxa.funtime.Function/Process",
            service__pb2.ProcessRecordRequest.SerializeToString,
            service__pb2.ProcessRecordResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )
