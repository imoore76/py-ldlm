# py-ldlm

An LDLM (http://github.com/imoore76/go-ldlm) client library providing Python sync and async clients.

## Installation

```
pip3 install py-ldlm
```

## Usage

### Create a Client
```python
from ldlm import Client

c = Client("server:3144")
```

or an asyncio client

```python
from ldlm import AsyncClient

c = AsyncClient("server:3144")
```


#### Client Options
| Name | Default | Description |
|:--- | :--- | :--- |
| `password` | `None` | Password to use for LDLM server |
| `retries ` | `-1` | Number or times to retry an RPC call when the LDLM server is down. `-1` for infinite |
| `retry_delay_seconds` | `5` | Number of seconds to wait between retry attempts |
| `auto_refresh_locks` | `True` | Automatically refresh locks in a background thread (or async task) when a lock timeout is specified for a lock |
| `tls` | `None` | An `ldlm.TLSConfig` instance or `None` to disable TLS |


#### TLSConfig

`ldlm.TLSConfig` options. All default to `None`.
| Name | Description |
| :--- | :--- |
| `ca_file` | Path to the CA certificate file to use. |
| `cert_file` | Path to the client certificate file to use when LDLM is configured for two-way TLS |
| `key_file` | Path to the file containing the key for the `cert_file` |

If you do not need to specify any of these, but your LDLM server is configured to use TLS, use an empty `TLSConfig()` object.

### Basic Concepts

Locks in an LDLM server generally live until the client unlocks the lock or disconnects. If a client dies while holding a lock, the disconnection is detected and handled in LDLM by releasing the lock.

Depending on your LDLM server configuration, this feature may be disabled and `lock_timeout_seconds` would be used to specify the maximum amount of time a lock can remain locked without being refreshed. If you've specified (or left unspecified) `auto_refresh_locks=True` when instantiating the LDLM client, it will take care of refreshing locks in the background for you. Otherwise, you must periodically call `c.refresh_lock()` yourself &lt; the lock timeout interval.

To `unlock()` or refresh a lock, you must use the lock key that was issued from the lock request's response. This is exemplified further in the examples.

### Lock

`lock()` attempts to acquire a lock in LDLM. It will block until the lock is acquired or until `wait_timeout_seconds` has elapsed (if specified). 

If you have set `wait_timeout_seconds`, the lock returned may not be locked because `wait_timeout_seconds` seconds have elapsed. In this case, be sure to check the `locked` property of the returned lock to determine when the lock was acquired or not. Locks returned without a `wait_timeout_seconds` will always be locked.

Locks also have a `size` (default: 1), which is the maximum number of concurrent locks that can be held. The size of a lock is set by the first client that obtains the lock. If subsequent calls to a acquire this lock (from the same or other clients) specify a different size, a `LockSizeMismatchError` exception will be raised.

#### Examples

Simple lock
```python
lock = c.lock("my-task")

# Do task

c.unlock("my-task", key=lock.key)
```

Async lock
```python
lock = await c.lock("my-task")

# Do task

await c.unlock("my-task", lock.key)
```

Wait timeout
```python
lock = c.lock("my-task", wait_timeout_seconds=30)

if not lock.locked:
    print("Could not obtain lock within the wait timeout")
    return

# Do task

c.unlock("my-task", lock.key)
```

Async wait timeout
```python
lock = await c.lock("my-task", wait_timeout_seconds=30)

if not lock.locked:
    print("Could not obtain lock within the wait timeout")
    return

# Do task

await c.unlock("my-task", lock.key)
```

### Lock Context
`lock_context()` behaves exactly like `lock()`, but will will unlock the lock for you when the context is exited.

#### Examples
Simple lock context
```python
with c.lock_context("my-task"):
    # Do task

```

Async lock context
```python
async with c.lock_context("my-task")
    # Do task

```

Wait timeout context
```python
with c.lock_context("my-task", wait_timeout_seconds=30) as lock

    if not lock.locked:
        print("Could not obtain lock within the wait timeout")
        return

    # Do task

```

Async wait timeout context
```python
async with c.lock_context("my-task", wait_timeout_seconds=30) as lock:

    if not lock.locked:
        print("Could not obtain lock within the wait timeout")
        return

    # Do task

```

### Try Lock
`try_lock()` attempts to acquire a lock and immediately returns; whether the lock was acquired or not. You must inspect the returned lock's `locked` property to determine if it was acquired.

#### Examples

Simple try lock
```python
lock = c.try_lock("my-task")

if not lock.locked:
    return

# Do task

c.unlock("my-task", key=lock.key)
```

Async lock
```python
lock = await c.try_lock("my-task")

if not lock.locked:
    return

# Do task

await c.unlock("my-task", lock.key)
```

### Try Lock Context
`try_lock_context()` behaves exactly like `try_lock_context()`, but will will unlock the lock for you (if the lock was acquired) when the context is exited.

#### Examples
Simple try lock context
```python
with c.try_lock_context("my-task") as lock:
    if lock.locked:
        # Do task

```

Async try lock context
```python
async with c.try_lock_context("my-task") as lock:
    if lock.locked:
        # Do task

```

### Unlock
`unlock()` unlocks the specified lock and stops any lock refresh job that may be associated with the lock. It must be passed the key that was issued when the lock was acquired. Using a different key will result in an error returned from LDLM and an exception raised in the client.


#### Examples
Simple unlock
```python
unlock("my_task", lock.key)
```

Async unlock
```python
await unlock("my_task", lock.key)
```

### Refresh Lock
As explained in [Basic Concepts](#basic-concepts), you may specify a lock timeout using a `lock_timeout_seconds` argument to any of the `*lock*()` methods. When you do this and leave the client option `auto_refresh_locks=True`, the client will refresh the lock in the background (using a background thread or async task) without you having to do anything. If, for some reason, you want to disable auto refresh, you will have to refresh the lock before it times out using the `refresh_lock()` method. It takes the following arguments

* `name` - name of the lock
* `key` - key for the lock
* `lock_timeout_seconds` - the new lock expiration timeout (or the same timeout if you'd like)

#### Examples
```python
lock = c.lock("task1-lock", lock_timeout_seconds=300)

# do some work, then

c.refresh_lock("task1-lock", l.key, lock_timeout_seconds=300)

# do some more work, then

c.refresh_lock("task1-lock", l.key, lock_timeout_seconds=300)

# do some more work and finally

c.unlock("task1-lock", l.key)
```

## Common Patterns

### Primary / Secondary Failover

Using a lock, it is relatively simple to implement primary / secondary (or secondaries) failover by running something similar to the following in each server application:
```python
lock = client.lock("application-primary")

if not lock.locked:
    # This should not happen
    raise RuntimeException("error: lock returned but not locked")

logger.info("Became primary. Performing work...")

# Do work. Lock will be unlocked if this process dies.

```

### Task Locking

In some queue / worker patterns it may be necessary to lock tasks while they are being performed to avoid duplicate work. This can be done using try lock:

```python                                                       

while True:

    work_item = queue.Get()

    lock = client.try_lock(work_item.name)
    if not lock.locked:
        log.debug(f"Work {work_item.name} already in progress");
        continue

    # do work

    client.unlock(lock.name, lock.key)
```

### Resource Utilization Limiting

In some applications it may be necessary to limit the number of concurrent operations on a resource. This can be implemented using lock size:

```python
# Code in each client to restrict the number of concurrent ElasticSearch operations to 10
lock = client1.lock("ElasticSearchSlot", size=10)

if not lock.locked:
    raise RuntimeException("error: lock returned but not locked")

# Perform ES operation

client1.unlock(lock.name, lock.key)
```

Remember - the size of a lock is set by the first client that obtains the lock. All subsequent calls to obtain that lock must use the same size parameter.

## Exceptions

The following exceptions are defined in the `exceptions` module and may raised by the client:

| Exception | Description |
| :--- | :--- |
| `LDLMError` | An unknown error (or error that doesn't have a specific code) occurred. Inspect `message` |
| `LockDoesNotExistError` | The lock attempted to unlock or refresh does not exist |
| `InvalidLockKeyError` | The supplied key was not valid for the lock |
| `NotLockedError` | The lock was not locked when `unlock()` was called. |
| `LockDoesNotExistOrInvalidKeyError` | The lock does not exist or the key is not valid when refreshing a lock |
| `LockSizeMismatchError` | The lock Size specified does not match the actual size of the lock |
| `InvalidLockSizeError` | The lock size specified is not > 0 |

All exceptions are subclasses of `LDLMError`.

## License

Apache 2.0; see [`LICENSE`](LICENSE) for details.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for details.

## Disclaimer

This project is not an official Google project. It is not supported by Google and Google specifically disclaims all warranties as to its quality, merchantability, or fitness for a particular purpose.

