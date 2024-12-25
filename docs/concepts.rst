=========
Concepts
=========

LDLM is a light-weight distributed lock manager with many use cases.

Locks
========
Locks in an LDLM server generally live until the client unlocks the lock or disconnects. If a client dies while holding a lock, the disconnection is detected and handled in LDLM by releasing the lock. This effectively eliminates deadlocks.

Name
------
A lock is uniquely identified by its name. This is specified when the lock is requested.

.. code-block:: python

    import ldlm

    client = ldlm.Client("ldlm-server:3144")

    lock = client.lock("my-task")


Size
------
Locks can have a size (defaults to: 1). This allows for a finite (but greater than 1)
number of lock acquisitions to be held on the same lock.

.. code-block:: python

    import ldlm

    # Number of expensive operation slots
    ES_SLOTS = 20

    client = ldlm.Client("ldlm-server:3144")

    lock = client.lock("expensive_operation", size=ES_SLOTS)

    # Do operation

Timeout
------------
.. note::
    
    Most users will **not** need to set a timeout for the purpose of mitigating
    deadlocks because client disconnects trigger a release of all locks held by the client.

Locks can have a timeout (defaults to: None). This specifies the maximum amount of
time a lock can remain locked without being renewed. If the lock is not renewed in time,
it is released. See also `Renewing a lock`_.

.. code-block:: python

    import ldlm

    client = ldlm.Client("ldlm-server:3144")

    lock = client.lock("my-task", lock_timeout_seconds=300)

Acquiring a Lock
========================

Locks are generally acquired using ``lock()`` or ``try_lock()``. ``lock()`` will block until
the lock is acquired or until ``wait_timeout_seconds`` has elapsed (if specified). ``try_lock()``
will return immediately whether the lock was acquired or not; the return value is inspected to
determine lock acquisition in this case.

Both methods have corresponding context managers as well; ``lock_context()`` and ``try_lock_context()``.

In all cases, a ``Lock`` object is returned. The object is a truthy if locked and falsy if
unlocked. It can also be used to unlock and renew the held lock as you will read about below.

Examples
---------------
.. code-block:: python
    :caption:   Simple lock

    # Block until lock is obtained
    lock = client.lock("my-task")

    # Do work, then release lock
    lock.unlock()


.. code-block:: python
    :caption: Wait timeout

    # Wait at most 30 seconds to acquire lock
    lock = client.lock("my-task", wait_timeout_seconds=30)
    if not lock:
        print("Could not obtain lock within 30 seconds.")
        return
    # Do work, then release lock
    lock.unlock()

.. code-block:: python
    :caption: Try lock

    # This is non-blocking
    lock = client.try_lock("my-task")
    if not lock:
        print("Lock already acquired.")
        return
    # Do work, then release lock
    lock.unlock()

.. code-block:: python
    :caption: lock context

    with client.lock_context("my-task"):
        # Do work. Lock will be released when context is exited
        pass

.. code-block:: python
    :caption: lock context with wait timeout

    with client.lock_context("my-task", wait_timeout_seconds=30) as lock:
        if lock: # Check if lock was obtained
            pass # Do work. Lock will be released when context is exited


.. code-block:: python
    :caption: try_lock context

    with client.try_lock_context("my-task") as lock:
        if lock: # Check if lock was obtained
            pass # Do work. Lock will be released when context is exited

Releasing a lock
========================
The ``unlock()`` method is used to release a held lock.

.. code-block:: python

    import ldlm

    client = ldlm.Client("ldlm-server:3144")

    lock = client.lock("my-task")

    # Do task

    lock.unlock()

Renewing a lock
================

.. note::
    
    Most users will not need to worry about lock renewal.

In rare cases where client connections are unreliable or disconnect often, one
could use a lock timeout on all locks
and disable the "lock release on client disconnect" feature  in the LDLM server.
By default, the client will
renew the lock in the background using a thread or async task if you specify a lock
timeout on a lock.

If you want to disable the auto renewal, you will have to manually renew the lock before it times
out. The ``renew()`` method is used to renew a held lock that will expire after the specified
``lock_timeout_seconds``. You must also specify ``lock_timeout_seconds`` when renewing the lock
which will be used as new the lock timeout from the time of renewal.

.. code-block:: python

    import ldlm

    client = ldlm.Client("ldlm-server:3144")

    lock = client.lock("my-task", lock_timeout_seconds=300)

    # Do some work

    lock.renew(300)

    # Do more work

    lock.unlock()

