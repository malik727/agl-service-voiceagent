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

class RecognizeStatusType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    REC_ERROR: _ClassVar[RecognizeStatusType]
    REC_SUCCESS: _ClassVar[RecognizeStatusType]
    REC_PROCESSING: _ClassVar[RecognizeStatusType]
    VOICE_NOT_RECOGNIZED: _ClassVar[RecognizeStatusType]
    INTENT_NOT_RECOGNIZED: _ClassVar[RecognizeStatusType]

class ExecuteStatusType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    EXEC_ERROR: _ClassVar[ExecuteStatusType]
    EXEC_SUCCESS: _ClassVar[ExecuteStatusType]
    KUKSA_CONN_ERROR: _ClassVar[ExecuteStatusType]
    INTENT_NOT_SUPPORTED: _ClassVar[ExecuteStatusType]
    INTENT_SLOTS_INCOMPLETE: _ClassVar[ExecuteStatusType]
START: RecordAction
STOP: RecordAction
SNIPS: NLUModel
RASA: NLUModel
MANUAL: RecordMode
AUTO: RecordMode
REC_ERROR: RecognizeStatusType
REC_SUCCESS: RecognizeStatusType
REC_PROCESSING: RecognizeStatusType
VOICE_NOT_RECOGNIZED: RecognizeStatusType
INTENT_NOT_RECOGNIZED: RecognizeStatusType
EXEC_ERROR: ExecuteStatusType
EXEC_SUCCESS: ExecuteStatusType
KUKSA_CONN_ERROR: ExecuteStatusType
INTENT_NOT_SUPPORTED: ExecuteStatusType
INTENT_SLOTS_INCOMPLETE: ExecuteStatusType

class Empty(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class ServiceStatus(_message.Message):
    __slots__ = ["version", "status", "wake_word"]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    WAKE_WORD_FIELD_NUMBER: _ClassVar[int]
    version: str
    status: bool
    wake_word: str
    def __init__(self, version: _Optional[str] = ..., status: bool = ..., wake_word: _Optional[str] = ...) -> None: ...

class WakeWordStatus(_message.Message):
    __slots__ = ["status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: bool
    def __init__(self, status: bool = ...) -> None: ...

class RecognizeControl(_message.Message):
    __slots__ = ["action", "nlu_model", "record_mode", "stream_id"]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    NLU_MODEL_FIELD_NUMBER: _ClassVar[int]
    RECORD_MODE_FIELD_NUMBER: _ClassVar[int]
    STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    action: RecordAction
    nlu_model: NLUModel
    record_mode: RecordMode
    stream_id: str
    def __init__(self, action: _Optional[_Union[RecordAction, str]] = ..., nlu_model: _Optional[_Union[NLUModel, str]] = ..., record_mode: _Optional[_Union[RecordMode, str]] = ..., stream_id: _Optional[str] = ...) -> None: ...

class IntentSlot(_message.Message):
    __slots__ = ["name", "value"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    name: str
    value: str
    def __init__(self, name: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class RecognizeResult(_message.Message):
    __slots__ = ["command", "intent", "intent_slots", "stream_id", "status"]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    INTENT_FIELD_NUMBER: _ClassVar[int]
    INTENT_SLOTS_FIELD_NUMBER: _ClassVar[int]
    STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    command: str
    intent: str
    intent_slots: _containers.RepeatedCompositeFieldContainer[IntentSlot]
    stream_id: str
    status: RecognizeStatusType
    def __init__(self, command: _Optional[str] = ..., intent: _Optional[str] = ..., intent_slots: _Optional[_Iterable[_Union[IntentSlot, _Mapping]]] = ..., stream_id: _Optional[str] = ..., status: _Optional[_Union[RecognizeStatusType, str]] = ...) -> None: ...

class ExecuteInput(_message.Message):
    __slots__ = ["intent", "intent_slots"]
    INTENT_FIELD_NUMBER: _ClassVar[int]
    INTENT_SLOTS_FIELD_NUMBER: _ClassVar[int]
    intent: str
    intent_slots: _containers.RepeatedCompositeFieldContainer[IntentSlot]
    def __init__(self, intent: _Optional[str] = ..., intent_slots: _Optional[_Iterable[_Union[IntentSlot, _Mapping]]] = ...) -> None: ...

class ExecuteResult(_message.Message):
    __slots__ = ["response", "status"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    response: str
    status: ExecuteStatusType
    def __init__(self, response: _Optional[str] = ..., status: _Optional[_Union[ExecuteStatusType, str]] = ...) -> None: ...
