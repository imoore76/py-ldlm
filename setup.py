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
"""setup.py for py-ldlm package"""
from setuptools import setup

VERSION = "1.0.0"

setup(
    name="py-ldlm",
    version=VERSION,
    description="Python LDLM client library",
    url="https://github.com/imoore76/py-ldlm/",
    project_urls={
        'Source': 'https://github.com/imoore76/py-ldlm/',
        'Documentation': 'https://github.com/imoore76/py-ldlm/README.md',
    },
    long_description=("Python LDLM client library for interacting with an "
                      "LDLM server - https://github.com/imoore76/go-ldlm"),
    author="Ian Moore",
    packages=["ldlm"],
    install_requires=[
        "grpcio",
        "google-api-python-client",
    ],
    extras_require={
        "test": ["pytest", "pytest-asyncio", "frozendict"],
    },
)
