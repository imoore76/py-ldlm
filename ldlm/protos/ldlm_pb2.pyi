from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ErrorCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    Unknown: _ClassVar[ErrorCode]
    LockDoesNotExist: _ClassVar[ErrorCode]
    InvalidLockKey: _ClassVar[ErrorCode]
    LockWaitTimeout: _ClassVar[ErrorCode]
    NotLocked: _ClassVar[ErrorCode]
    LockDoesNotExistOrInvalidKey: _ClassVar[ErrorCode]
    LockSizeMismatch: _ClassVar[ErrorCode]
    InvalidLockSize: _ClassVar[ErrorCode]
Unknown: ErrorCode
LockDoesNotExist: ErrorCode
InvalidLockKey: ErrorCode
LockWaitTimeout: ErrorCode
NotLocked: ErrorCode
LockDoesNotExistOrInvalidKey: ErrorCode
LockSizeMismatch: ErrorCode
InvalidLockSize: ErrorCode

class Error(_message.Message):
    __slots__ = ("code", "message")
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    code: ErrorCode
    message: str
    def __init__(self, code: _Optional[_Union[ErrorCode, str]] = ..., message: _Optional[str] = ...) -> None: ...

class LockRequest(_message.Message):
    __slots__ = ("name", "wait_timeout_seconds", "lock_timeout_seconds", "size")
    NAME_FIELD_NUMBER: _ClassVar[int]
    WAIT_TIMEOUT_SECONDS_FIELD_NUMBER: _ClassVar[int]
    LOCK_TIMEOUT_SECONDS_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    name: str
    wait_timeout_seconds: int
    lock_timeout_seconds: int
    size: int
    def __init__(self, name: _Optional[str] = ..., wait_timeout_seconds: _Optional[int] = ..., lock_timeout_seconds: _Optional[int] = ..., size: _Optional[int] = ...) -> None: ...

class TryLockRequest(_message.Message):
    __slots__ = ("name", "lock_timeout_seconds", "size")
    NAME_FIELD_NUMBER: _ClassVar[int]
    LOCK_TIMEOUT_SECONDS_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    name: str
    lock_timeout_seconds: int
    size: int
    def __init__(self, name: _Optional[str] = ..., lock_timeout_seconds: _Optional[int] = ..., size: _Optional[int] = ...) -> None: ...

class LockResponse(_message.Message):
    __slots__ = ("locked", "name", "key", "error")
    LOCKED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    locked: bool
    name: str
    key: str
    error: Error
    def __init__(self, locked: bool = ..., name: _Optional[str] = ..., key: _Optional[str] = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...

class UnlockRequest(_message.Message):
    __slots__ = ("name", "key")
    NAME_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    name: str
    key: str
    def __init__(self, name: _Optional[str] = ..., key: _Optional[str] = ...) -> None: ...

class UnlockResponse(_message.Message):
    __slots__ = ("unlocked", "name", "error")
    UNLOCKED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    unlocked: bool
    name: str
    error: Error
    def __init__(self, unlocked: bool = ..., name: _Optional[str] = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...

class RenewRequest(_message.Message):
    __slots__ = ("name", "key", "lock_timeout_seconds")
    NAME_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    LOCK_TIMEOUT_SECONDS_FIELD_NUMBER: _ClassVar[int]
    name: str
    key: str
    lock_timeout_seconds: int
    def __init__(self, name: _Optional[str] = ..., key: _Optional[str] = ..., lock_timeout_seconds: _Optional[int] = ...) -> None: ...
