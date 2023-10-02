# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import voice_agent_pb2 as voice__agent__pb2


class VoiceAgentServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.CheckServiceStatus = channel.unary_unary(
                '/VoiceAgentService/CheckServiceStatus',
                request_serializer=voice__agent__pb2.Empty.SerializeToString,
                response_deserializer=voice__agent__pb2.ServiceStatus.FromString,
                )
        self.DetectWakeWord = channel.unary_stream(
                '/VoiceAgentService/DetectWakeWord',
                request_serializer=voice__agent__pb2.Empty.SerializeToString,
                response_deserializer=voice__agent__pb2.WakeWordStatus.FromString,
                )
        self.RecognizeVoiceCommand = channel.stream_unary(
                '/VoiceAgentService/RecognizeVoiceCommand',
                request_serializer=voice__agent__pb2.RecognizeControl.SerializeToString,
                response_deserializer=voice__agent__pb2.RecognizeResult.FromString,
                )
        self.ExecuteVoiceCommand = channel.unary_unary(
                '/VoiceAgentService/ExecuteVoiceCommand',
                request_serializer=voice__agent__pb2.ExecuteInput.SerializeToString,
                response_deserializer=voice__agent__pb2.ExecuteResult.FromString,
                )


class VoiceAgentServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def CheckServiceStatus(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DetectWakeWord(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RecognizeVoiceCommand(self, request_iterator, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ExecuteVoiceCommand(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_VoiceAgentServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'CheckServiceStatus': grpc.unary_unary_rpc_method_handler(
                    servicer.CheckServiceStatus,
                    request_deserializer=voice__agent__pb2.Empty.FromString,
                    response_serializer=voice__agent__pb2.ServiceStatus.SerializeToString,
            ),
            'DetectWakeWord': grpc.unary_stream_rpc_method_handler(
                    servicer.DetectWakeWord,
                    request_deserializer=voice__agent__pb2.Empty.FromString,
                    response_serializer=voice__agent__pb2.WakeWordStatus.SerializeToString,
            ),
            'RecognizeVoiceCommand': grpc.stream_unary_rpc_method_handler(
                    servicer.RecognizeVoiceCommand,
                    request_deserializer=voice__agent__pb2.RecognizeControl.FromString,
                    response_serializer=voice__agent__pb2.RecognizeResult.SerializeToString,
            ),
            'ExecuteVoiceCommand': grpc.unary_unary_rpc_method_handler(
                    servicer.ExecuteVoiceCommand,
                    request_deserializer=voice__agent__pb2.ExecuteInput.FromString,
                    response_serializer=voice__agent__pb2.ExecuteResult.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'VoiceAgentService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class VoiceAgentService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def CheckServiceStatus(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/VoiceAgentService/CheckServiceStatus',
            voice__agent__pb2.Empty.SerializeToString,
            voice__agent__pb2.ServiceStatus.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def DetectWakeWord(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/VoiceAgentService/DetectWakeWord',
            voice__agent__pb2.Empty.SerializeToString,
            voice__agent__pb2.WakeWordStatus.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def RecognizeVoiceCommand(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_unary(request_iterator, target, '/VoiceAgentService/RecognizeVoiceCommand',
            voice__agent__pb2.RecognizeControl.SerializeToString,
            voice__agent__pb2.RecognizeResult.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ExecuteVoiceCommand(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/VoiceAgentService/ExecuteVoiceCommand',
            voice__agent__pb2.ExecuteInput.SerializeToString,
            voice__agent__pb2.ExecuteResult.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
