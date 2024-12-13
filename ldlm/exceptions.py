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
"""
This module contains the exception classes for the ldlm service.
"""


def from_rpc_error(rpc_error):
    """
    Converts an RPC error into a corresponding LDLM exception.

    param rpc_error: The RPC error to convert.

    Returns:
        BaseLDLMException: The corresponding LDLM exception.

    """
    for cls in BaseLDLMException.__subclasses__():
        if rpc_error.code == cls.RPC_CODE:
            return cls(rpc_error.message)
    return LDLMError(rpc_error.message)


class BaseLDLMException(Exception):
    """
    Base class for all LDLM exceptions.
    """
    __slots__ = ("message",)

    def __init__(self, message):
        self.message = message


class LDLMError(BaseLDLMException):
    """
    LDLM error.
    """
    RPC_CODE = 0


class LockDoesNotExistError(BaseLDLMException):
    """
    Lock does not exist error.
    """
    RPC_CODE = 1


class InvalidLockKeyError(BaseLDLMException):
    """
    Invalid lock key error.
    """
    RPC_CODE = 2


class LockWaitTimeoutError(BaseLDLMException):
    """
    Lock wait timeout error.
    """
    RPC_CODE = 3


class NotLockedError(BaseLDLMException):
    """
    Unlock request for a lock that is not locked error.
    """
    RPC_CODE = 4


class LockDoesNotExistOrInvalidKeyError(BaseLDLMException):
    """
    Lock does not exist or invalid key error.
    """
    RPC_CODE = 5


class LockSizeMismatchError(BaseLDLMException):
    """
    The size of the lock does not match the size specified in the lock request.
    """
    RPC_CODE = 6
