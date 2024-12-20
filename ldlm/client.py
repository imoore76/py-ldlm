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
This module contains the python client class for the ldlm service.
"""
from __future__ import annotations

import time
import logging
from contextlib import contextmanager
from typing import Optional, Callable, Iterator, Union
from threading import Timer

import grpc
from grpc._channel import _InactiveRpcError

from ldlm import exceptions
from ldlm.base_client import BaseClient
from ldlm.protos import ldlm_pb2 as pb2


class RefreshLockTimer(Timer):
    """
    threading.Timer implementation for refreshing a lock
    """

    def __init__(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        self,
        refresh_lock: Callable,
        name: str,
        key: str,
        lock_timeout_seconds: int,
        interval: int,
        logger: logging.Logger,
    ):
        """
        Initializes a new instance of the class.

        param: refresh_lock (Callable): The function to call to refresh the lock.
        param: name (str): The name of the lock to refresh.
        param: key (str): The key associated with the lock to refresh.
        param: lock_timeout_seconds (int): The timeout in seconds after which the lock will expire
        param: interval (int): The interval in seconds between refresh attempts
        param: logger (logging.Logger): The logger to use for logging
        """
        logger.debug(
            f"Refresh timer refreshing lock {name} every {interval} seconds.")
        super().__init__(
            interval,
            refresh_lock,
            args=(name, key, lock_timeout_seconds),
        )

    def run(self):
        """
        Start the timer thread
        """
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


class Client(BaseClient):
    """
    Client class for interacting with the ldlm gRPC server.
    """

    def _create_channel(
        self,
        address: str,
        creds: Optional[grpc.ChannelCredentials] = None,
    ) -> grpc.Channel:
        """
        Creates a gRPC channel to the specified address with optional credentials. Required by
        BaseClient ABC.

        param: address (str): The address of the gRPC server.
        param: creds (grpc.ChannelCredentials, optional): The credentials to use for the
            channel. Defaults to None.

        Returns:
            grpc.Channel: The created gRPC channel.

        Raises:
            None
        """
        if creds is not None:
            return grpc.secure_channel(
                address,
                creds,
            )
        return grpc.insecure_channel(address)

    def refresh_lock(
            self, name: str, key: str,
            lock_timeout_seconds: int) -> pb2.LockResponse:  # pylint: disable=E1101
        """
        Attempts to refresh a lock.

        param: name (str): The name of the lock to refresh.
        param: key (str): The key associated with the lock to refresh.
        param: lock_timeout_seconds (int): The timeout in seconds for acquiring the lock.

        Returns:
                object: The response object returned by the gRPC server indicating the result of
                    the refresh attempt.
        """
        rpc_msg: pb2.RefreshLockRequest = (
            pb2.RefreshLockRequest(  # pylint: disable=E1101
                name=name,
                key=key,
                lock_timeout_seconds=lock_timeout_seconds,
            ))

        return self.rpc_with_retry("RefreshLock", rpc_msg)  # type: ignore

    def unlock(self, name: str, key: str) -> None:
        """
        Attempts to unlock a lock.

        param: name (str): The name of the lock to unlock.
        param: key (str): The key associated with the lock to unlock.

        Raises:
                RuntimeError: If the lock cannot be unlocked.
        """
        if timer := self._lock_timers.pop(name, None):
            self._logger.debug(f"Canceling lock refresh for `{name}`")
            timer.cancel()
            timer.join()

        rpc_msg: pb2.UnlockRequest = pb2.UnlockRequest(  # pylint: disable=E1101
            name=name,
            key=key,
        )

        self._logger.debug(f"Unlocking `{name}`")
        r: pb2.UnlockResponse = self.rpc_with_retry("Unlock",
                                                    rpc_msg)  # type: ignore
        self._logger.debug(f"Unlock response from server: {r}")
        if not r.unlocked:  # pragma: no cover
            raise RuntimeError(f"Failed to unlock {name}")

    def lock(
        self,
        name: str,
        wait_timeout_seconds: int = 0,
        lock_timeout_seconds: int = 0,
        size: int = 0,
    ) -> pb2.LockResponse:
        """
        Attempt to acquire a lock with the given name.

        param: name (str): The name of the lock to acquire.
        param: wait_timeout_seconds (int, optional): The timeout in seconds to wait for the lock to
            be acquired. Defaults to 0.
        param: lock_timeout_seconds (int, optional): The timeout in seconds to wait for the lock to
            be acquired. Defaults to 0.
        param: size (int, optional): The size of the lock. Defaults to 0 which translates to
            unspecified. The server will use a size of 1 in this case.

        Returns:
            object: The response object returned by the gRPC server indicating the result of the
                lock attempt.

        Raises:
            RuntimeError: If the lock cannot be released after being acquired.

        Example:
            response = client.lock("my_lock", wait_timeout_seconds=10, lock_timeout_seconds=600)
            if response.locked:
                # Lock acquired, do something, then unlock
            else:
                # Lock not acquired, handle accordingly
        """
        rpc_msg: pb2.LockRequest = pb2.LockRequest(name=name)  # pylint: disable=E1101
        if wait_timeout_seconds:
            rpc_msg.wait_timeout_seconds = wait_timeout_seconds
        if self._lock_timeout_seconds:
            rpc_msg.lock_timeout_seconds = self._lock_timeout_seconds
        elif lock_timeout_seconds:
            rpc_msg.lock_timeout_seconds = lock_timeout_seconds
        if size > 0:  # pylint: disable=R1730
            rpc_msg.size = size

        try:
            self._logger.info(f"Waiting to acquire lock `{name}`")
            r: pb2.LockResponse = self.rpc_with_retry("Lock",
                                                      rpc_msg)  # type: ignore
        except exceptions.LockWaitTimeoutError:
            r = pb2.LockResponse(name=name, locked=False)  # pylint: disable=E1101

        self._logger.info(f"Lock response from server: {r}")

        if r.locked and lock_timeout_seconds and self._auto_refresh_locks:
            self._start_refresh(name, r.key, rpc_msg.lock_timeout_seconds)

        return r

    @contextmanager
    def lock_context(
        self,
        name: str,
        wait_timeout_seconds: int = 0,
        lock_timeout_seconds: int = 0,
        size: int = 0,
    ) -> Iterator[pb2.LockResponse]:
        """
        A context manager that attempts to acquire a lock with the given name. Unlocks the lock
        when the context is exited.

        param: name (str): The name of the lock to acquire.
        param: wait_timeout_seconds (int, optional): The timeout in seconds to wait for the lock
            to be acquired. Defaults to 0.
        param: lock_timeout_seconds (int, optional): The timeout in seconds to wait for the lock
            to be acquired. Defaults to 0.
        param: size (int, optional): The size of the lock. Defaults to 0 which translates to
            unspecified. The server will use a size of 1 in this case.

        Yields:
            object: The response object returned by the gRPC server indicating the result of the
                lock attempt.

        Raises:
            RuntimeError: If the lock cannot be released after being acquired.

        Example:
            with client.lock_context(
                "my_lock",
                wait_timeout_seconds=10,
                lock_timeout_seconds=600,
            ) as response:
                if response.locked:
                    # Lock acquired, do something
                else:
                    # Lock not acquired, handle accordingly
        """
        lock = self.lock(
            name,
            wait_timeout_seconds=wait_timeout_seconds,
            lock_timeout_seconds=lock_timeout_seconds,
            size=size,
        )

        try:
            yield lock
        finally:
            if lock.locked:
                self.unlock(name, lock.key)

    @contextmanager
    def try_lock_context(
        self,
        name: str,
        lock_timeout_seconds: int = 0,
        size: int = 0,
    ) -> Iterator[pb2.LockResponse]:
        """
        A context manager that attempts to acquire a lock with the given name. If auto_refresh_lock
        is True, the lock will be automatically refreshed after it is acquired by a
        RefreshLockTimer thread. Unlocks the lock and stops the RefreshLockTimer thread when the
        context is exited.

        param: name (str): The name of the lock to acquire.
        param: lock_timeout_seconds (int, optional): The timeout in seconds to wait for the lock to
            be acquired. Defaults to 0.
        param: size (int, optional): The size of the lock. Defaults to 0 which translates to
            unspecified. The server will use a size of 1 in this case.

        Yields:
            object: The response object returned by the gRPC server indicating the result of the
                lock attempt.

        Raises:
            RuntimeError: If the lock cannot be released after being acquired.

        Example:
            with client.try_lock_context(stub, "my_lock", lock_timeout_seconds=60) as response:
                if response.locked:
                    # Lock acquired, do something
                else:
                    # Lock not acquired, handle accordingly
        """
        lock = self.try_lock(
            name,
            lock_timeout_seconds=lock_timeout_seconds,
            size=size,
        )

        try:
            yield lock
        finally:
            if lock.locked:
                self.unlock(name, lock.key)

    def try_lock(
        self,
        name: str,
        lock_timeout_seconds: int = 0,
        size: int = 0,
    ) -> pb2.LockResponse:  # pylint: disable=E1101
        """
        Attempt to acquire a lock with the given name. If auto_refresh_lock is True, the lock will
        be automatically refreshed at an appropriate interval using a RefreshLockTimer thread.

        param: name (str): The name of the lock to acquire.
        param: lock_timeout_seconds (int, optional): The timeout in seconds to wait for the lock
            to be acquired. Defaults to 0.
        param: size (int, optional): The size of the lock. Defaults to 0 which translates to
            unspecified. The server will use a size of 1 in this case.

        Returns:
            object: The response object returned by the gRPC server indicating the result of the
                lock attempt.

        Example:
                response = client.try_lock(stub, "my_lock", 10)
                if response.locked:
                    # Lock acquired. do something then unlock
                else:
                    # Lock not acquired, handle accordingly
        """
        rpc_msg: pb2.TryLockRequest = pb2.TryLockRequest(  # pylint: disable=E1101
            name=name,)
        if self._lock_timeout_seconds:
            rpc_msg.lock_timeout_seconds = self._lock_timeout_seconds
        elif lock_timeout_seconds:
            rpc_msg.lock_timeout_seconds = lock_timeout_seconds
        if size > 0:  # pylint: disable=R1730
            rpc_msg.size = size

        self._logger.info(f"Attempting to acquire lock `{name}`")
        r: pb2.LockResponse = self.rpc_with_retry("TryLock",
                                                  rpc_msg)  # type: ignore
        self._logger.info(f"Lock response from server: {r}")

        if r.locked and lock_timeout_seconds and self._auto_refresh_locks:
            self._start_refresh(name, r.key, rpc_msg.lock_timeout_seconds)

        return r

    def _start_refresh(self, name: str, key: str,
                       lock_timeout_seconds: int) -> None:
        """
        Start the refresh timer for a lock.

        param: name (str): The name of the lock to refresh.
        param: key (str): The key associated with the lock to refresh.
        param: lock_timeout_seconds (int): The timeout in seconds after which the lock will expire

        Raises:
            RuntimeError: If a refresh timer already exists for the lock.

        Returns:
            None
        """
        if name in self._lock_timers:  # pragma: no cover
            raise RuntimeError(f"Lock `{name}` already has a refresh timer")

        interval = max(lock_timeout_seconds - 30,
                       self.min_refresh_interval_seconds)

        self._lock_timers[name] = RefreshLockTimer(
            self.refresh_lock,
            name,
            key,
            lock_timeout_seconds,
            interval=interval,
            logger=self._logger,
        )
        self._lock_timers[name].start()

    def rpc_with_retry(
        self,
        rpc_func: str,
        rpc_message: Union[
            pb2.LockRequest,
            pb2.TryLockRequest,
            pb2.RefreshLockRequest,
            pb2.UnlockRequest,
        ],
    ) -> Union[pb2.LockResponse, pb2.UnlockResponse]:
        """
        Executes an RPC call with retries in case of errors.

        :param rpc_func: The RPC function to call.
        :param rpc_message: The message to send in the RPC call.

        :return: The response from the RPC call.
        """
        num_retries = 0
        if self._password is not None:
            metadata = (("authorization", self._password),)
        else:
            metadata = None

        rpc_callable = getattr(self.stub, rpc_func)
        while True:
            try:
                resp = rpc_callable(rpc_message, metadata=metadata)
                if resp.HasField("error"):  # pragma: no cover
                    raise exceptions.from_rpc_error(resp.error)
                return resp
            except _InactiveRpcError as e:
                if self._retries > -1 and num_retries == self._retries:
                    raise
                num_retries += 1
                self._logger.warning(
                    f"Encountered error {e} while trying rpc_call. "
                    f"Retrying in {self._retry_delay_seconds} seconds "
                    f"({num_retries} of {self._retries}).")
            time.sleep(self._retry_delay_seconds)

    def close(self) -> None:
        """
        Closes the channel and sets the `_closed` attribute to `True`.

        This method is used to close the channel and indicate that the client is no longer active.
        It is typically called when the client is no longer needed or when the program is exiting.
        """
        self._channel.close()
        self._closed = True

    def __del__(self) -> None:
        """
        Closes the channel if it is not already closed.

        This method is called when the object is about to be destroyed. It checks if the channel is
            still open and closes it if it is not.
        """
        if self._channel and not getattr(self, "_closed", False):
            self._channel.close()
