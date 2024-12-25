# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
Exception classes for the LDLM service.
"""
from typing import Union
from ldlm.protos import ldlm_pb2 as pb2


class _BaseLDLMException(Exception):
    """
    Base class for all LDLM exceptions.
    """
    RPC_CODE = -1

    __slots__ = ("message",)

    def __init__(self, message):
        self.message = message


class LDLMError(_BaseLDLMException):
    """
    Generic LDLM error.
    """

    RPC_CODE = 0


class LockDoesNotExistError(_BaseLDLMException):
    """
    Lock does not exist error. This can occur when attempting to unlock or renew a lock that
    does not exist.
    """

    RPC_CODE = 1


class InvalidLockKeyError(_BaseLDLMException):
    """
    Invalid lock key error. The key specified in the request is not valid.
    """

    RPC_CODE = 2


class LockWaitTimeoutError(_BaseLDLMException):
    """
    Lock wait timeout error. The lock could not be acquired in `wait_timeout_seconds` seconds.
    """

    RPC_CODE = 3


class NotLockedError(_BaseLDLMException):
    """
    Lock is not locked error. This can occur when attempting to renew or unlock a lock that
    is not locked.
    """

    RPC_CODE = 4


class LockDoesNotExistOrInvalidKeyError(_BaseLDLMException):
    """
    Lock does not exist or invalid key error. This can occur when renewing a lock using an
    invalid name or key.
    """

    RPC_CODE = 5


class LockSizeMismatchError(_BaseLDLMException):
    """
    The size of the lock in the LDLM server does not match the size specified. A previous lock
    request was made with a different size.
    """

    RPC_CODE = 6


class InvalidLockSizeError(_BaseLDLMException):
    """
    The specified size in the lock request is not a valid size (must be > 0).
    """

    RPC_CODE = 7


def from_rpc_error(
    rpc_error: pb2.Error
) -> Union[LDLMError, LockDoesNotExistError, InvalidLockKeyError,
           LockWaitTimeoutError, NotLockedError,
           LockDoesNotExistOrInvalidKeyError, LockSizeMismatchError,
           InvalidLockSizeError]:
    """
    Converts an LDLM error into a corresponding exception.

    param rpc_error: The LDLM error to convert.

    Returns:
        An exception.
    """
    for cls in _BaseLDLMException.__subclasses__():
        if rpc_error.code == cls.RPC_CODE:  # type: ignore
            return cls(rpc_error.message)  # type: ignore
    return LDLMError(rpc_error.message)
