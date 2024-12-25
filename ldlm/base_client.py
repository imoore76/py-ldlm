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
Base client class for interacting with the LDLM gRPC server and TLSConfig class for
LDLM client TLS configuration.
"""
from __future__ import annotations

import abc
from dataclasses import dataclass
import logging
from typing import Optional, Any

import grpc

from ldlm.protos import ldlm_pb2_grpc as ldlm_grpc


def readfile(file_path: Optional[str] = None) -> bytes | None:
    """
    Reads the entire contents of a file.

    file_path (str, optional): The path to the file to read. If None, an empty string is
        returned.

    Returns:
        bytes: The contents of the file as bytes or None if file_path is None.

    """
    if file_path is None:
        return None

    with open(file_path, "rb") as f:
        return f.read()


@dataclass
class TLSConfig:
    """
    TLS configuration dataclass for LDLM client. Pass an instance of this class as the `tls`
    parameter to an LDLM client constructor.
    """

    cert_file: Optional[str] = None
    """Path to the client certificate file"""

    key_file: Optional[str] = None
    """Path to the client key file"""

    ca_file: Optional[str] = None
    """Path to the CA certificate file"""


class BaseClient(abc.ABC):  # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """
    Base client class for interacting with the LDLM gRPC server.
    """

    min_renew_interval_seconds: int = 10
    """minimum time between lock renews in seconds"""

    def __init__(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        self,
        address: str,
        password: Optional[str] = None,
        tls: Optional[TLSConfig] = None,
        retries: int = -1,
        retry_delay_seconds: int = 5,
        auto_renew_locks: bool = True,
        lock_timeout_seconds: int = 0,
    ):
        """
        Args:
            address (str): The address of the server.
            password (str, optional): The password to use for authentication. Defaults to None.
            tls (TLSConfig, optional): TLS configuration. Leave `None` (default) to disable TLS.
            retries (int, optional): The number of retries to attempt. Defaults to `-1`
                (infinite). Set to `0` to disable retries
            retry_delay_seconds (int, optional): The delay in seconds between retry attempts.
            auto_renew_locks (bool, optional): Automatically renew locks using a background
                thread or asyncio task
            lock_timeout (int, optional): The lock timeout to use for all lock operations
        """

        if tls is not None:
            creds = grpc.ssl_channel_credentials(
                root_certificates=readfile(tls.ca_file),
                private_key=readfile(tls.key_file),
                certificate_chain=readfile(tls.cert_file),
            )
        else:
            creds = None

        self._channel: grpc.Channel = self._create_channel(address, creds)

        # Number of times to retry each request in case of failure
        self._retries: int = retries

        # Auto-renew locks at an appropriate interval
        self._auto_renew_locks: bool = auto_renew_locks

        # Need password for RPC calls
        self._password: Optional[str] = password

        # Hold ref to client for gRPC calls
        self._stub: ldlm_grpc.LDLMStub = ldlm_grpc.LDLMStub(self._channel)

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
    ) -> grpc.Channel:  # pragma: no cover
        """
        Abstract method that creates a gRPC channel with the specified address and credentials.
        """
        raise NotImplementedError("_create_channel not implemented")
