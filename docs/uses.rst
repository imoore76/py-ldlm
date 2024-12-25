
===============
Use Cases
===============

Below are some common use cases and examples.

Failover
===============================

Implement primary / secondary (or secondaries)
failover by running something similar to the following in each server application:

.. code-block:: python

    import ldlm

    client = ldlm.Client("ldlm-server:3144")

    # This will block until lock is acquired
    lock = client.lock("application-primary")

    logger.info("Became primary. Performing work...")

    # Lock will be unlocked when this process ends.

Task Locking
===============================

In some queue / worker patterns it may be necessary to lock tasks while they are
being performed to avoid duplicate work. This can be done using try lock:

.. code-block:: python

    import ldlm

    client = ldlm.Client("ldlm-server:3144")

    while True:

        work_item = queue.Get()

        lock = client.try_lock(work_item.name)
        if not lock:
            log.debug(f"Work {work_item.name} already in progress")
            continue

        # do work

        lock.unlock()

Resource Utilization Limiting
===============================

In some applications it may be necessary to limit the number of concurrent operations on a
resource. Assuming distributed clients sharing the same codebase, (e.g. deployed kubernetes pods)
this can be implemented using lock size.

.. code-block:: python

    import ldlm

    # Code in each client to restrict the number of concurrent ElasticSearch operations to 10
    client = ldlm.Client("ldlm-server:3144")

    # Block until a slot becomes available. It will be released when the context-manager exits
    with client.lock_context("ElasticSearchSlot", size=10):

        # Perform ES operation
        pass


Client-side Rate Limiting
===============================

Limit request rate to a service using locks. Like the task locking example, this assumes
distributed clients sharing the same codebase, (e.g. deployed kubernetes pods).

.. code-block:: python

    import ldlm

    # Allow 30 requests every 60 seconds
    RATE_LIMIT_SIZE = 30
    RATE_LIMIT_SECONDS = 60

    # A client-enforced sliding window of 30 requests per minute.
    client = ldlm.Client("ldlm-server:3144", auto_renew_locks=False)

    # This will block until lock is acquired.
    client.lock(
        "RateLimitExpensiveService",
        size=RATE_LIMIT_SIZE,
        lock_timeout_seconds=RATE_LIMIT_SECONDS
    )

    results = expensive_service.query("getAll")
    
    # Do not unlock. Lock will expire in 60 seconds, which enforces the rate window.

Server-side Rate Limiting
===============================

Limit request rate to a service using locks:

.. code-block:: python

    import ldlm

    # Allow 30 requests every 60 seconds
    RATE_LIMIT_SIZE = 30
    RATE_LIMIT_SECONDS = 60

    client = ldlm.Client("ldlm-server:3144", auto_renew_locks=False)

    def generate_image(request):
        """Request handler for expensive AI image generation"""

        lock = client.try_lock(
            "generate_image",
            size=RATE_LIMIT_SIZE,
            lock_timeout_seconds=RATE_LIMIT_SECONDS
        )

        if not lock:
            return HttpResponse("Too Many Requests", status=429)

        # Generate image.
        for chunk in ai_image_generator(request)
            yield chunk

        # Do not unlock. Lock will expire in 60 seconds, which enforces the rate window.