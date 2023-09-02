from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RecordAction(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    START: _ClassVar[RecordAction]
    STOP: _ClassVar[RecordAction]

class NLUModel(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    SNIPS: _ClassVar[NLUModel]
    RASA: _ClassVar[NLUModel]

class RecordMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    MANUAL: _ClassVar[RecordMode]
    AUTO: _ClassVar[RecordMode]
START: RecordAction
STOP: RecordAction
SNIPS: NLUModel
RASA: NLUModel
MANUAL: RecordMode
AUTO: RecordMode

class Empty(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class WakeWordStatus(_message.Message):
    __slots__ = ["status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: bool
    def __init__(self, status: bool = ...) -> None: ...

class RecognizeControl(_message.Message):
    __slots__ = ["action", "nlu_model", "record_mode"]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    NLU_MODEL_FIELD_NUMBER: _ClassVar[int]
    RECORD_MODE_FIELD_NUMBER: _ClassVar[int]
    action: RecordAction
    nlu_model: NLUModel
    record_mode: RecordMode
    def __init__(self, action: _Optional[_Union[RecordAction, str]] = ..., nlu_model: _Optional[_Union[NLUModel, str]] = ..., record_mode: _Optional[_Union[RecordMode, str]] = ...) -> None: ...

class IntentSlot(_message.Message):
    __slots__ = ["name", "value"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    name: str
    value: str
    def __init__(self, name: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class RecognizeResult(_message.Message):
    __slots__ = ["command", "intent", "intent_slots"]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    INTENT_FIELD_NUMBER: _ClassVar[int]
    INTENT_SLOTS_FIELD_NUMBER: _ClassVar[int]
    command: str
    intent: str
    intent_slots: _containers.RepeatedCompositeFieldContainer[IntentSlot]
    def __init__(self, command: _Optional[str] = ..., intent: _Optional[str] = ..., intent_slots: _Optional[_Iterable[_Union[IntentSlot, _Mapping]]] = ...) -> None: ...
