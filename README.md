# py-ldlm

An LDLM (http://github.com/imoore76/go-ldlm) client library providing Python sync and async clients.

[![PyPI version](https://badge.fury.io/py/py-ldlm.svg)](https://badge.fury.io/py/py-ldlm)
[![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fimoore76%2Fpy-ldlm%2Fmain%2Fpyproject.toml)](https://github.com/imoore76/py-ldlm/blob/main/pyproject.toml)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Coverage Status](https://coveralls.io/repos/github/imoore76/py-ldlm/badge.svg)](https://coveralls.io/github/imoore76/py-ldlm)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/imoore76/py-ldlm/run_checks.yaml)
![CodeQL Workflow Status](https://github.com/imoore76/py-ldlm/actions/workflows/codeql.yml/badge.svg)

## Installation

```
pip install py-ldlm
```

## Usage

### Overview
```python
from ldlm import Client

c = Client("server:3144")

lock = c.lock("my-task")

# Do task

lock.unlock()
```


#### Client Options
| Name | Default | Description |
|:--- | :--- | :--- |
| `address` (required) |  | Address of the LDLM server |
| `password` | `None` | Password to use for LDLM server |
| `retries ` | `-1` | Number or times to retry an RPC call when the LDLM server is down. `-1` for infinite |
| `retry_delay_seconds` | `5` | Number of seconds to wait between retry attempts |
| `auto_renew_locks` | `True` | Automatically renew locks in a background thread (or async task) when a lock timeout is specified for a lock |
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

Depending on your LDLM server configuration, this feature may be disabled and `lock_timeout_seconds` would be used to specify the maximum amount of time a lock can remain locked without being renewed. If you've specified (or left unspecified) `auto_renew_locks=True` when instantiating the LDLM client, it will take care of renewing locks in the background for you. Otherwise, you must periodically call `renew()` yourself &lt; the lock timeout interval.

To `unlock()` or renew a lock, you must use the lock key that was issued from the lock request's response. This is exemplified further in the examples.

#### Lock object
Lock operations return a `Lock` object which contains a `name`, `key`, and `locked` property. The object is a truthy if locked and falsy if unlocked. It can also be used to unlock and renew the held lock.

### Lock

`lock()` acquires a lock in LDLM. It will block until the lock is acquired or until `wait_timeout_seconds` has elapsed (if specified). 

If you have set `wait_timeout_seconds`, the lock returned may not be locked because `wait_timeout_seconds` seconds have elapsed. In this case, be sure to check the `locked` property of the returned lock to determine when the lock was acquired or not. Locks returned without a `wait_timeout_seconds` will always be locked.

Locks also have a `size` (default: 1), which is the maximum number of concurrent locks that can be held. The size of a lock is set by the first client that obtains the lock. If subsequent calls to a acquire this lock (from the same or other clients) specify a different size, a `LockSizeMismatchError` exception will be raised.

#### Examples

Simple lock
```python
lock = c.lock("my-task")

# Do task

lock.unlock()
```

Async lock
```python
lock = await c.lock("my-task")

# Do task

await lock.unlock()
```

Wait timeout
```python
lock = c.lock("my-task", wait_timeout_seconds=30)

if not lock:
    print("Could not obtain lock within the wait timeout")
    return

# Do task

lock.unlock()
```

Async wait timeout
```python
lock = await c.lock("my-task", wait_timeout_seconds=30)

if not lock:
    print("Could not obtain lock within the wait timeout")
    return

# Do task

await lock.unlock()
```

### Lock Context
`lock_context()` behaves exactly like `lock()`, but will will unlock the lock for you when the context is exited.

#### Examples
Simple lock context
```python
with c.lock_context("my-task"):
    # Do task
    pass

```

Async lock context
```python
async with c.lock_context("my-task")
    # Do task
    pass

```

Wait timeout context
```python
with c.lock_context("my-task", wait_timeout_seconds=30) as lock:

    if not lock:
        print("Could not obtain lock within the wait timeout")
        return

    # Do task

```

Async wait timeout context
```python
async with c.lock_context("my-task", wait_timeout_seconds=30) as lock:

    if not lock:
        print("Could not obtain lock within the wait timeout")
        return

    # Do task

```

### Try Lock
`try_lock()` attempts to acquire a lock and immediately returns; whether the lock was acquired or not. You must inspect the returned lock's `locked` property or evaluate it as a boolean value to determine if it was acquired.

#### Examples

Simple try lock
```python
lock = c.try_lock("my-task")

if not lock:
    return

# Do task

lock.unlock()
```

Async lock
```python
lock = await c.try_lock("my-task")

if not lock:
    return

# Do task

await lock.unlock()
```

### Try Lock Context
`try_lock_context()` behaves exactly like `try_lock_context()`, but will will unlock the lock for you (if the lock was acquired) when the context is exited.

#### Examples
Simple try lock context
```python
with c.try_lock_context("my-task") as lock:
    if lock:
        # Do task

```

Async try lock context
```python
async with c.try_lock_context("my-task") as lock:
    if lock:
        # Do task

```

### Unlock
`unlock()` unlocks the specified lock and stops any lock renew job that may be associated with the lock. 

#### Lock object
Simply calling `Lock.unlock()` on a locked Lock object is sufficient to unlock the lock.

Simple unlock
```python
lock = client.lock("my_task")
lock.unlock()
```

Async unlock
```python
await lock = client.lock("my_task")
await lock.unlock()
```

#### LDLM client
`unlock()` on the LDLM client must be passed the lock name and key that was issued when the lock was acquired. Using a different key will result in an error returned from LDLM and an exception raised in the client.

Simple unlock
```python
lock = client.lock("my_task")
client.unlock("my_task", lock.key)
```

Async unlock
```python
await lock = client.lock("my_task")
await client.unlock("my_task", lock.key)
```

### Renew Lock
As explained in [Basic Concepts](#basic-concepts), you may specify a lock timeout using a `lock_timeout_seconds` argument to any of the `*lock*()` methods. When you do this and leave the client option `auto_renew_locks=True`, the client will renew the lock in the background (using a background thread or async task) without you having to do anything. If, for some reason, you want to disable auto renew, you will have to renew the lock before it times out. You must specify `lock_timeout_seconds` when renewing the lock which will be used as the lock timeout beginning from when the lock is renewed.

#### Lock object
Calling `Lock.renew(<lock timeout_second>)` on a locked Lock object is sufficient to renew the lock.

Simple renew lock
```python
lock = client.lock("my_task")
# do work
lock.renew(300)
# do more work
lock.unlock()
```

Async renew lock
```python
await lock = client.lock("my_task")
# do work
await lock.renew(300)
# do more work
await lock.unlock()
```

#### LDLM client
The `renew()` client method takes the following arguments:

* `name` - name of the lock
* `key` - key for the lock
* `lock_timeout_seconds` - the new lock expiration timeout (or the same timeout if you'd like)

Simple renew lock
```python
lock = c.lock("task1-lock", lock_timeout_seconds=300)

# do some work, then

c.renew("task1-lock", lock.key, lock_timeout_seconds=300)

# do some more work, then

c.renew("task1-lock", lock.key, lock_timeout_seconds=300)

# do some more work and finally

c.unlock("task1-lock", lock.key)
```

Async renew lock
```python
await lock = c.lock("task1-lock", lock_timeout_seconds=300)

# do some work, then

await c.renew("task1-lock", lock.key, lock_timeout_seconds=300)

# do some more work, then

await c.renew("task1-lock", lock.key, lock_timeout_seconds=300)

# do some more work and finally

await lock.unlock()
```

## Common Patterns

### Primary / Secondary Failover

Using a lock, it is relatively simple to implement primary / secondary (or secondaries) failover by running something similar to the following in each server application:
```python
# This will block until lock is acquired
lock = client.lock("application-primary")

logger.info("Became primary. Performing work...")

# Do work. Lock will be unlocked if this process dies.

```

### Task Locking

In some queue / worker patterns it may be necessary to lock tasks while they are being performed to avoid duplicate work. This can be done using try lock:

```python                                                       

while True:

    work_item = queue.Get()

    lock = client.try_lock(work_item.name)
    if not lock:
        log.debug(f"Work {work_item.name} already in progress")
        continue

    # do work

    lock.unlock()
```

### Resource Utilization Limiting

In some applications it may be necessary to limit the number of concurrent operations on a resource. This can be implemented using lock size:

```python
# Code in each client to restrict the number of concurrent ElasticSearch operations to 10
with client.lock("ElasticSearchSlot", size=10):

    # Perform ES operation
    pass

```

Remember - the size of a lock is set by the first client that obtains the lock. All subsequent calls to obtain that lock must use the same size parameter.

### Rate limiting

Limit request rate to a service using locks:

```python
# A client-enforced sliding window of 30 requests per minute.
client = Client("lockserver:3144", auto_renew_locks=False)

# This will block until lock is acquired. No need to store reference to lock.
client.lock("RateLimitExpensiveService", size=30, lock_timeout_seconds=60)
results = expensive_service.query("getAll")

# Do not unlock. Lock will expire in 60 seconds, which enforces the rate window.
```

## Exceptions

The following exceptions are defined in the `exceptions` module and may raised by the client:

| Exception | Description |
| :--- | :--- |
| `LDLMError` | An unknown error (or error that doesn't have a specific code) occurred. Inspect `message` |
| `LockDoesNotExistError` | The lock attempted to unlock or renew does not exist |
| `InvalidLockKeyError` | The supplied key was not valid for the lock |
| `NotLockedError` | The lock was not locked when `unlock()` was called. |
| `LockDoesNotExistOrInvalidKeyError` | The lock does not exist or the key is not valid when renewing a lock |
| `LockSizeMismatchError` | The lock Size specified does not match the actual size of the lock |
| `InvalidLockSizeError` | The lock size specified is not > 0 |

All exceptions are subclasses of `LDLMError`.

## License

Apache 2.0; see [`LICENSE`](LICENSE) for details.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for details.

## Disclaimer

This project is not an official Google project. It is not supported by Google and Google specifically disclaims all warranties as to its quality, merchantability, or fitness for a particular purpose.

