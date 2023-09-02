# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: voice_agent.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x11voice_agent.proto\"\x07\n\x05\x45mpty\" \n\x0eWakeWordStatus\x12\x0e\n\x06status\x18\x01 \x01(\x08\"q\n\x10RecognizeControl\x12\x1d\n\x06\x61\x63tion\x18\x01 \x01(\x0e\x32\r.RecordAction\x12\x1c\n\tnlu_model\x18\x02 \x01(\x0e\x32\t.NLUModel\x12 \n\x0brecord_mode\x18\x03 \x01(\x0e\x32\x0b.RecordMode\")\n\nIntentSlot\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t\"U\n\x0fRecognizeResult\x12\x0f\n\x07\x63ommand\x18\x01 \x01(\t\x12\x0e\n\x06intent\x18\x02 \x01(\t\x12!\n\x0cintent_slots\x18\x03 \x03(\x0b\x32\x0b.IntentSlot*#\n\x0cRecordAction\x12\t\n\x05START\x10\x00\x12\x08\n\x04STOP\x10\x01*\x1f\n\x08NLUModel\x12\t\n\x05SNIPS\x10\x00\x12\x08\n\x04RASA\x10\x01*\"\n\nRecordMode\x12\n\n\x06MANUAL\x10\x00\x12\x08\n\x04\x41UTO\x10\x01\x32~\n\x11VoiceAgentService\x12+\n\x0e\x44\x65tectWakeWord\x12\x06.Empty\x1a\x0f.WakeWordStatus0\x01\x12<\n\x15RecognizeVoiceCommand\x12\x11.RecognizeControl\x1a\x10.RecognizeResultb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'voice_agent_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _globals['_RECORDACTION']._serialized_start=309
  _globals['_RECORDACTION']._serialized_end=344
  _globals['_NLUMODEL']._serialized_start=346
  _globals['_NLUMODEL']._serialized_end=377
  _globals['_RECORDMODE']._serialized_start=379
  _globals['_RECORDMODE']._serialized_end=413
  _globals['_EMPTY']._serialized_start=21
  _globals['_EMPTY']._serialized_end=28
  _globals['_WAKEWORDSTATUS']._serialized_start=30
  _globals['_WAKEWORDSTATUS']._serialized_end=62
  _globals['_RECOGNIZECONTROL']._serialized_start=64
  _globals['_RECOGNIZECONTROL']._serialized_end=177
  _globals['_INTENTSLOT']._serialized_start=179
  _globals['_INTENTSLOT']._serialized_end=220
  _globals['_RECOGNIZERESULT']._serialized_start=222
  _globals['_RECOGNIZERESULT']._serialized_end=307
  _globals['_VOICEAGENTSERVICE']._serialized_start=415
  _globals['_VOICEAGENTSERVICE']._serialized_end=541
# @@protoc_insertion_point(module_scope)