# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from . import ldlm_pb2 as ldlm__pb2

GRPC_GENERATED_VERSION = '1.63.0'
GRPC_VERSION = grpc.__version__
EXPECTED_ERROR_RELEASE = '1.65.0'
SCHEDULED_RELEASE_DATE = 'June 25, 2024'
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    warnings.warn(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in ldlm_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
        + f' This warning will become an error in {EXPECTED_ERROR_RELEASE},'
        + f' scheduled for release on {SCHEDULED_RELEASE_DATE}.',
        RuntimeWarning
    )


class LDLMStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Lock = channel.unary_unary(
                '/ldlm.LDLM/Lock',
                request_serializer=ldlm__pb2.LockRequest.SerializeToString,
                response_deserializer=ldlm__pb2.LockResponse.FromString,
                _registered_method=True)
        self.TryLock = channel.unary_unary(
                '/ldlm.LDLM/TryLock',
                request_serializer=ldlm__pb2.TryLockRequest.SerializeToString,
                response_deserializer=ldlm__pb2.LockResponse.FromString,
                _registered_method=True)
        self.Unlock = channel.unary_unary(
                '/ldlm.LDLM/Unlock',
                request_serializer=ldlm__pb2.UnlockRequest.SerializeToString,
                response_deserializer=ldlm__pb2.UnlockResponse.FromString,
                _registered_method=True)
        self.Renew = channel.unary_unary(
                '/ldlm.LDLM/Renew',
                request_serializer=ldlm__pb2.RenewRequest.SerializeToString,
                response_deserializer=ldlm__pb2.LockResponse.FromString,
                _registered_method=True)


class LDLMServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Lock(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def TryLock(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Unlock(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Renew(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_LDLMServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Lock': grpc.unary_unary_rpc_method_handler(
                    servicer.Lock,
                    request_deserializer=ldlm__pb2.LockRequest.FromString,
                    response_serializer=ldlm__pb2.LockResponse.SerializeToString,
            ),
            'TryLock': grpc.unary_unary_rpc_method_handler(
                    servicer.TryLock,
                    request_deserializer=ldlm__pb2.TryLockRequest.FromString,
                    response_serializer=ldlm__pb2.LockResponse.SerializeToString,
            ),
            'Unlock': grpc.unary_unary_rpc_method_handler(
                    servicer.Unlock,
                    request_deserializer=ldlm__pb2.UnlockRequest.FromString,
                    response_serializer=ldlm__pb2.UnlockResponse.SerializeToString,
            ),
            'Renew': grpc.unary_unary_rpc_method_handler(
                    servicer.Renew,
                    request_deserializer=ldlm__pb2.RenewRequest.FromString,
                    response_serializer=ldlm__pb2.LockResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'ldlm.LDLM', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class LDLM(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Lock(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/ldlm.LDLM/Lock',
            ldlm__pb2.LockRequest.SerializeToString,
            ldlm__pb2.LockResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def TryLock(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/ldlm.LDLM/TryLock',
            ldlm__pb2.TryLockRequest.SerializeToString,
            ldlm__pb2.LockResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def Unlock(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/ldlm.LDLM/Unlock',
            ldlm__pb2.UnlockRequest.SerializeToString,
            ldlm__pb2.UnlockResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def Renew(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/ldlm.LDLM/Renew',
            ldlm__pb2.RenewRequest.SerializeToString,
            ldlm__pb2.LockResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
