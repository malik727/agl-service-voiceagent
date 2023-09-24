# SPDX-License-Identifier: Apache-2.0
#
# Copyright (c) 2023 Malik Talha
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

import grpc
import time
import threading
from agl_service_voiceagent.generated import voice_agent_pb2
from agl_service_voiceagent.generated import voice_agent_pb2_grpc
from agl_service_voiceagent.utils.audio_recorder import AudioRecorder
from agl_service_voiceagent.utils.wake_word import WakeWordDetector
from agl_service_voiceagent.utils.stt_model import STTModel
from agl_service_voiceagent.utils.config import get_config_value
from agl_service_voiceagent.utils.common import generate_unique_uuid, delete_file
from agl_service_voiceagent.nlu.snips_interface import SnipsInterface
from agl_service_voiceagent.nlu.rasa_interface import RASAInterface


class VoiceAgentServicer(voice_agent_pb2_grpc.VoiceAgentServiceServicer):
    def __init__(self):
        # Get the config values
        self.service_version = get_config_value('SERVICE_VERSION')
        self.wake_word = get_config_value('WAKE_WORD')
        self.base_audio_dir = get_config_value('BASE_AUDIO_DIR')
        self.channels = int(get_config_value('CHANNELS'))
        self.sample_rate = int(get_config_value('SAMPLE_RATE'))
        self.bits_per_sample = int(get_config_value('BITS_PER_SAMPLE'))
        self.stt_model_path = get_config_value('STT_MODEL_PATH')
        self.snips_model_path = get_config_value('SNIPS_MODEL_PATH')
        self.rasa_model_path = get_config_value('RASA_MODEL_PATH')
        self.rasa_server_port = int(get_config_value('RASA_SERVER_PORT'))
        self.base_log_dir = get_config_value('BASE_LOG_DIR')
        self.store_voice_command = bool(int(get_config_value('STORE_VOICE_COMMANDS')))

        # Initialize class methods
        self.stt_model = STTModel(self.stt_model_path, self.sample_rate)
        self.snips_interface = SnipsInterface(self.snips_model_path)
        self.rasa_interface = RASAInterface(self.rasa_server_port, self.rasa_model_path, self.base_log_dir)
        self.rasa_interface.start_server()
        self.rvc_stream_uuids = {}


    def CheckServiceStatus(self, request, context):
        response = voice_agent_pb2.ServiceStatus(
            version=self.service_version,
            status=True
        )
        return response


    def DetectWakeWord(self, request, context):
        wake_word_detector = WakeWordDetector(self.wake_word, self.stt_model, self.channels, self.sample_rate, self.bits_per_sample)
        wake_word_detector.create_pipeline()
        detection_thread = threading.Thread(target=wake_word_detector.start_listening)
        detection_thread.start()
        while True:
            status = wake_word_detector.get_wake_word_status()
            time.sleep(1)
            if not context.is_active():
                wake_word_detector.send_eos()
                break
            yield voice_agent_pb2.WakeWordStatus(status=status)
            if status:
                break

        detection_thread.join()
    
    
    def RecognizeVoiceCommand(self, requests, context):
        stt = ""
        intent = ""
        intent_slots = []

        for request in requests:
            if request.record_mode == voice_agent_pb2.MANUAL:

                if request.action == voice_agent_pb2.START:
                    status = voice_agent_pb2.REC_PROCESSING
                    stream_uuid = generate_unique_uuid(8)
                    recorder = AudioRecorder(self.stt_model, self.base_audio_dir, self.channels, self.sample_rate, self.bits_per_sample)
                    recorder.set_pipeline_mode("manual")
                    audio_file = recorder.create_pipeline()

                    self.rvc_stream_uuids[stream_uuid] = {
                        "recorder": recorder,
                        "audio_file": audio_file
                    }
                    
                    recorder.start_recording()

                elif request.action == voice_agent_pb2.STOP:
                    stream_uuid = request.stream_id
                    status = voice_agent_pb2.REC_SUCCESS

                    recorder = self.rvc_stream_uuids[stream_uuid]["recorder"]
                    audio_file = self.rvc_stream_uuids[stream_uuid]["audio_file"]
                    del self.rvc_stream_uuids[stream_uuid]

                    recorder.stop_recording()
                    recognizer_uuid = self.stt_model.setup_recognizer()
                    stt = self.stt_model.recognize_from_file(recognizer_uuid, audio_file)

                    if stt not in ["FILE_NOT_FOUND", "FILE_FORMAT_INVALID", "VOICE_NOT_RECOGNIZED", ""]:
                        if request.nlu_model == voice_agent_pb2.SNIPS:
                            extracted_intent = self.snips_interface.extract_intent(stt)
                            intent, intent_actions = self.snips_interface.process_intent(extracted_intent)

                            if not intent or intent == "":
                                status = voice_agent_pb2.INTENT_NOT_RECOGNIZED

                            for action, value in intent_actions.items():
                                intent_slots.append(voice_agent_pb2.IntentSlot(name=action, value=value))
                        
                        elif request.nlu_model == voice_agent_pb2.RASA:
                            extracted_intent = self.rasa_interface.extract_intent(stt)
                            intent, intent_actions = self.rasa_interface.process_intent(extracted_intent)

                            if not intent or intent == "":
                                status = voice_agent_pb2.INTENT_NOT_RECOGNIZED

                            for action, value in intent_actions.items():
                                intent_slots.append(voice_agent_pb2.IntentSlot(name=action, value=value))

                    else:
                        stt = ""
                        status = voice_agent_pb2.VOICE_NOT_RECOGNIZED
                    
                    # cleanup the kaldi recognizer
                    self.stt_model.cleanup_recognizer(recognizer_uuid)

                    # delete the audio file
                    if not self.store_voice_command:   
                        delete_file(audio_file)


        # Process the request and generate a RecognizeResult
        response = voice_agent_pb2.RecognizeResult(
            command=stt,
            intent=intent,
            intent_slots=intent_slots,
            stream_id=stream_uuid,
            status=status
        )
        return response
