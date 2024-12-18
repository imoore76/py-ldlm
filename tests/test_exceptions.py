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
import pytest

from ldlm import exceptions
from ldlm.protos import ldlm_pb2 as pb2


@pytest.mark.parametrize("code,exception_cls", [
    (0, exceptions.LDLMError),
    (1, exceptions.LockDoesNotExistError),
    (2, exceptions.InvalidLockKeyError),
    (3, exceptions.LockWaitTimeoutError),
    (4, exceptions.NotLockedError),
    (5, exceptions.LockDoesNotExistOrInvalidKeyError),
    (6, exceptions.LockSizeMismatchError),
    (7, exceptions.InvalidLockSizeError),
])
def test_exceptions(code, exception_cls):
    ex = exceptions.from_rpc_error(pb2.Error(code=code))
    assert isinstance(ex, exception_cls)
    assert ex.RPC_CODE == code


def test_unknown_exception():
    ex = exceptions.from_rpc_error(pb2.Error(code=22))
    assert isinstance(ex, exceptions.LDLMError)
    assert ex.RPC_CODE == 0
