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
Python asyncio AsyncClient class and helpers for the LDLM service.
"""
from __future__ import annotations

import asyncio
import functools
import logging
from typing import Optional, Callable, AsyncIterator, Union
from contextlib import asynccontextmanager

import grpc
from grpc._channel import _InactiveRpcError

from ldlm import exceptions
from ldlm.base_client import BaseClient

from ldlm.protos import ldlm_pb2 as pb


class AsyncLock:
    """
    A lock returned by LDLM AsyncClient lock methods.
    """

    __slots__ = ("name", "key", "locked", "_client")

    def __init__(self, client: AsyncClient, lock: pb.LockResponse):
        """
        Args:
            client (Client): The client object.
            lock (pb.LockResponse): An LDLM lock response object.
        """
        self._client: Optional[AsyncClient] = client if lock.locked else None

        self.name: str = lock.name
        """name of the lock"""

        self.key: str = lock.key
        """key associated with the lock"""

        self.locked: bool = lock.locked
        """whether the lock is locked or not"""

    def __bool__(self) -> bool:
        """
        Returns whether the lock is locked or not.

        Returns:
            bool: Whether the lock is locked or not.
        """
        return self.locked

    async def unlock(self) -> None:
        """
        Unlocks the lock.

        Returns:
            None

        Raises:
            RuntimeError: If the lock is not locked
        """
        if not self.locked or self._client is None:
            raise RuntimeError("unlock() called on unlocked lock")

        await self._client.unlock(self.name, self.key)

    async def renew(self, lock_timeout_seconds: int) -> None:
        """
        Renews the lock.

        Args:
            lock_timeout_seconds (int): The timeout in seconds after which the lock will
                expire.

        Returns:
            None

        Raises:
            RuntimeError: If the lock is not locked
        """
        if not self.locked or self._client is None:
            raise RuntimeError("renew() called on unlocked lock")
        lock: AsyncLock = await self._client.renew(self.name, self.key,
                                                   lock_timeout_seconds)
        self.locked = lock.locked


class _RenewTimer:
    """
    Timer implementation for renewing a lock
    """

    def __init__(
        self,
        lock: AsyncLock,
        lock_timeout_seconds: int,
        interval: int,
        logger: logging.Logger,
    ):
        """
        Initializes a new instance of _RenewTimer.

        Args:
            lock (Lock): The lock to renew.
            lock_timeout_seconds (int): The timeout in seconds after which the lock will
                expire
            interval (int): The interval in seconds between renew attempts
            logger (logging.Logger): The logger to use for logging

        Returns:
            None
        """
        self.interval: int = interval
        self.fn: Callable = functools.partial(lock.renew, lock_timeout_seconds)
        self.task: asyncio.Task | None = None
        logger.debug(
            f"Renew timer renewing lock {lock.name} every {self.interval} seconds."
        )

    async def start(self) -> None:
        """
        Asynchronously starts the lock renewer.

        Returns:
            None
        """
        self.task = asyncio.create_task(self.run())

    async def run(self) -> None:
        """
        Asynchronously runs the function in a loop with a specified interval.

        This function continuously runs the provided function `self.fn()` in a loop at a
        specified interval. The interval is determined by the `self.interval` attribute. The
        function `self.fn()` is executed after each sleep interval using the `await` keyword to
        ensure asynchronous execution.

        Returns:
            None
        """
        while True:
            await asyncio.sleep(self.interval)
            await self.fn()

    def cancel(self) -> None:
        """
        Cancels the task if it is not done.

        Returns:
            None
        """
        if self.task is not None and not self.task.done():
            self.task.cancel()
            self.task = None


class AsyncClient(BaseClient):
    """
    asyncio client class for interacting with the LDLM server.
    """

    def _create_channel(
        self,
        address: str,
        creds: Optional[grpc.ChannelCredentials] = None,
    ) -> grpc.Channel:
        """
        Creates a gRPC channel to the specified address with optional credentials. Required by
        BaseClient ABC.

        Args:
            address (str): The address of the gRPC server.
            creds (grpc.ChannelCredentials, optional): The credentials to use for the
                channel. Defaults to None.

        Returns:
            grpc.Channel: The created gRPC channel.
        """
        if creds is not None:
            return grpc.aio.secure_channel(
                address,
                creds,
            )
        return grpc.aio.insecure_channel(address)

    async def _rpc_with_retry(
        self,
        rpc_func: str,
        rpc_message: Union[
            pb.LockRequest,
            pb.TryLockRequest,
            pb.RenewRequest,
            pb.UnlockRequest,
        ],
    ) -> Union[pb.LockResponse, pb.UnlockResponse]:
        """
        Executes an RPC call with retries in case of connection loss.

        Args:
            rpc_func (str): The RPC function to call.
            rpc_message (Union[LockRequest, TryLockRequest, RenewRequest, UnlockRequest]):
                The message to send in the RPC call.

        Returns:
            The response from the RPC call.
        """
        if self._password is not None:
            metadata = (("authorization", self._password),)
        else:
            metadata = None

        num_retries = 0
        rpc_func_callable = getattr(self._stub, rpc_func)
        while True:
            try:
                resp = await rpc_func_callable(rpc_message, metadata=metadata)
                if resp.HasField("error"):  # pragma: no cover
                    raise exceptions.from_rpc_error(resp.error)
                return resp
            except _InactiveRpcError as e:
                if self._retries > -1 and num_retries == self._retries:
                    raise
                num_retries += 1
                self._logger.warning(
                    f"Encountered error {e} while attempting rpc_call. "
                    f"Retrying in {self._retry_delay_seconds} seconds "
                    f"({num_retries} of {self._retries}).")
                await asyncio.sleep(self._retry_delay_seconds)

    async def lock(
        self,
        name: str,
        wait_timeout_seconds: int = 0,
        lock_timeout_seconds: int = 0,
        size: int = 0,
    ) -> AsyncLock:
        """
        Acquires a lock with the given name.

        If the client's `auto_renew_lock` parameter was set to True (the default) or left
        unspecified, the lock will be automatically renewed at an appropriate interval using
        a background asyncio task.

        Args:
            name (str): The name of the lock to acquire.
            wait_timeout_seconds (int, optional): The timeout in seconds to wait for the
                lock to be acquired. Defaults to 0.
            lock_timeout_seconds (int, optional): The timeout in seconds to wait for the
                lock to be acquired. Defaults to 0.
            size (int, optional): The size of the lock. Defaults to 0 which translates to
                unspecified. The server will use a size of 1 in this case.

        Returns:
            AsyncLock: A lock object.

        Examples:
            >>> import asyncio
            >>> from ldlm import AsyncClient
            >>> 
            >>> async def test_lock():
            ...     client = AsyncClient("ldlm-server:3144")
            ...     lock = await client.lock(
            ...             "test_lock",
            ...             wait_timeout_seconds=10,
            ...             lock_timeout_seconds=600,
            ...     )   
            ...     if not lock:
            ...         print("Could not acquire lock within 10 seconds")
            ...     print("Doing work with lock")
            ...     await lock.unlock()
            ...     print("Released lock")
            ... 
            >>> asyncio.run(test_lock())
            Doing work with lock
            Released lock
        """
        rpc_msg: pb.LockRequest = pb.LockRequest(name=name)
        if wait_timeout_seconds:
            rpc_msg.wait_timeout_seconds = wait_timeout_seconds
        if self._lock_timeout_seconds:
            rpc_msg.lock_timeout_seconds = self._lock_timeout_seconds
        elif lock_timeout_seconds:
            rpc_msg.lock_timeout_seconds = lock_timeout_seconds
        if size > 0:
            rpc_msg.size = size

        try:
            self._logger.info(f"Waiting to acquire lock `{name}`")
            r: pb.LockResponse = await self._rpc_with_retry("Lock", rpc_msg)
        except exceptions.LockWaitTimeoutError:
            r = pb.LockResponse(name=name, locked=False)

        self._logger.info(f"Lock response from server: {r}")

        lock: AsyncLock = AsyncLock(self, r)
        if lock.locked and rpc_msg.lock_timeout_seconds and self._auto_renew_locks:
            await self._start_renew(lock, rpc_msg.lock_timeout_seconds)

        return lock

    @asynccontextmanager
    async def lock_context(
        self,
        name: str,
        wait_timeout_seconds: int = 0,
        lock_timeout_seconds: int = 0,
        size: int = 0,
    ) -> AsyncIterator[AsyncLock]:
        """
        A context manager that acquires a lock and unlocks it when the context is exited.

        If the client's `auto_renew_lock` parameter was set to True (the default) or left
        unspecified, the lock will be automatically renewed at an appropriate interval using
        a background asyncio task.

        Args:
            name (str): The name of the lock to acquire.
            wait_timeout_seconds (int, optional): The timeout in seconds to wait for the lock
                to be acquired. Defaults to 0.
            lock_timeout_seconds (int, optional): The timeout in seconds to wait for the lock
                to be acquired. Defaults to 0.
            size (int, optional): The size of the lock. Defaults to 0 which translates to
                unspecified. The server will use a size of 1 in this case.

        Yields:
            AsyncLock: A lock object.

        Raises:
            RuntimeError: If the lock cannot be released after being acquired.

        Examples:
            >>> import asyncio
            >>> from ldlm import AsyncClient
            >>> 
            >>> async def test_lock_context():
            ...     client = AsyncClient("ldlm-server:3144")
            ...     
            ...     async with client.lock_context(
            ...             "my_lock",
            ...             wait_timeout_seconds=10,
            ...             lock_timeout_seconds=600,
            ...     ) as lock:
            ...         if not lock:
            ...             print("Could not acquire lock within 10 seconds")
            ...         print("Doing work with lock")
            ... 
            >>> asyncio.run(test_lock_context())
            Doing work with lock
        """

        lock = await self.lock(
            name,
            wait_timeout_seconds=wait_timeout_seconds,
            lock_timeout_seconds=lock_timeout_seconds,
            size=size,
        )

        try:
            yield lock
        finally:
            if lock.locked:
                await lock.unlock()

    async def try_lock(
        self,
        name: str,
        lock_timeout_seconds: int = 0,
        size: int = 0,
    ) -> AsyncLock:
        """
        Attempts to acquire a lock and immediately returns; whether the lock was acquired or not.
        You must inspect the returned lock's `locked` property or evaluate it as a boolean
        value to determine if it was acquired.
        
        If the client's `auto_renew_lock` parameter was set to True (the default) or left
        unspecified, the lock will be automatically renewed at an appropriate interval using
        a background asyncio task.

        Args:
            name (str): The name of the lock to acquire.
            lock_timeout_seconds (int, optional): The timeout in seconds to wait for the
                lock to be acquired. Defaults to 0.
            size (int, optional): The size of the lock. Defaults to 0 which translates to
                unspecified. The server will use a size of 1 in this case.

        Yields:
            AsyncLock: A lock object.

        Raises:
            RuntimeError: If the lock cannot be released after being acquired.

        Examples:
            >>> async def test_try_lock():
            ...     client = AsyncClient("ldlm-server:3144")
            ...     
            ...     lock = await client.try_lock(
            ...             "my_lock",
            ...             lock_timeout_seconds=600,
            ...     ) 
            ...     if not lock:
            ...             print("Could not acquire lock")
            ...     print("Doing work with lock")
            ...     await lock.unlock()
            ...     print("Released lock")
            ... 
            >>> asyncio.run(test_try_lock())
            Doing work with lock
            Released lock
        """
        rpc_msg: pb.TryLockRequest = pb.TryLockRequest(name=name,)
        if self._lock_timeout_seconds:
            rpc_msg.lock_timeout_seconds = self._lock_timeout_seconds
        elif lock_timeout_seconds:
            rpc_msg.lock_timeout_seconds = lock_timeout_seconds
        if size > 0:
            rpc_msg.size = size

        self._logger.info(f"Attempting to acquire lock `{name}`")
        r: pb.LockResponse = await self._rpc_with_retry("TryLock", rpc_msg)
        self._logger.info(f"Lock response from server: {r}")

        lock: AsyncLock = AsyncLock(self, r)

        if lock.locked and rpc_msg.lock_timeout_seconds and self._auto_renew_locks:
            await self._start_renew(
                lock,
                rpc_msg.lock_timeout_seconds,
            )

        return lock

    @asynccontextmanager
    async def try_lock_context(
        self,
        name: str,
        lock_timeout_seconds: int = 0,
        size: int = 0,
    ) -> AsyncIterator[AsyncLock]:
        """
        A context manager that attempts to acquire a lock with the given name. You must inspect the
        returned lock's `locked` property or evaluate it as a boolean value to determine if it was
        acquired. If locked, the lock will be released when the context is exited.
        
        If the client's `auto_renew_lock` parameter was set to True (the default) or left
        unspecified, the lock will be automatically renewed at an appropriate interval using
        a background asyncio task.

        Args:
            name (str): The name of the lock to acquire.
            lock_timeout_seconds (int, optional): The timeout in seconds to wait for the lock
                to be acquired. Defaults to 0.
            size (int, optional): The size of the lock. Defaults to 0 which translates to
                unspecified. The server will use a size of 1 in this case.

        Yields:
            AsyncLock: A lock object.

        Raises:
            RuntimeError: If the lock cannot be released after being acquired.

        Examples:
            >>> async def test_try_lock_context():
            ...     client = AsyncClient("ldlm-server:3144")
            ...     
            ...     async with client.try_lock_context(
            ...             "my_lock",
            ...             lock_timeout_seconds=600,
            ...     ) as lock:
            ...         if not lock:
            ...             print("Could not acquire lock")
            ...         print("Doing work with lock")
            ... 
            >>> asyncio.run(test_try_lock_context())
            Doing work with lock
        """
        lock = await self.try_lock(
            name,
            lock_timeout_seconds=lock_timeout_seconds,
            size=size,
        )

        try:
            yield lock
        finally:
            if lock.locked:
                await lock.unlock()

    async def unlock(self, name: str, key: str) -> None:
        """
        Unlock the specified lock. It is much more concise to run this method on the
        :py:class:`ldlm.AsyncLock` object returned by this client's lock methods.

        Args:
            name (str): The name of the lock to unlock.
            key (str): The key associated with the lock to unlock.

        Raises:
            RuntimeError: If the lock cannot be unlocked.
        """
        if timer := self._lock_timers.pop(name, None):
            self._logger.debug(f"Canceling lock renew for `{name}`")
            timer.cancel()

        rpc_msg: pb.UnlockRequest = pb.UnlockRequest(
            name=name,
            key=key,
        )

        self._logger.debug(f"Unlocking `{name}`")
        r: pb.UnlockResponse = await self._rpc_with_retry("Unlock", rpc_msg)
        self._logger.debug(f"Unlock response from server: {r}")
        if not r.unlocked:  # pragma: no cover
            raise RuntimeError(f"Failed to unlock `{name}`")

    async def renew(self, name: str, key: str,
                    lock_timeout_seconds: int) -> AsyncLock:
        """
        Renews a lock. It is much more concise to run this method on the :py:class:`ldlm.AsyncLock`
        object returned by this client's lock methods.

        Args:
            name (str): The name of the lock to renew.
            key (str): The key associated with the lock to renew.
            lock_timeout_seconds (int): The timeout in seconds for acquiring the lock.

        Returns:
            AsyncLock: A lock object.
        """
        rpc_msg: pb.RenewRequest = (pb.RenewRequest(
            name=name,
            key=key,
            lock_timeout_seconds=lock_timeout_seconds,
        ))

        resp: pb.LockResponse = await self._rpc_with_retry(
            "Renew",
            rpc_msg,
        )
        return AsyncLock(self, resp)

    async def _start_renew(self, lock: AsyncLock,
                           lock_timeout_seconds: int) -> None:
        """
        Start the renew timer for a lock.

        Args:
            name (str): The name of the lock to renew.
            key (str): The key associated with the lock to renew.
            lock_timeout_seconds (int): The timeout in seconds after which the lock will
                expire

        Raises:
            RuntimeError: If a renew timer already exists for the lock.

        Returns:
            None
        """
        if lock.name in self._lock_timers:  # pragma: no cover
            raise RuntimeError(f"Lock `{lock.name}` already has a renew timer")

        interval = max(lock_timeout_seconds - 30,
                       self.min_renew_interval_seconds)
        self._lock_timers[lock.name] = _RenewTimer(
            lock,
            lock_timeout_seconds,
            interval=interval,
            logger=self._logger,
        )
        await self._lock_timers[lock.name].start()

    async def close(self) -> None:
        """
        Closes the LDLM gRPC channel.

        This method is used to close the LDLM gRPC channel and indicate that the client is no
        longer active. It is typically called when the client is no longer needed or when the
        program is exiting.

        Returns:
            None
        """
        await self._channel.close()
        self._closed = True

    async def aclose(self) -> None:
        """
        Awaits self.close(). For compatibility with contextlib.aclosing().

        Returns:
            None
        """
        await self.close()
