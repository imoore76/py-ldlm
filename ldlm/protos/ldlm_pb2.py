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

# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: ldlm.proto
# Protobuf Python Version: 5.26.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nldlm.proto\x12\x04ldlm\"7\n\x05\x45rror\x12\x1d\n\x04\x63ode\x18\x01 \x01(\x0e\x32\x0f.ldlm.ErrorCode\x12\x0f\n\x07message\x18\x02 \x01(\t\"\xaf\x01\n\x0bLockRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12!\n\x14wait_timeout_seconds\x18\x03 \x01(\x05H\x00\x88\x01\x01\x12!\n\x14lock_timeout_seconds\x18\x64 \x01(\x05H\x01\x88\x01\x01\x12\x11\n\x04size\x18\x04 \x01(\x05H\x02\x88\x01\x01\x42\x17\n\x15_wait_timeout_secondsB\x17\n\x15_lock_timeout_secondsB\x07\n\x05_size\"v\n\x0eTryLockRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12!\n\x14lock_timeout_seconds\x18\x64 \x01(\x05H\x00\x88\x01\x01\x12\x11\n\x04size\x18\x04 \x01(\x05H\x01\x88\x01\x01\x42\x17\n\x15_lock_timeout_secondsB\x07\n\x05_size\"d\n\x0cLockResponse\x12\x0e\n\x06locked\x18\x01 \x01(\x08\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x0b\n\x03key\x18\x03 \x01(\t\x12\x1f\n\x05\x65rror\x18\x04 \x01(\x0b\x32\x0b.ldlm.ErrorH\x00\x88\x01\x01\x42\x08\n\x06_error\"*\n\rUnlockRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0b\n\x03key\x18\x02 \x01(\t\"[\n\x0eUnlockResponse\x12\x10\n\x08unlocked\x18\x01 \x01(\x08\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x1f\n\x05\x65rror\x18\x03 \x01(\x0b\x32\x0b.ldlm.ErrorH\x00\x88\x01\x01\x42\x08\n\x06_error\"G\n\x0cRenewRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0b\n\x03key\x18\x02 \x01(\t\x12\x1c\n\x14lock_timeout_seconds\x18\x64 \x01(\x05*\xb3\x01\n\tErrorCode\x12\x0b\n\x07Unknown\x10\x00\x12\x14\n\x10LockDoesNotExist\x10\x01\x12\x12\n\x0eInvalidLockKey\x10\x02\x12\x13\n\x0fLockWaitTimeout\x10\x03\x12\r\n\tNotLocked\x10\x04\x12 \n\x1cLockDoesNotExistOrInvalidKey\x10\x05\x12\x14\n\x10LockSizeMismatch\x10\x06\x12\x13\n\x0fInvalidLockSize\x10\x07\x32\xd8\x01\n\x04LDLM\x12/\n\x04Lock\x12\x11.ldlm.LockRequest\x1a\x12.ldlm.LockResponse\"\x00\x12\x35\n\x07TryLock\x12\x14.ldlm.TryLockRequest\x1a\x12.ldlm.LockResponse\"\x00\x12\x35\n\x06Unlock\x12\x13.ldlm.UnlockRequest\x1a\x14.ldlm.UnlockResponse\"\x00\x12\x31\n\x05Renew\x12\x12.ldlm.RenewRequest\x1a\x12.ldlm.LockResponse\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'ldlm_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_ERRORCODE']._serialized_start=688
  _globals['_ERRORCODE']._serialized_end=867
  _globals['_ERROR']._serialized_start=20
  _globals['_ERROR']._serialized_end=75
  _globals['_LOCKREQUEST']._serialized_start=78
  _globals['_LOCKREQUEST']._serialized_end=253
  _globals['_TRYLOCKREQUEST']._serialized_start=255
  _globals['_TRYLOCKREQUEST']._serialized_end=373
  _globals['_LOCKRESPONSE']._serialized_start=375
  _globals['_LOCKRESPONSE']._serialized_end=475
  _globals['_UNLOCKREQUEST']._serialized_start=477
  _globals['_UNLOCKREQUEST']._serialized_end=519
  _globals['_UNLOCKRESPONSE']._serialized_start=521
  _globals['_UNLOCKRESPONSE']._serialized_end=612
  _globals['_RENEWREQUEST']._serialized_start=614
  _globals['_RENEWREQUEST']._serialized_end=685
  _globals['_LDLM']._serialized_start=870
  _globals['_LDLM']._serialized_end=1086
# @@protoc_insertion_point(module_scope)
