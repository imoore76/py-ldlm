# Overview

[![PyPI version](https://badge.fury.io/py/py-ldlm.svg)](https://badge.fury.io/py/py-ldlm)
[![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fimoore76%2Fpy-ldlm%2Fmain%2Fpyproject.toml)](https://github.com/imoore76/py-ldlm/blob/main/pyproject.toml)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Coverage Status](https://coveralls.io/repos/github/imoore76/py-ldlm/badge.svg)](https://coveralls.io/github/imoore76/py-ldlm)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/imoore76/py-ldlm/run_checks.yaml)
![CodeQL Workflow Status](https://github.com/imoore76/py-ldlm/actions/workflows/codeql.yml/badge.svg)

<p align="center">
<img src="./_static/logo_symbol.png" width=100 alt="LDLM logo"/>
</p>

An <a href="http://github.com/imoore76/ldlm" target="_blank">LDLM</a> client library providing Python sync and async clients. For LDLM concepts, use cases, and general information, see the <a href="https://ldlm.readthedocs.io/" target="_blank">LDLM documentation</a>.

## Installation

```
pip install py-ldlm
```

## Basic Usage

```python

import ldlm

client = ldlm.Client("ldlm-server:3144")

lock = client.lock("my-task")

do_something()

lock.unlock()

```

More advanced usage and examples can be found in the <a href='ldlm.html'>API Reference section</a>.

