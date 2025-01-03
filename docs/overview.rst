============
Overview
============

.. |header| raw:: html

    <p>
    <a href="https://badge.fury.io/py/py-ldlm"><img alt="PyPI version" src="https://badge.fury.io/py/py-ldlm.svg" /></a>
    <a href="https://github.com/imoore76/py-ldlm/blob/main/pyproject.toml"><img alt="Python Version from PEP 621 TOML" src="https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fimoore76%2Fpy-ldlm%2Fmain%2Fpyproject.toml" /></a>
    <a href="http://mypy-lang.org/"><img alt="Checked with mypy" src="http://www.mypy-lang.org/static/mypy_badge.svg" /></a>
    <a class="reference external" href="https://coveralls.io/github/imoore76/py-ldlm"><img alt="Coverage Status" src="https://coveralls.io/repos/github/imoore76/py-ldlm/badge.svg" /></a>
    <img alt="GitHub Actions Workflow Status" src="https://img.shields.io/github/actions/workflow/status/imoore76/py-ldlm/run_checks.yaml" />
    <img alt="CodeQL Workflow Status" src="https://github.com/imoore76/py-ldlm/actions/workflows/codeql.yml/badge.svg" />
    </p>

|header|

.. image:: _static/logo_symbol.png
    :align: center
    :alt: LDLM logo
    :width: 100px

.. |inline1| raw:: html

    <p>
    An <a href="http://github.com/imoore76/ldlm" target="_blank">LDLM</a>
    client library providing Python sync and async clients. For LDLM concepts,
    use cases, and general information, see the
    <a href="https://ldlm.readthedocs.io/" target="_blank">LDLM documentation</a>.
    </p>

|inline1|

Installation
=============

.. code:: shell

    $ pip install py-ldlm

Basic Usage
=============

.. code-block:: python
    :caption: Create client

    import ldlm

    client = ldlm.Client("ldlm-server:3144")

.. code-block:: python
    :caption: Lock and unlock

    lock = client.lock("my-task")

    try:
        do_something()
    finally:
        lock.unlock()


.. code-block:: python
    :caption: Context manager

    # context manager example
    with client.lock_context("my-task"):
        do_something()

.. code-block:: python
    :caption: Create async client

    import ldlm

    client = ldlm.AsyncClient("ldlm-server:3144")

.. code-block:: python
    :caption: Async lock and unlock

    lock = await client.lock("my-task")

    try:
        do_something()
    finally:
        await lock.unlock()


.. code-block:: python
    :caption: Async context manager

    # context manager example
    async with client.lock_context("my-task"):
        do_something()


More advanced usage and examples can be found in 

.. |useslink| raw:: html

    <a href="https://ldlm.readthedocs.io/en/stable/uses.html" target="_blank">LDLM Use Cases</a>

* The |useslink| documentation
* The :doc:`API Reference</ldlm>` section

