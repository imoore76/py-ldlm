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
"""
This module defines the base client class for interacting with the ldlm gRPC server and associated
TLSConfig class for TLS configuration.
"""
from __future__ import annotations

import abc
from dataclasses import dataclass
import logging
from typing import Optional, Any

import grpc

from ldlm.protos import ldlm_pb2_grpc as pb2grpc


def readfile(file_path: Optional[str] = None) -> bytes | None:
    """
    Reads the entire contents of a file.

    param: file_path (str, optional): The path to the file to read. If None, an empty string is
        returned.

    Returns:
        bytes: The contents of the file as bytes or None if file_path is None.

    """
    if file_path is None:
        return None

    with open(file_path, "rb") as f:
        return f.read()


@dataclass
class TLSConfig():
    """
    TLS configuration class
    """
    cert_file: Optional[str] = None
    key_file: Optional[str] = None
    ca_file: Optional[str] = None


class BaseClient(abc.ABC):  # pylint: disable=R0903,R0902
    """
    Base client class for interacting with the ldlm gRPC server.
    """
    # Minimum time between lock refreshes
    min_refresh_interval_seconds = 10

    def __init__(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        self,
        address: str,
        password: Optional[str] = None,
        tls: Optional[TLSConfig] = None,
        retries: int = -1,
        retry_delay_seconds: int = 5,
        auto_refresh_locks: bool = True,
        lock_timeout_seconds: int = 0,
    ):
        """
        Initializes a new instance of the class.

        param: address (str): The address of the server.
        param: password (str, optional): The password to use for authentication. Defaults to None.
        param: tls (TLSConfig, optional): TLS configuration. Defaults to None.
        param: retries (int, optional): The number of retries to attempt. Defaults to -1
            (infinite). 0 to disable retries
        param: retry_delay_seconds (int, optional): The delay in seconds between retry attempts.
        param: auto_refresh_locks (bool, optional): Automatically refreshed at an appropriate
            interval using a RefreshLockTimer thread
        param: lock_timeout (int, optional): The lock timeout to use for all lock operations
        """

        if tls is not None:
            creds = grpc.ssl_channel_credentials(
                root_certificates=readfile(tls.ca_file),
                private_key=readfile(tls.key_file),
                certificate_chain=readfile(tls.cert_file),
            )
        else:
            creds = None

        self._channel = self._create_channel(address, creds)

        # Number of times to retry each request in case of failure
        self._retries: int = retries

        # Auto-refresh locks at an appropriate interval
        self._auto_refresh_locks: bool = auto_refresh_locks

        # Need password for RPC calls
        self._password: Optional[str] = password

        # Hold ref to client for gRPC calls
        self.stub: pb2grpc.LDLMStub = pb2grpc.LDLMStub(self._channel)

        # Hold ref to lock timers so they can be canceled when unlocking
        self._lock_timers: dict[str, Any] = {}

        # Flag to indicate if the client is closed
        self._closed: bool = False

        # setup logger
        self._logger = logging.getLogger("ldlm")

        # Forced lock timeout
        self._lock_timeout_seconds = lock_timeout_seconds

        # Delay between retry attempts
        self._retry_delay_seconds = retry_delay_seconds

    @abc.abstractmethod
    def _create_channel(
        self,
        address: str,
        creds: Optional[grpc.ChannelCredentials] = None,
    ) -> grpc.Channel:
        """
        Creates a gRPC channel with the specified address and credentials.

        param: address (str): The address of the gRPC server.
        param: creds (Optional[grpc.ChannelCredentials], optional): The credentials to use for the
            channel. Defaults to None.

        Returns:
            grpc.Channel: The created gRPC channel.

        Raises:
            NotImplementedError: If the method is not implemented in the subclass.
        """
        raise NotImplementedError("_create_channel not implemented")
